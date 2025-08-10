#!/usr/bin/env python3
"""
Connection Pooling Performance Comparison

This script compares the performance impact of connection pooling vs non-connection pooling
by testing HTTP client creation overhead and connection reuse benefits.
"""

import asyncio
import time
import json
import httpx
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import statistics

from app.infrastructure.providers.service_locator import ServiceLocator
from app.infrastructure.providers.enhanced_base_provider import EnhancedBaseProvider
from app.core.logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class PoolingMetrics:
    """Metrics for connection pooling comparison"""
    approach: str
    total_time: float
    request_count: int
    avg_request_time: float
    min_request_time: float
    max_request_time: float
    median_request_time: float
    std_deviation: float
    connection_creation_count: int
    connection_reuse_count: int

class ConnectionPoolingPerformanceTest:
    """Test connection pooling performance benefits"""
    
    def __init__(self):
        self.service_locator = ServiceLocator()
        self.service_locator.initialize_providers()
        
        # Get providers
        self.embedding_provider = self.service_locator.get_embedding_provider()
        self.llm_provider = self.service_locator.get_llm_provider()
        self.vector_store_provider = self.service_locator.get_vector_store_provider()
        
        # Test configuration
        self.test_url = "https://httpbin.org/delay/0.1"  # Simulate API delay
        self.request_count = 20
        self.concurrent_requests = 5
        
        # Performance tracking
        self.request_times = []
        self.connection_creation_count = 0
        self.connection_reuse_count = 0
    
    def _reset_metrics(self):
        """Reset performance metrics"""
        self.request_times = []
        self.connection_creation_count = 0
        self.connection_reuse_count = 0
    
    async def _make_request_with_pooling(self, client: httpx.AsyncClient, request_id: int) -> float:
        """Make a request using connection pooling"""
        start_time = time.time()
        
        try:
            response = await client.get(self.test_url)
            response.raise_for_status()
            
            end_time = time.time()
            request_time = end_time - start_time
            self.request_times.append(request_time)
            
            logger.debug(f"Pooled request {request_id} completed in {request_time:.3f}s")
            return request_time
            
        except Exception as e:
            logger.error(f"Pooled request {request_id} failed: {e}")
            return -1
    
    async def _make_request_without_pooling(self, request_id: int) -> float:
        """Make a request without connection pooling (new client each time)"""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.test_url)
                response.raise_for_status()
                
                end_time = time.time()
                request_time = end_time - start_time
                self.request_times.append(request_time)
                
                logger.debug(f"Non-pooled request {request_id} completed in {request_time:.3f}s")
                return request_time
                
        except Exception as e:
            logger.error(f"Non-pooled request {request_id} failed: {e}")
            return -1
    
    async def test_with_pooling(self) -> PoolingMetrics:
        """Test performance with connection pooling"""
        logger.info("🔗 Testing with connection pooling...")
        self._reset_metrics()
        
        start_time = time.time()
        
        # Create a single client for all requests
        async with httpx.AsyncClient(
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30.0
            )
        ) as client:
            
            # Make concurrent requests
            tasks = []
            for i in range(self.request_count):
                task = self._make_request_with_pooling(client, i + 1)
                tasks.append(task)
            
            # Execute requests in batches to simulate concurrent load
            for i in range(0, len(tasks), self.concurrent_requests):
                batch = tasks[i:i + self.concurrent_requests]
                await asyncio.gather(*batch)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate metrics
        successful_times = [t for t in self.request_times if t > 0]
        if not successful_times:
            raise ValueError("No successful requests with pooling")
        
        return PoolingMetrics(
            approach="With Connection Pooling",
            total_time=total_time,
            request_count=len(successful_times),
            avg_request_time=statistics.mean(successful_times),
            min_request_time=min(successful_times),
            max_request_time=max(successful_times),
            median_request_time=statistics.median(successful_times),
            std_deviation=statistics.stdev(successful_times) if len(successful_times) > 1 else 0,
            connection_creation_count=1,  # Only one client created
            connection_reuse_count=len(successful_times) - 1  # All but first reuse
        )
    
    async def test_without_pooling(self) -> PoolingMetrics:
        """Test performance without connection pooling"""
        logger.info("🔌 Testing without connection pooling...")
        self._reset_metrics()
        
        start_time = time.time()
        
        # Make requests without pooling (new client each time)
        tasks = []
        for i in range(self.request_count):
            task = self._make_request_without_pooling(i + 1)
            tasks.append(task)
        
        # Execute requests in batches
        for i in range(0, len(tasks), self.concurrent_requests):
            batch = tasks[i:i + self.concurrent_requests]
            await asyncio.gather(*batch)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate metrics
        successful_times = [t for t in self.request_times if t > 0]
        if not successful_times:
            raise ValueError("No successful requests without pooling")
        
        return PoolingMetrics(
            approach="Without Connection Pooling",
            total_time=total_time,
            request_count=len(successful_times),
            avg_request_time=statistics.mean(successful_times),
            min_request_time=min(successful_times),
            max_request_time=max(successful_times),
            median_request_time=statistics.median(successful_times),
            std_deviation=statistics.stdev(successful_times) if len(successful_times) > 1 else 0,
            connection_creation_count=len(successful_times),  # New client for each request
            connection_reuse_count=0  # No reuse
        )
    
    async def test_provider_performance(self) -> Dict[str, PoolingMetrics]:
        """Test performance with actual providers"""
        logger.info("🏭 Testing provider performance with connection pooling...")
        
        results = {}
        
        # Test embedding provider
        logger.info("Testing embedding provider...")
        start_time = time.time()
        self._reset_metrics()
        
        # Make multiple embedding calls
        test_texts = [f"Test text {i} for embedding performance testing" for i in range(10)]
        
        for i, text in enumerate(test_texts):
            request_start = time.time()
            try:
                embeddings = await self.embedding_provider.get_embeddings([text])
                request_end = time.time()
                self.request_times.append(request_end - request_start)
                logger.debug(f"Embedding request {i+1} completed in {request_end - request_start:.3f}s")
            except Exception as e:
                logger.error(f"Embedding request {i+1} failed: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful_times = [t for t in self.request_times if t > 0]
        if successful_times:
            results['embedding_provider'] = PoolingMetrics(
                approach="Embedding Provider (With Pooling)",
                total_time=total_time,
                request_count=len(successful_times),
                avg_request_time=statistics.mean(successful_times),
                min_request_time=min(successful_times),
                max_request_time=max(successful_times),
                median_request_time=statistics.median(successful_times),
                std_deviation=statistics.stdev(successful_times) if len(successful_times) > 1 else 0,
                connection_creation_count=1,
                connection_reuse_count=len(successful_times) - 1
            )
        
        # Test LLM provider
        logger.info("Testing LLM provider...")
        start_time = time.time()
        self._reset_metrics()
        
        # Make multiple LLM calls
        test_messages = [
            "Hello, how are you?",
            "What is the weather like?",
            "Tell me a joke",
            "Explain quantum computing",
            "What is machine learning?"
        ]
        
        for i, message in enumerate(test_messages):
            request_start = time.time()
            try:
                response = await self.llm_provider.call_llm(message)
                request_end = time.time()
                self.request_times.append(request_end - request_start)
                logger.debug(f"LLM request {i+1} completed in {request_end - request_start:.3f}s")
            except Exception as e:
                logger.error(f"LLM request {i+1} failed: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful_times = [t for t in self.request_times if t > 0]
        if successful_times:
            results['llm_provider'] = PoolingMetrics(
                approach="LLM Provider (With Pooling)",
                total_time=total_time,
                request_count=len(successful_times),
                avg_request_time=statistics.mean(successful_times),
                min_request_time=min(successful_times),
                max_request_time=max(successful_times),
                median_request_time=statistics.median(successful_times),
                std_deviation=statistics.stdev(successful_times) if len(successful_times) > 1 else 0,
                connection_creation_count=1,
                connection_reuse_count=len(successful_times) - 1
            )
        
        return results
    
    def analyze_comparison(self, pooling_metrics: PoolingMetrics, non_pooling_metrics: PoolingMetrics) -> Dict[str, Any]:
        """Analyze the performance comparison"""
        analysis = {
            'total_time_improvement': {
                'absolute': non_pooling_metrics.total_time - pooling_metrics.total_time,
                'percentage': ((non_pooling_metrics.total_time - pooling_metrics.total_time) / non_pooling_metrics.total_time) * 100
            },
            'avg_request_time_improvement': {
                'absolute': non_pooling_metrics.avg_request_time - pooling_metrics.avg_request_time,
                'percentage': ((non_pooling_metrics.avg_request_time - pooling_metrics.avg_request_time) / non_pooling_metrics.avg_request_time) * 100
            },
            'connection_efficiency': {
                'creation_reduction': non_pooling_metrics.connection_creation_count - pooling_metrics.connection_creation_count,
                'reuse_benefit': pooling_metrics.connection_reuse_count,
                'efficiency_ratio': pooling_metrics.connection_reuse_count / non_pooling_metrics.connection_creation_count if non_pooling_metrics.connection_creation_count > 0 else 0
            },
            'throughput_improvement': {
                'requests_per_second_pooling': pooling_metrics.request_count / pooling_metrics.total_time,
                'requests_per_second_non_pooling': non_pooling_metrics.request_count / non_pooling_metrics.total_time,
                'improvement_factor': (pooling_metrics.request_count / pooling_metrics.total_time) / (non_pooling_metrics.request_count / non_pooling_metrics.total_time)
            }
        }
        
        return analysis
    
    def print_comparison(self, pooling_metrics: PoolingMetrics, non_pooling_metrics: PoolingMetrics, analysis: Dict[str, Any]):
        """Print the performance comparison results"""
        print("\n" + "="*80)
        print("🔗 CONNECTION POOLING PERFORMANCE COMPARISON")
        print("="*80)
        
        print(f"\n📊 Test Configuration:")
        print(f"   • Total requests: {self.request_count}")
        print(f"   • Concurrent requests: {self.concurrent_requests}")
        print(f"   • Test URL: {self.test_url}")
        
        print(f"\n📈 Performance Results:")
        print(f"\n{'Metric':<30} {'With Pooling':<20} {'Without Pooling':<20} {'Improvement':<15}")
        print("-" * 85)
        print(f"{'Total Time (s)':<30} {pooling_metrics.total_time:<20.3f} {non_pooling_metrics.total_time:<20.3f} {analysis['total_time_improvement']['percentage']:<15.1f}%")
        print(f"{'Avg Request Time (s)':<30} {pooling_metrics.avg_request_time:<20.3f} {non_pooling_metrics.avg_request_time:<20.3f} {analysis['avg_request_time_improvement']['percentage']:<15.1f}%")
        print(f"{'Min Request Time (s)':<30} {pooling_metrics.min_request_time:<20.3f} {non_pooling_metrics.min_request_time:<20.3f}")
        print(f"{'Max Request Time (s)':<30} {pooling_metrics.max_request_time:<20.3f} {non_pooling_metrics.max_request_time:<20.3f}")
        print(f"{'Median Request Time (s)':<30} {pooling_metrics.median_request_time:<20.3f} {non_pooling_metrics.median_request_time:<20.3f}")
        print(f"{'Std Deviation (s)':<30} {pooling_metrics.std_deviation:<20.3f} {non_pooling_metrics.std_deviation:<20.3f}")
        print(f"{'Connection Creations':<30} {pooling_metrics.connection_creation_count:<20} {non_pooling_metrics.connection_creation_count:<20}")
        print(f"{'Connection Reuses':<30} {pooling_metrics.connection_reuse_count:<20} {non_pooling_metrics.connection_reuse_count:<20}")
        print(f"{'Requests/Second':<30} {analysis['throughput_improvement']['requests_per_second_pooling']:<20.1f} {analysis['throughput_improvement']['requests_per_second_non_pooling']:<20.1f}")
        
        print(f"\n🎯 Key Improvements:")
        print(f"   • Total time reduction: {analysis['total_time_improvement']['absolute']:.3f}s ({analysis['total_time_improvement']['percentage']:.1f}%)")
        print(f"   • Average request time reduction: {analysis['avg_request_time_improvement']['absolute']:.3f}s ({analysis['avg_request_time_improvement']['percentage']:.1f}%)")
        print(f"   • Connection creation reduction: {analysis['connection_efficiency']['creation_reduction']}")
        print(f"   • Connection reuse benefit: {analysis['connection_efficiency']['reuse_benefit']}")
        print(f"   • Throughput improvement factor: {analysis['throughput_improvement']['improvement_factor']:.2f}x")
        
        print(f"\n💡 Efficiency Analysis:")
        print(f"   • Connection efficiency ratio: {analysis['connection_efficiency']['efficiency_ratio']:.2f}")
        print(f"   • Pooling reduces connection overhead by: {analysis['connection_efficiency']['creation_reduction']} connections")
        print(f"   • Each connection is reused {analysis['connection_efficiency']['reuse_benefit']} times on average")
    
    def print_provider_results(self, provider_results: Dict[str, PoolingMetrics]):
        """Print provider-specific performance results"""
        if not provider_results:
            return
        
        print(f"\n🏭 PROVIDER PERFORMANCE RESULTS")
        print("="*60)
        
        for provider_name, metrics in provider_results.items():
            print(f"\n📊 {provider_name.replace('_', ' ').title()}:")
            print(f"   • Total time: {metrics.total_time:.3f}s")
            print(f"   • Request count: {metrics.request_count}")
            print(f"   • Average request time: {metrics.avg_request_time:.3f}s")
            print(f"   • Min/Max request time: {metrics.min_request_time:.3f}s / {metrics.max_request_time:.3f}s")
            print(f"   • Connection reuses: {metrics.connection_reuse_count}")
            print(f"   • Requests per second: {metrics.request_count / metrics.total_time:.1f}")
    
    async def run_comparison(self) -> Dict[str, Any]:
        """Run the complete performance comparison"""
        logger.info("🚀 Starting connection pooling performance comparison...")
        
        try:
            # Test with and without pooling
            pooling_metrics = await self.test_with_pooling()
            non_pooling_metrics = await self.test_without_pooling()
            
            # Analyze results
            analysis = self.analyze_comparison(pooling_metrics, non_pooling_metrics)
            
            # Test provider performance
            provider_results = await self.test_provider_performance()
            
            # Print results
            self.print_comparison(pooling_metrics, non_pooling_metrics, analysis)
            self.print_provider_results(provider_results)
            
            # Prepare results for saving
            results = {
                'timestamp': datetime.now().isoformat(),
                'test_configuration': {
                    'request_count': self.request_count,
                    'concurrent_requests': self.concurrent_requests,
                    'test_url': self.test_url
                },
                'pooling_metrics': {
                    'approach': pooling_metrics.approach,
                    'total_time': pooling_metrics.total_time,
                    'request_count': pooling_metrics.request_count,
                    'avg_request_time': pooling_metrics.avg_request_time,
                    'min_request_time': pooling_metrics.min_request_time,
                    'max_request_time': pooling_metrics.max_request_time,
                    'median_request_time': pooling_metrics.median_request_time,
                    'std_deviation': pooling_metrics.std_deviation,
                    'connection_creation_count': pooling_metrics.connection_creation_count,
                    'connection_reuse_count': pooling_metrics.connection_reuse_count
                },
                'non_pooling_metrics': {
                    'approach': non_pooling_metrics.approach,
                    'total_time': non_pooling_metrics.total_time,
                    'request_count': non_pooling_metrics.request_count,
                    'avg_request_time': non_pooling_metrics.avg_request_time,
                    'min_request_time': non_pooling_metrics.min_request_time,
                    'max_request_time': non_pooling_metrics.max_request_time,
                    'median_request_time': non_pooling_metrics.median_request_time,
                    'std_deviation': non_pooling_metrics.std_deviation,
                    'connection_creation_count': non_pooling_metrics.connection_creation_count,
                    'connection_reuse_count': non_pooling_metrics.connection_reuse_count
                },
                'analysis': analysis,
                'provider_results': {
                    name: {
                        'approach': metrics.approach,
                        'total_time': metrics.total_time,
                        'request_count': metrics.request_count,
                        'avg_request_time': metrics.avg_request_time,
                        'min_request_time': metrics.min_request_time,
                        'max_request_time': metrics.max_request_time,
                        'median_request_time': metrics.median_request_time,
                        'std_deviation': metrics.std_deviation,
                        'connection_creation_count': metrics.connection_creation_count,
                        'connection_reuse_count': metrics.connection_reuse_count
                    }
                    for name, metrics in provider_results.items()
                }
            }
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scripts/reports/performance/connection_pooling_performance_{timestamp}.json"
            
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"📊 Results saved to {filename}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Performance comparison failed: {e}")
            raise
        finally:
            # Cleanup
            await self.service_locator.cleanup()

async def main():
    """Main function"""
    print("🔗 Connection Pooling Performance Comparison")
    print("="*60)
    
    try:
        test = ConnectionPoolingPerformanceTest()
        results = await test.run_comparison()
        
        print(f"\n✅ Performance comparison completed successfully!")
        print(f"📊 Results saved to reports/performance/")
        
    except Exception as e:
        print(f"❌ Performance comparison failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
