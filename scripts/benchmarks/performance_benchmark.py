#!/usr/bin/env python3
"""
Performance Benchmarking Script for Enhanced Chat Completion Service

This script measures the real performance impact of multiple embedding and vector query calls
in the enhanced chat completion service compared to the original single-query approach.
"""

import asyncio
import time
import json
import statistics
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
class PerformanceMetrics:
    """Container for performance metrics"""
    total_time: float
    embedding_calls: int
    vector_search_calls: int
    llm_calls: int
    queries_generated: int
    results_retrieved: int
    avg_embedding_time: float
    avg_vector_search_time: float
    avg_llm_time: float
    parallel_processing: bool

class PerformanceBenchmark:
    """Performance benchmarking for enhanced chat completion"""
    
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
        self.llm_times = []
        self.embedding_call_count = 0
        self.vector_search_call_count = 0
        self.llm_call_count = 0
        
        # Mock the providers to track calls
        self._setup_performance_tracking()
    
    def _setup_performance_tracking(self):
        """Setup performance tracking by wrapping provider methods"""
        original_get_embeddings = self.rag_service.embedding_provider.get_embeddings
        original_search_vectors = self.rag_service.vector_store_provider.search_vectors
        original_call_llm = self.llm_provider.call_llm_api
        
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
        
        async def tracked_call_llm(messages, **kwargs):
            start_time = time.time()
            self.llm_call_count += 1
            result = await original_call_llm(messages, **kwargs)
            end_time = time.time()
            self.llm_times.append(end_time - start_time)
            return result
        
        self.rag_service.embedding_provider.get_embeddings = tracked_get_embeddings
        self.rag_service.vector_store_provider.search_vectors = tracked_search_vectors
        self.llm_provider.call_llm_api = tracked_call_llm
    
    def _reset_metrics(self):
        """Reset performance metrics"""
        self.embedding_times = []
        self.vector_search_times = []
        self.llm_times = []
        self.embedding_call_count = 0
        self.vector_search_call_count = 0
        self.llm_call_count = 0
    
    def _create_test_request(self, conversation_turns: int = 3) -> ChatCompletionRequest:
        """Create a test request with specified conversation turns"""
        messages = [
            ChatMessage(role="system", content="You are a Credit Officer specializing in regulatory compliance.")
        ]
        
        # Add conversation turns
        for i in range(conversation_turns):
            if i % 2 == 0:
                messages.append(ChatMessage(role="user", content=f"Turn {i+1}: I need help with Basel III compliance requirements for SME lending"))
            else:
                messages.append(ChatMessage(role="assistant", content=f"Turn {i+1}: I'll help you with Basel III compliance. Let me gather relevant information."))
        
        # Final user question
        messages.append(ChatMessage(role="user", content="What are the key capital requirements for SME exposures under Basel III?"))
        
        return ChatCompletionRequest(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
    
    async def benchmark_single_run(self, request: ChatCompletionRequest) -> PerformanceMetrics:
        """Run a single benchmark test"""
        self._reset_metrics()
        
        start_time = time.time()
        response = await self.enhanced_service.process_request(request)
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # Calculate averages
        avg_embedding_time = statistics.mean(self.embedding_times) if self.embedding_times else 0
        avg_vector_search_time = statistics.mean(self.vector_search_times) if self.vector_search_times else 0
        avg_llm_time = statistics.mean(self.llm_times) if self.llm_times else 0
        
        # Get metadata from response
        metadata = response.metadata or {}
        queries_generated = metadata.get("enhanced_queries_count", 0)
        results_retrieved = len(metadata.get("rag_results", []))
        parallel_processing = metadata.get("parallel_processing_enabled", False)
        
        return PerformanceMetrics(
            total_time=total_time,
            embedding_calls=self.embedding_call_count,
            vector_search_calls=self.vector_search_call_count,
            llm_calls=self.llm_call_count,
            queries_generated=queries_generated,
            results_retrieved=results_retrieved,
            avg_embedding_time=avg_embedding_time,
            avg_vector_search_time=avg_vector_search_time,
            avg_llm_time=avg_llm_time,
            parallel_processing=parallel_processing
        )
    
    async def benchmark_multiple_runs(self, num_runs: int = 5, conversation_turns: int = 3) -> List[PerformanceMetrics]:
        """Run multiple benchmark tests"""
        results = []
        request = self._create_test_request(conversation_turns)
        
        logger.info(f"Starting benchmark with {num_runs} runs, {conversation_turns} conversation turns")
        
        for i in range(num_runs):
            logger.info(f"Running benchmark {i+1}/{num_runs}")
            metrics = await self.benchmark_single_run(request)
            results.append(metrics)
            
            # Small delay between runs
            await asyncio.sleep(1)
        
        return results
    
    def analyze_results(self, results: List[PerformanceMetrics]) -> Dict[str, Any]:
        """Analyze benchmark results"""
        if not results:
            return {}
        
        # Calculate statistics
        total_times = [r.total_time for r in results]
        embedding_calls = [r.embedding_calls for r in results]
        vector_search_calls = [r.vector_search_calls for r in results]
        queries_generated = [r.queries_generated for r in results]
        
        analysis = {
            "summary": {
                "total_runs": len(results),
                "avg_total_time": statistics.mean(total_times),
                "min_total_time": min(total_times),
                "max_total_time": max(total_times),
                "std_total_time": statistics.stdev(total_times) if len(total_times) > 1 else 0,
                "avg_embedding_calls": statistics.mean(embedding_calls),
                "avg_vector_search_calls": statistics.mean(vector_search_calls),
                "avg_queries_generated": statistics.mean(queries_generated),
                "parallel_processing_used": any(r.parallel_processing for r in results)
            },
            "detailed_metrics": []
        }
        
        for i, result in enumerate(results):
            analysis["detailed_metrics"].append({
                "run": i + 1,
                "total_time": result.total_time,
                "embedding_calls": result.embedding_calls,
                "vector_search_calls": result.vector_search_calls,
                "llm_calls": result.llm_calls,
                "queries_generated": result.queries_generated,
                "results_retrieved": result.results_retrieved,
                "avg_embedding_time": result.avg_embedding_time,
                "avg_vector_search_time": result.avg_vector_search_time,
                "avg_llm_time": result.avg_llm_time,
                "parallel_processing": result.parallel_processing
            })
        
        return analysis
    
    def print_results(self, analysis: Dict[str, Any]):
        """Print benchmark results in a formatted way"""
        summary = analysis["summary"]
        
        print("\n" + "="*80)
        print("ENHANCED CHAT COMPLETION PERFORMANCE BENCHMARK RESULTS")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Runs: {summary['total_runs']}")
        print(f"Parallel Processing: {'Enabled' if summary['parallel_processing_used'] else 'Disabled'}")
        print()
        
        print("PERFORMANCE METRICS:")
        print("-" * 40)
        print(f"Average Total Time:     {summary['avg_total_time']:.3f}s")
        print(f"Min Total Time:         {summary['min_total_time']:.3f}s")
        print(f"Max Total Time:         {summary['max_total_time']:.3f}s")
        print(f"Standard Deviation:     {summary['std_total_time']:.3f}s")
        print()
        
        print("API CALL METRICS:")
        print("-" * 40)
        print(f"Average Embedding Calls:    {summary['avg_embedding_calls']:.1f}")
        print(f"Average Vector Search Calls: {summary['avg_vector_search_calls']:.1f}")
        print(f"Average Queries Generated:   {summary['avg_queries_generated']:.1f}")
        print()
        
        print("DETAILED RUN RESULTS:")
        print("-" * 80)
        print(f"{'Run':<4} {'Total(s)':<8} {'Embed':<6} {'Search':<6} {'LLM':<4} {'Queries':<8} {'Results':<8}")
        print("-" * 80)
        
        for metric in analysis["detailed_metrics"]:
            print(f"{metric['run']:<4} {metric['total_time']:<8.3f} {metric['embedding_calls']:<6} "
                  f"{metric['vector_search_calls']:<6} {metric['llm_calls']:<4} {metric['queries_generated']:<8} "
                  f"{metric['results_retrieved']:<8}")
        
        print("="*80)
        
        # Performance insights
        print("\nPERFORMANCE INSIGHTS:")
        print("-" * 40)
        avg_queries = summary['avg_queries_generated']
        avg_time = summary['avg_total_time']
        
        if avg_queries > 1:
            print(f"✅ Multi-query generation: {avg_queries:.1f} queries per request")
            print(f"✅ Enhanced retrieval: {summary['avg_vector_search_calls']:.1f} vector searches")
            print(f"✅ Total processing time: {avg_time:.3f}s")
            
            if summary['parallel_processing_used']:
                print("✅ Parallel processing enabled for improved performance")
            else:
                print("⚠️  Sequential processing used (parallel disabled)")
        else:
            print("⚠️  Single query generation detected")
        
        print("\n" + "="*80)

async def main():
    """Main benchmarking function"""
    print("🚀 Enhanced Chat Completion Performance Benchmark")
    print("=" * 60)
    
    try:
        # Initialize benchmark
        benchmark = PerformanceBenchmark()
        
        # Run benchmarks with different conversation lengths
        conversation_lengths = [1, 3, 5]
        num_runs = 3
        
        all_results = {}
        
        for turns in conversation_lengths:
            print(f"\n📊 Benchmarking with {turns} conversation turn(s)...")
            results = await benchmark.benchmark_multiple_runs(num_runs, turns)
            analysis = benchmark.analyze_results(results)
            all_results[f"{turns}_turns"] = analysis
            
            # Print results for this configuration
            benchmark.print_results(analysis)
        
        # Save detailed results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../reports/performance/performance_benchmark_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {filename}")
        
        # Summary comparison
        print("\n📈 PERFORMANCE COMPARISON SUMMARY:")
        print("-" * 50)
        for turns, analysis in all_results.items():
            summary = analysis["summary"]
            print(f"{turns:>12}: {summary['avg_total_time']:.3f}s avg, "
                  f"{summary['avg_queries_generated']:.1f} queries, "
                  f"{summary['avg_embedding_calls']:.1f} embedding calls")
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        print(f"❌ Benchmark failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
