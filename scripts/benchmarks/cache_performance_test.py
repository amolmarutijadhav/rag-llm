#!/usr/bin/env python3
"""
Cache Performance Test for Enhanced Chat Completion Service

This script measures the performance improvement brought by in-memory caching
for embedding and vector search operations in the Enhanced Chat Completion Service.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

# Add the project root to Python path
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.domain.services.enhanced_chat_completion_service import EnhancedChatCompletionService
from app.domain.services.rag_service import RAGService
from app.infrastructure.providers.service_locator import ServiceLocator
from app.core.enhanced_chat_config import PERFORMANCE_CONFIG


@dataclass
class CacheTestMetrics:
    """Metrics for cache performance testing"""
    test_name: str
    total_requests: int
    total_time_ms: float
    avg_time_per_request_ms: float
    cache_hits: int
    cache_misses: int
    cache_hit_rate: float
    embedding_calls: int
    vector_search_calls: int
    total_api_calls: int
    avg_api_calls_per_request: float
    performance_improvement_percent: float = 0.0


class CachePerformanceTest:
    """Test class for measuring cache performance improvements"""
    
    def __init__(self):
        self.service_locator = ServiceLocator()
        self.service_locator.initialize_providers()
        self.embedding_provider = self.service_locator.get_embedding_provider()
        self.llm_provider = self.service_locator.get_llm_provider()
        self.vector_store_provider = self.service_locator.get_vector_store_provider()
        self.rag_service = RAGService(self.embedding_provider, self.llm_provider, self.vector_store_provider)
        self.enhanced_service = EnhancedChatCompletionService(self.rag_service, self.llm_provider)
        
        # Test data - using proper request objects
        from app.domain.models.requests import ChatCompletionRequest, ChatMessage
        
        self.test_requests = [
            ChatCompletionRequest(
                messages=[
                    ChatMessage(role="system", content="You are a helpful assistant."),
                    ChatMessage(role="user", content="What are the key requirements for a business requirements document?")
                ],
                model="gpt-3.5-turbo",
                temperature=0.7
            ),
            ChatCompletionRequest(
                messages=[
                    ChatMessage(role="system", content="You are a helpful assistant."),
                    ChatMessage(role="user", content="How should I structure the BRD document?")
                ],
                model="gpt-3.5-turbo",
                temperature=0.7
            ),
            ChatCompletionRequest(
                messages=[
                    ChatMessage(role="system", content="You are a helpful assistant."),
                    ChatMessage(role="user", content="What stakeholders should be involved in BRD review?")
                ],
                model="gpt-3.5-turbo",
                temperature=0.7
            ),
            ChatCompletionRequest(
                messages=[
                    ChatMessage(role="system", content="You are a helpful assistant."),
                    ChatMessage(role="user", content="What are the best practices for BRD documentation?")
                ],
                model="gpt-3.5-turbo",
                temperature=0.7
            ),
            ChatCompletionRequest(
                messages=[
                    ChatMessage(role="system", content="You are a helpful assistant."),
                    ChatMessage(role="user", content="How do I ensure BRD completeness and accuracy?")
                ],
                model="gpt-3.5-turbo",
                temperature=0.7
            )
        ]
        
        # Track API calls
        self.embedding_call_count = 0
        self.vector_search_call_count = 0
        self._setup_tracking()
    
    def _setup_tracking(self):
        """Setup tracking for API calls"""
        original_get_embeddings = self.embedding_provider.get_embeddings
        original_search_vectors = self.vector_store_provider.search_vectors
        
        async def tracked_get_embeddings(texts):
            self.embedding_call_count += 1
            return await original_get_embeddings(texts)
        
        async def tracked_search_vectors(query_vector, top_k, collection_name):
            self.vector_search_call_count += 1
            return await original_search_vectors(query_vector, top_k, collection_name)
        
        self.embedding_provider.get_embeddings = tracked_get_embeddings
        self.vector_store_provider.search_vectors = tracked_search_vectors
    
    def _reset_tracking(self):
        """Reset API call tracking"""
        self.embedding_call_count = 0
        self.vector_search_call_count = 0
    
    async def _run_test_with_cache(self, cache_enabled: bool, test_name: str) -> CacheTestMetrics:
        """Run performance test with or without cache"""
        print(f"\n🧪 Running {test_name}...")
        
        # Reset tracking
        self._reset_tracking()
        
        # Temporarily modify cache configuration
        original_cache_config = PERFORMANCE_CONFIG.get("enable_query_caching", True)
        
        # Import and modify cache service
        from app.core.cache_service import cache_service
        if not cache_enabled:
            # Clear cache and disable it
            await cache_service.clear_all()
            # We'll simulate cache disabled by not using cached results
        
        start_time = time.time()
        
        # Run multiple requests to test cache effectiveness
        successful_requests = 0
        for i, request_data in enumerate(self.test_requests):
            try:
                response = await self.enhanced_service.process_request(request_data)
                if response and response.choices:
                    successful_requests += 1
                    print(f"  ✓ Request {i+1}/{len(self.test_requests)} completed")
                else:
                    print(f"  ✗ Request {i+1}/{len(self.test_requests)} failed")
            except Exception as e:
                print(f"  ✗ Request {i+1}/{len(self.test_requests)} error: {str(e)}")
        
        end_time = time.time()
        total_time_ms = (end_time - start_time) * 1000
        
        # Get cache statistics
        from app.core.cache_service import cache_service
        cache_stats = await cache_service.get_all_stats()
        
        # Calculate metrics
        total_requests = successful_requests
        avg_time_per_request_ms = total_time_ms / total_requests if total_requests > 0 else 0
        
        # Calculate cache hit rate
        embedding_cache_stats = cache_stats.get('embedding_cache', {})
        search_cache_stats = cache_stats.get('search_cache', {})
        
        total_cache_hits = embedding_cache_stats.get('total_access_count', 0) + search_cache_stats.get('total_access_count', 0)
        total_cache_entries = embedding_cache_stats.get('total_entries', 0) + search_cache_stats.get('total_entries', 0)
        
        # Estimate cache misses (simplified)
        cache_misses = self.embedding_call_count + self.vector_search_call_count
        cache_hits = max(0, total_cache_hits - cache_misses)  # Rough estimate
        cache_hit_rate = (cache_hits / (cache_hits + cache_misses)) * 100 if (cache_hits + cache_misses) > 0 else 0
        
        total_api_calls = self.embedding_call_count + self.vector_search_call_count
        avg_api_calls_per_request = total_api_calls / total_requests if total_requests > 0 else 0
        
        return CacheTestMetrics(
            test_name=test_name,
            total_requests=total_requests,
            total_time_ms=total_time_ms,
            avg_time_per_request_ms=avg_time_per_request_ms,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            cache_hit_rate=cache_hit_rate,
            embedding_calls=self.embedding_call_count,
            vector_search_calls=self.vector_search_call_count,
            total_api_calls=total_api_calls,
            avg_api_calls_per_request=avg_api_calls_per_request
        )
    
    async def run_cache_performance_test(self) -> Dict[str, Any]:
        """Run comprehensive cache performance test"""
        print("🚀 Starting Cache Performance Test")
        print("=" * 50)
        
        # Test 1: Without cache (first run)
        print("\n📊 Test 1: First run (cache cold)")
        metrics_no_cache = await self._run_test_with_cache(False, "Cold Cache")
        
        # Test 2: With cache (second run - should be faster)
        print("\n📊 Test 2: Second run (cache warm)")
        metrics_with_cache = await self._run_test_with_cache(True, "Warm Cache")
        
        # Calculate performance improvement
        if metrics_no_cache.avg_time_per_request_ms > 0:
            improvement = ((metrics_no_cache.avg_time_per_request_ms - metrics_with_cache.avg_time_per_request_ms) / 
                         metrics_no_cache.avg_time_per_request_ms) * 100
            metrics_with_cache.performance_improvement_percent = improvement
        
        # Test 3: Repeated identical requests (cache hot)
        print("\n📊 Test 3: Repeated identical requests (cache hot)")
        repeated_requests = []
        for _ in range(3):  # Run same requests multiple times
            repeated_requests.extend(self.test_requests[:2])  # Use first 2 requests
        
        self._reset_tracking()
        start_time = time.time()
        
        successful_requests = 0
        for i, request_data in enumerate(repeated_requests):
            try:
                response = await self.enhanced_service.process_request(request_data)
                if response and response.choices:
                    successful_requests += 1
            except Exception as e:
                print(f"  ✗ Repeated request {i+1} error: {str(e)}")
        
        end_time = time.time()
        total_time_ms = (end_time - start_time) * 1000
        
        from app.core.cache_service import cache_service
        cache_stats = await cache_service.get_all_stats()
        embedding_cache_stats = cache_stats.get('embedding_cache', {})
        search_cache_stats = cache_stats.get('search_cache', {})
        
        total_cache_hits = embedding_cache_stats.get('total_access_count', 0) + search_cache_stats.get('total_access_count', 0)
        cache_misses = self.embedding_call_count + self.vector_search_call_count
        cache_hits = max(0, total_cache_hits - cache_misses)
        cache_hit_rate = (cache_hits / (cache_hits + cache_misses)) * 100 if (cache_hits + cache_misses) > 0 else 0
        
        metrics_hot_cache = CacheTestMetrics(
            test_name="Hot Cache (Repeated Requests)",
            total_requests=successful_requests,
            total_time_ms=total_time_ms,
            avg_time_per_request_ms=total_time_ms / successful_requests if successful_requests > 0 else 0,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            cache_hit_rate=cache_hit_rate,
            embedding_calls=self.embedding_call_count,
            vector_search_calls=self.vector_search_call_count,
            total_api_calls=self.embedding_call_count + self.vector_search_call_count,
            avg_api_calls_per_request=(self.embedding_call_count + self.vector_search_call_count) / successful_requests if successful_requests > 0 else 0
        )
        
        # Calculate improvement from cold to hot cache
        if metrics_no_cache.avg_time_per_request_ms > 0:
            hot_improvement = ((metrics_no_cache.avg_time_per_request_ms - metrics_hot_cache.avg_time_per_request_ms) / 
                             metrics_no_cache.avg_time_per_request_ms) * 100
            metrics_hot_cache.performance_improvement_percent = hot_improvement
        
        # Compile results
        results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_configuration": {
                "parallel_processing_enabled": PERFORMANCE_CONFIG.get("enable_parallel_processing", True),
                "max_concurrent_queries": PERFORMANCE_CONFIG.get("max_concurrent_queries", 4),
                "cache_enabled": PERFORMANCE_CONFIG.get("enable_query_caching", True),
                "cache_ttl_seconds": PERFORMANCE_CONFIG.get("cache_ttl_seconds", 300)
            },
            "test_results": {
                "cold_cache": asdict(metrics_no_cache),
                "warm_cache": asdict(metrics_with_cache),
                "hot_cache": asdict(metrics_hot_cache)
            },
            "performance_summary": {
                "cold_to_warm_improvement_percent": metrics_with_cache.performance_improvement_percent,
                "cold_to_hot_improvement_percent": metrics_hot_cache.performance_improvement_percent,
                "cache_effectiveness": {
                    "warm_cache_hit_rate": metrics_with_cache.cache_hit_rate,
                    "hot_cache_hit_rate": metrics_hot_cache.cache_hit_rate,
                    "api_call_reduction": {
                        "cold_cache_avg_calls": metrics_no_cache.avg_api_calls_per_request,
                        "warm_cache_avg_calls": metrics_with_cache.avg_api_calls_per_request,
                        "hot_cache_avg_calls": metrics_hot_cache.avg_api_calls_per_request
                    }
                }
            }
        }
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📈 CACHE PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        cold = results["test_results"]["cold_cache"]
        warm = results["test_results"]["warm_cache"]
        hot = results["test_results"]["hot_cache"]
        
        print(f"\n⏱️  Response Time Performance:")
        print(f"   Cold Cache:     {cold['avg_time_per_request_ms']:.1f}ms per request")
        print(f"   Warm Cache:     {warm['avg_time_per_request_ms']:.1f}ms per request")
        print(f"   Hot Cache:      {hot['avg_time_per_request_ms']:.1f}ms per request")
        
        print(f"\n🚀 Performance Improvements:")
        print(f"   Cold → Warm:    {warm['performance_improvement_percent']:.1f}% faster")
        print(f"   Cold → Hot:     {hot['performance_improvement_percent']:.1f}% faster")
        
        print(f"\n💾 Cache Effectiveness:")
        print(f"   Warm Cache Hit Rate: {warm['cache_hit_rate']:.1f}%")
        print(f"   Hot Cache Hit Rate:  {hot['cache_hit_rate']:.1f}%")
        
        print(f"\n📊 API Call Reduction:")
        print(f"   Cold Cache:     {cold['avg_api_calls_per_request']:.1f} calls per request")
        print(f"   Warm Cache:     {warm['avg_api_calls_per_request']:.1f} calls per request")
        print(f"   Hot Cache:      {hot['avg_api_calls_per_request']:.1f} calls per request")
        
        print(f"\n🔧 Configuration:")
        config = results["test_configuration"]
        print(f"   Parallel Processing: {config['parallel_processing_enabled']}")
        print(f"   Max Concurrent:      {config['max_concurrent_queries']}")
        print(f"   Cache Enabled:       {config['cache_enabled']}")
        print(f"   Cache TTL:           {config['cache_ttl_seconds']}s")


async def main():
    """Main function to run the cache performance test"""
    try:
        # Create test instance
        test = CachePerformanceTest()
        
        # Run the test
        results = await test.run_cache_performance_test()
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../reports/performance/cache_performance_test_{timestamp}.json"
        
        print(f"📁 Attempting to save to: {os.path.abspath(filename)}")
        
        # Ensure directory exists
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            print(f"✅ Directory created/verified: {os.path.dirname(filename)}")
        except Exception as e:
            print(f"❌ Error creating directory: {e}")
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✅ Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving file: {e}")
            # Try saving to current directory as fallback
            fallback_filename = f"cache_performance_test_{timestamp}.json"
            with open(fallback_filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"✅ Results saved to fallback location: {fallback_filename}")
        
    except Exception as e:
        print(f"❌ Error running cache performance test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
