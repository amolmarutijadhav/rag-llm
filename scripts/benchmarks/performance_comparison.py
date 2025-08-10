#!/usr/bin/env python3
"""
Performance Comparison: Single Query vs Multi-Query RAG

This script compares the performance impact of single query vs multi-query approaches
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
class ComparisonMetrics:
    """Metrics for performance comparison"""
    approach: str
    total_time: float
    embedding_calls: int
    vector_search_calls: int
    queries_generated: int
    results_retrieved: int
    avg_embedding_time: float
    avg_vector_search_time: float

class PerformanceComparison:
    """Compare single query vs multi-query performance"""
    
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
    
    def _create_single_query_request(self) -> ChatCompletionRequest:
        """Create a request that should generate single query"""
        return ChatCompletionRequest(
            model="gpt-4",
            messages=[
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content="What is the capital of France?")
            ],
            temperature=0.7,
            max_tokens=1000
        )
    
    def _create_multi_query_request(self) -> ChatCompletionRequest:
        """Create a request that should generate multiple queries"""
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
    
    async def test_approach(self, request: ChatCompletionRequest, approach_name: str) -> ComparisonMetrics:
        """Test a specific approach"""
        self._reset_metrics()
        
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
        
        return ComparisonMetrics(
            approach=approach_name,
            total_time=total_time,
            embedding_calls=self.embedding_call_count,
            vector_search_calls=self.vector_search_call_count,
            queries_generated=queries_generated,
            results_retrieved=results_retrieved,
            avg_embedding_time=avg_embedding_time,
            avg_vector_search_time=avg_vector_search_time
        )
    
    async def run_comparison(self, num_runs: int = 5) -> Dict[str, Any]:
        """Run the performance comparison"""
        print(f"🔄 Running performance comparison with {num_runs} runs per approach...")
        
        single_query_results = []
        multi_query_results = []
        
        for i in range(num_runs):
            print(f"  Run {i+1}/{num_runs}...")
            
            # Test single query approach
            single_request = self._create_single_query_request()
            single_metrics = await self.test_approach(single_request, "single_query")
            single_query_results.append(single_metrics)
            
            # Test multi-query approach
            multi_request = self._create_multi_query_request()
            multi_metrics = await self.test_approach(multi_request, "multi_query")
            multi_query_results.append(multi_metrics)
            
            # Small delay between runs
            await asyncio.sleep(1)
        
        return {
            "single_query": single_query_results,
            "multi_query": multi_query_results,
            "timestamp": datetime.now().isoformat(),
            "num_runs": num_runs
        }
    
    def analyze_comparison(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze comparison results"""
        single_results = results["single_query"]
        multi_results = results["multi_query"]
        
        # Calculate averages for single query
        single_times = [r.total_time for r in single_results]
        single_embedding_calls = [r.embedding_calls for r in single_results]
        single_vector_calls = [r.vector_search_calls for r in single_results]
        single_queries = [r.queries_generated for r in single_results]
        
        # Calculate averages for multi-query
        multi_times = [r.total_time for r in multi_results]
        multi_embedding_calls = [r.embedding_calls for r in multi_results]
        multi_vector_calls = [r.vector_search_calls for r in multi_results]
        multi_queries = [r.queries_generated for r in multi_results]
        
        analysis = {
            "single_query": {
                "avg_total_time": sum(single_times) / len(single_times),
                "avg_embedding_calls": sum(single_embedding_calls) / len(single_embedding_calls),
                "avg_vector_calls": sum(single_vector_calls) / len(single_vector_calls),
                "avg_queries": sum(single_queries) / len(single_queries),
                "min_time": min(single_times),
                "max_time": max(single_times)
            },
            "multi_query": {
                "avg_total_time": sum(multi_times) / len(multi_times),
                "avg_embedding_calls": sum(multi_embedding_calls) / len(multi_embedding_calls),
                "avg_vector_calls": sum(multi_vector_calls) / len(multi_vector_calls),
                "avg_queries": sum(multi_queries) / len(multi_queries),
                "min_time": min(multi_times),
                "max_time": max(multi_times)
            },
            "comparison": {
                "time_increase": ((sum(multi_times) / len(multi_times)) / (sum(single_times) / len(single_times)) - 1) * 100,
                "embedding_calls_increase": ((sum(multi_embedding_calls) / len(multi_embedding_calls)) / (sum(single_embedding_calls) / len(single_embedding_calls)) - 1) * 100,
                "vector_calls_increase": ((sum(multi_vector_calls) / len(multi_vector_calls)) / (sum(single_vector_calls) / len(single_vector_calls)) - 1) * 100,
                "queries_increase": ((sum(multi_queries) / len(multi_queries)) / (sum(single_queries) / len(single_queries)) - 1) * 100
            }
        }
        
        return analysis
    
    def print_comparison(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Print comparison results"""
        print("\n" + "="*100)
        print("PERFORMANCE COMPARISON: SINGLE QUERY vs MULTI-QUERY RAG")
        print("="*100)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Runs per approach: {results['num_runs']}")
        print()
        
        # Detailed results table
        print("DETAILED RESULTS:")
        print("-" * 100)
        print(f"{'Run':<4} {'Approach':<12} {'Time(s)':<8} {'Embed':<6} {'Search':<6} {'Queries':<8} {'Results':<8}")
        print("-" * 100)
        
        for i in range(results['num_runs']):
            single = results['single_query'][i]
            multi = results['multi_query'][i]
            
            print(f"{i+1:<4} {'Single':<12} {single.total_time:<8.3f} {single.embedding_calls:<6} "
                  f"{single.vector_search_calls:<6} {single.queries_generated:<8} {single.results_retrieved:<8}")
            print(f"{'':<4} {'Multi':<12} {multi.total_time:<8.3f} {multi.embedding_calls:<6} "
                  f"{multi.vector_search_calls:<6} {multi.queries_generated:<8} {multi.results_retrieved:<8}")
            print()
        
        # Summary comparison
        print("SUMMARY COMPARISON:")
        print("-" * 100)
        single = analysis['single_query']
        multi = analysis['multi_query']
        comp = analysis['comparison']
        
        print(f"{'Metric':<20} {'Single Query':<15} {'Multi Query':<15} {'Increase':<15}")
        print("-" * 100)
        print(f"{'Avg Total Time':<20} {single['avg_total_time']:<15.3f} {multi['avg_total_time']:<15.3f} {comp['time_increase']:<15.1f}%")
        print(f"{'Avg Embedding Calls':<20} {single['avg_embedding_calls']:<15.1f} {multi['avg_embedding_calls']:<15.1f} {comp['embedding_calls_increase']:<15.1f}%")
        print(f"{'Avg Vector Calls':<20} {single['avg_vector_calls']:<15.1f} {multi['avg_vector_calls']:<15.1f} {comp['vector_calls_increase']:<15.1f}%")
        print(f"{'Avg Queries':<20} {single['avg_queries']:<15.1f} {multi['avg_queries']:<15.1f} {comp['queries_increase']:<15.1f}%")
        print()
        
        # Performance insights
        print("PERFORMANCE INSIGHTS:")
        print("-" * 100)
        
        time_increase = comp['time_increase']
        queries_increase = comp['queries_increase']
        
        if time_increase > 0:
            print(f"⚠️  Multi-query approach takes {time_increase:.1f}% more time")
            print(f"✅ Multi-query approach generates {queries_increase:.1f}% more queries")
            
            if time_increase < 50:
                print("✅ Performance impact is reasonable for enhanced retrieval")
            elif time_increase < 100:
                print("⚠️  Moderate performance impact - consider optimization")
            else:
                print("❌ High performance impact - needs optimization")
        else:
            print("✅ Multi-query approach is faster (parallel processing benefit)")
        
        # Parallel processing benefit
        if multi['avg_queries'] > single['avg_queries']:
            efficiency = (multi['avg_queries'] / single['avg_queries']) / (multi['avg_total_time'] / single['avg_total_time'])
            print(f"📈 Query efficiency: {efficiency:.2f}x more queries per second")
        
        print("\n" + "="*100)

async def main():
    """Main comparison function"""
    print("🔍 Performance Comparison: Single Query vs Multi-Query RAG")
    print("=" * 70)
    
    try:
        # Initialize comparison
        comparison = PerformanceComparison()
        
        # Run comparison
        results = await comparison.run_comparison(num_runs=3)
        
        # Analyze results
        analysis = comparison.analyze_comparison(results)
        
        # Print results
        comparison.print_comparison(results, analysis)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"performance_comparison_{timestamp}.json"
        
        # Convert dataclasses to dict for JSON serialization
        serializable_results = {
            "single_query": [
                {
                    "approach": r.approach,
                    "total_time": r.total_time,
                    "embedding_calls": r.embedding_calls,
                    "vector_search_calls": r.vector_search_calls,
                    "queries_generated": r.queries_generated,
                    "results_retrieved": r.results_retrieved,
                    "avg_embedding_time": r.avg_embedding_time,
                    "avg_vector_search_time": r.avg_vector_search_time
                }
                for r in results["single_query"]
            ],
            "multi_query": [
                {
                    "approach": r.approach,
                    "total_time": r.total_time,
                    "embedding_calls": r.embedding_calls,
                    "vector_search_calls": r.vector_search_calls,
                    "queries_generated": r.queries_generated,
                    "results_retrieved": r.results_retrieved,
                    "avg_embedding_time": r.avg_embedding_time,
                    "avg_vector_search_time": r.avg_vector_search_time
                }
                for r in results["multi_query"]
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
