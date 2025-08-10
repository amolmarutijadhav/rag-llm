#!/usr/bin/env python3
"""
Parallel vs Sequential Processing Performance Test

This script compares the performance of parallel vs sequential processing
in the enhanced chat completion service.
"""

import asyncio
import time
import json
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from app.domain.models.requests import ChatCompletionRequest, ChatMessage
from app.domain.services.enhanced_chat_completion_service import EnhancedChatCompletionService
from app.domain.services.rag_service import RAGService
from app.infrastructure.providers.service_locator import ServiceLocator
from app.core.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class ProcessingMetrics:
    """Metrics for processing performance"""
    mode: str
    total_time: float
    embedding_calls: int
    vector_search_calls: int
    queries_generated: int
    results_retrieved: int
    avg_embedding_time: float
    avg_vector_search_time: float

class ParallelVsSequentialTest:
    """Compare parallel vs sequential processing performance"""
    
    def __init__(self):
        self.service_locator = ServiceLocator()
        self.service_locator.initialize_providers()
        
        # Get providers
        self.embedding_provider = self.service_locator.get_embedding_provider()
        self.llm_provider = self.service_locator.get_llm_provider()
        self.vector_store_provider = self.service_locator.get_vector_store_provider()
        
        # Create RAG service
        self.rag_service = RAGService(self.embedding_provider, self.llm_provider, self.vector_store_provider)
        self.enhanced_service = EnhancedChatCompletionService(self.rag_service, self.llm_provider)
        
        # Performance tracking
        self.embedding_times = []
        self.vector_search_times = []
        self.embedding_call_count = 0
        self.vector_search_call_count = 0
        
        # Setup tracking
        self._setup_tracking()
    
    def _setup_tracking(self):
        """Setup performance tracking"""
        original_get_embeddings = self.rag_service.embedding_provider.get_embeddings
        original_search_vectors = self.rag_service.vector_store_provider.search_vectors
        
        async def tracked_get_embeddings(queries):
            start_time = time.time()
            self.embedding_call_count += 1
            result = await original_get_embeddings(queries)
            end_time = time.time()
            self.embedding_times.append(end_time - start_time)
            return result
        
        async def tracked_search_vectors(vector, top_k, collection):
            start_time = time.time()
            self.vector_search_call_count += 1
            result = await original_search_vectors(vector, top_k, collection)
            end_time = time.time()
            self.vector_search_times.append(end_time - start_time)
            return result
        
        self.rag_service.embedding_provider.get_embeddings = tracked_get_embeddings
        self.rag_service.vector_store_provider.search_vectors = tracked_search_vectors
    
    def _reset_metrics(self):
        """Reset performance metrics"""
        self.embedding_times = []
        self.vector_search_times = []
        self.embedding_call_count = 0
        self.vector_search_call_count = 0
    
    def _create_test_request(self) -> ChatCompletionRequest:
        """Create a test request that should generate multiple queries"""
        return ChatCompletionRequest(
            model="gpt-4",
            messages=[
                ChatMessage(role="system", content="You are a Credit Officer specializing in regulatory compliance."),
                ChatMessage(role="user", content="I need to prepare a BRD for Basel III compliance"),
                ChatMessage(role="assistant", content="I'll help you create a comprehensive BRD. Let me gather relevant information about Basel III requirements."),
                ChatMessage(role="user", content="What sections should I include?"),
                ChatMessage(role="assistant", content="Based on Basel III compliance requirements, your BRD should include: Executive Summary, Risk Assessment, Implementation Plan, and Compliance Framework."),
                ChatMessage(role="user", content="Can you help me draft the executive summary with specific capital requirements for SME exposures?")
            ],
            temperature=0.7,
            max_tokens=1000
        )
    
    async def test_processing_mode(self, enable_parallel: bool, mode_name: str) -> ProcessingMetrics:
        """Test a specific processing mode"""
        self._reset_metrics()
        
        # Temporarily modify the configuration
        from app.core.enhanced_chat_config import PERFORMANCE_CONFIG
        original_config = PERFORMANCE_CONFIG.copy()
        
        try:
            # Set the processing mode
            PERFORMANCE_CONFIG["enable_parallel_processing"] = enable_parallel
            PERFORMANCE_CONFIG["max_concurrent_queries"] = 4 if enable_parallel else 1
            
            # Create test request
            request = self._create_test_request()
            
            # Run the test
            start_time = time.time()
            response = await self.enhanced_service.process_request(request)
            end_time = time.time()
            
            total_time = end_time - start_time
            
            # Calculate averages
            avg_embedding_time = sum(self.embedding_times) / len(self.embedding_times) if self.embedding_times else 0
            avg_vector_search_time = sum(self.vector_search_times) / len(self.vector_search_times) if self.vector_search_times else 0
            
            # Get metadata
            metadata = response.metadata or {}
            queries_generated = metadata.get("enhanced_queries_count", 0)
            results_retrieved = len(metadata.get("rag_results", []))
            
            return ProcessingMetrics(
                mode=mode_name,
                total_time=total_time,
                embedding_calls=self.embedding_call_count,
                vector_search_calls=self.vector_search_call_count,
                queries_generated=queries_generated,
                results_retrieved=results_retrieved,
                avg_embedding_time=avg_embedding_time,
                avg_vector_search_time=avg_vector_search_time
            )
            
        finally:
            # Restore original configuration
            PERFORMANCE_CONFIG.update(original_config)
    
    async def run_comparison(self, num_runs: int = 5) -> Dict[str, Any]:
        """Run the parallel vs sequential comparison"""
        print(f"🔄 Running parallel vs sequential comparison with {num_runs} runs per mode...")
        
        parallel_results = []
        sequential_results = []
        
        for i in range(num_runs):
            print(f"  Run {i+1}/{num_runs}...")
            
            # Test parallel processing
            parallel_metrics = await self.test_processing_mode(True, "parallel")
            parallel_results.append(parallel_metrics)
            
            # Test sequential processing
            sequential_metrics = await self.test_processing_mode(False, "sequential")
            sequential_results.append(sequential_metrics)
            
            # Small delay between runs
            await asyncio.sleep(1)
        
        return {
            "parallel": parallel_results,
            "sequential": sequential_results,
            "timestamp": datetime.now().isoformat(),
            "num_runs": num_runs
        }
    
    def analyze_comparison(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze comparison results"""
        parallel_results = results["parallel"]
        sequential_results = results["sequential"]
        
        # Calculate averages for parallel
        parallel_times = [r.total_time for r in parallel_results]
        parallel_embedding_calls = [r.embedding_calls for r in parallel_results]
        parallel_vector_calls = [r.vector_search_calls for r in parallel_results]
        parallel_queries = [r.queries_generated for r in parallel_results]
        
        # Calculate averages for sequential
        sequential_times = [r.total_time for r in sequential_results]
        sequential_embedding_calls = [r.embedding_calls for r in sequential_results]
        sequential_vector_calls = [r.vector_search_calls for r in sequential_results]
        sequential_queries = [r.queries_generated for r in sequential_results]
        
        analysis = {
            "parallel": {
                "avg_total_time": sum(parallel_times) / len(parallel_times),
                "avg_embedding_calls": sum(parallel_embedding_calls) / len(parallel_embedding_calls),
                "avg_vector_calls": sum(parallel_vector_calls) / len(parallel_vector_calls),
                "avg_queries": sum(parallel_queries) / len(parallel_queries),
                "min_time": min(parallel_times),
                "max_time": max(parallel_times)
            },
            "sequential": {
                "avg_total_time": sum(sequential_times) / len(sequential_times),
                "avg_embedding_calls": sum(sequential_embedding_calls) / len(sequential_embedding_calls),
                "avg_vector_calls": sum(sequential_vector_calls) / len(sequential_vector_calls),
                "avg_queries": sum(sequential_queries) / len(sequential_queries),
                "min_time": min(sequential_times),
                "max_time": max(sequential_times)
            },
            "comparison": {
                "time_improvement": ((sum(sequential_times) / len(sequential_times)) / (sum(parallel_times) / len(parallel_times)) - 1) * 100,
                "speedup_factor": (sum(sequential_times) / len(sequential_times)) / (sum(parallel_times) / len(parallel_times)),
                "api_calls_same": sum(parallel_embedding_calls) == sum(sequential_embedding_calls)
            }
        }
        
        return analysis
    
    def print_comparison(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Print comparison results"""
        print("\n" + "="*100)
        print("PARALLEL vs SEQUENTIAL PROCESSING PERFORMANCE COMPARISON")
        print("="*100)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Runs per mode: {results['num_runs']}")
        print()
        
        # Detailed results table
        print("DETAILED RESULTS:")
        print("-" * 100)
        print(f"{'Run':<4} {'Mode':<12} {'Time(s)':<8} {'Embed':<6} {'Search':<6} {'Queries':<8} {'Results':<8}")
        print("-" * 100)
        
        for i in range(results['num_runs']):
            parallel = results['parallel'][i]
            sequential = results['sequential'][i]
            
            print(f"{i+1:<4} {'Parallel':<12} {parallel.total_time:<8.3f} {parallel.embedding_calls:<6} "
                  f"{parallel.vector_search_calls:<6} {parallel.queries_generated:<8} {parallel.results_retrieved:<8}")
            print(f"{'':<4} {'Sequential':<12} {sequential.total_time:<8.3f} {sequential.embedding_calls:<6} "
                  f"{sequential.vector_search_calls:<6} {sequential.queries_generated:<8} {sequential.results_retrieved:<8}")
            print()
        
        # Summary comparison
        print("SUMMARY COMPARISON:")
        print("-" * 100)
        parallel = analysis['parallel']
        sequential = analysis['sequential']
        comp = analysis['comparison']
        
        print(f"{'Metric':<20} {'Parallel':<15} {'Sequential':<15} {'Improvement':<15}")
        print("-" * 100)
        print(f"{'Avg Total Time':<20} {parallel['avg_total_time']:<15.3f} {sequential['avg_total_time']:<15.3f} {comp['time_improvement']:<15.1f}%")
        print(f"{'Avg Embedding Calls':<20} {parallel['avg_embedding_calls']:<15.1f} {sequential['avg_embedding_calls']:<15.1f} {'Same':<15}")
        print(f"{'Avg Vector Calls':<20} {parallel['avg_vector_calls']:<15.1f} {sequential['avg_vector_calls']:<15.1f} {'Same':<15}")
        print(f"{'Avg Queries':<20} {parallel['avg_queries']:<15.1f} {sequential['avg_queries']:<15.1f} {'Same':<15}")
        print()
        
        # Performance insights
        print("PERFORMANCE INSIGHTS:")
        print("-" * 100)
        
        speedup = comp['speedup_factor']
        improvement = comp['time_improvement']
        
        if speedup > 1:
            print(f"🚀 Parallel processing is {speedup:.2f}x faster than sequential")
            print(f"✅ {improvement:.1f}% performance improvement with parallel processing")
            
            if speedup >= 2:
                print("🎉 Excellent parallel processing performance!")
            elif speedup >= 1.5:
                print("👍 Good parallel processing performance")
            else:
                print("⚠️  Moderate parallel processing benefit")
        else:
            print(f"⚠️  Sequential processing is {1/speedup:.2f}x faster than parallel")
            print("🔍 This might indicate overhead in parallel processing setup")
        
        print(f"📊 API calls are identical: {comp['api_calls_same']}")
        print("\n" + "="*100)

async def main():
    """Main comparison function"""
    print("⚡ Parallel vs Sequential Processing Performance Test")
    print("=" * 60)
    
    try:
        # Initialize test
        test = ParallelVsSequentialTest()
        
        # Run comparison
        results = await test.run_comparison(num_runs=3)
        
        # Analyze results
        analysis = test.analyze_comparison(results)
        
        # Print results
        test.print_comparison(results, analysis)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../reports/performance/parallel_vs_sequential_{timestamp}.json"
        
        # Convert dataclasses to dict for JSON serialization
        serializable_results = {
            "parallel": [
                {
                    "mode": r.mode,
                    "total_time": r.total_time,
                    "embedding_calls": r.embedding_calls,
                    "vector_search_calls": r.vector_search_calls,
                    "queries_generated": r.queries_generated,
                    "results_retrieved": r.results_retrieved,
                    "avg_embedding_time": r.avg_embedding_time,
                    "avg_vector_search_time": r.avg_vector_search_time
                }
                for r in results["parallel"]
            ],
            "sequential": [
                {
                    "mode": r.mode,
                    "total_time": r.total_time,
                    "embedding_calls": r.embedding_calls,
                    "vector_search_calls": r.vector_search_calls,
                    "queries_generated": r.queries_generated,
                    "results_retrieved": r.results_retrieved,
                    "avg_embedding_time": r.avg_embedding_time,
                    "avg_vector_search_time": r.avg_vector_search_time
                }
                for r in results["sequential"]
            ],
            "analysis": analysis,
            "timestamp": results["timestamp"],
            "num_runs": results["num_runs"]
        }
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {filename}")
        
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        print(f"❌ Comparison failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
