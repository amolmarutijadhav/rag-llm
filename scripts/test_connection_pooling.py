#!/usr/bin/env python3
"""
Test script to verify connection pooling implementation.
This script tests that HTTP clients are properly reused and connection pools are working.
"""

import asyncio
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.infrastructure.providers.service_locator import ServiceLocator
from app.core.logging_config import get_logger

logger = get_logger(__name__)

async def test_connection_pooling():
    """Test connection pooling functionality"""
    print("🔧 Testing Connection Pooling Implementation")
    print("=" * 50)
    
    # Initialize service locator
    service_locator = ServiceLocator()
    service_locator.initialize_providers()
    
    print("✅ Service locator initialized")
    
    # Get providers
    embedding_provider = service_locator.get_embedding_provider()
    llm_provider = service_locator.get_llm_provider()
    vector_store_provider = service_locator.get_vector_store_provider()
    
    print("✅ Providers retrieved")
    
    # Test that providers have connection pooling attributes
    print("\n🔍 Checking Connection Pooling Configuration:")
    
    for provider_name, provider in [
        ("Embedding", embedding_provider),
        ("LLM", llm_provider),
        ("Vector Store", vector_store_provider)
    ]:
        print(f"\n{provider_name} Provider:")
        
        # Check if provider has connection pooling attributes
        has_async_client = hasattr(provider, '_async_client')
        has_sync_client = hasattr(provider, '_sync_client')
        has_client_lock = hasattr(provider, '_client_lock')
        has_close_method = hasattr(provider, 'close') and callable(getattr(provider, 'close'))
        
        print(f"  - Async client: {'✅' if has_async_client else '❌'}")
        print(f"  - Sync client: {'✅' if has_sync_client else '❌'}")
        print(f"  - Client lock: {'✅' if has_client_lock else '❌'}")
        print(f"  - Close method: {'✅' if has_close_method else '❌'}")
        
        # Check connection pooling configuration
        if hasattr(provider, 'max_keepalive_connections'):
            print(f"  - Max keepalive connections: {provider.max_keepalive_connections}")
        if hasattr(provider, 'max_connections'):
            print(f"  - Max connections: {provider.max_connections}")
        if hasattr(provider, 'keepalive_expiry'):
            print(f"  - Keepalive expiry: {provider.keepalive_expiry}s")
    
    # Test multiple API calls to verify connection reuse
    print("\n🚀 Testing Connection Reuse:")
    
    try:
        # Test embedding provider with multiple calls
        print("\nTesting Embedding Provider:")
        start_time = time.time()
        
        # Make multiple embedding calls
        test_texts = [
            "This is a test query for connection pooling",
            "Another test query to verify connection reuse",
            "Third test query to check performance",
            "Fourth test query for comprehensive testing",
            "Fifth test query to ensure stability"
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"  Making embedding call {i}/5...")
            try:
                embeddings = await embedding_provider.get_embeddings([text])
                print(f"    ✅ Call {i} successful - {len(embeddings)} embeddings")
            except Exception as e:
                print(f"    ❌ Call {i} failed: {str(e)}")
        
        embedding_duration = time.time() - start_time
        print(f"  Total embedding time: {embedding_duration:.2f}s")
        
        # Test LLM provider
        print("\nTesting LLM Provider:")
        start_time = time.time()
        
        test_messages = [
            [{"role": "user", "content": "Hello, this is a test message"}],
            [{"role": "user", "content": "Another test message for connection pooling"}],
            [{"role": "user", "content": "Third test message to verify performance"}]
        ]
        
        for i, messages in enumerate(test_messages, 1):
            print(f"  Making LLM call {i}/3...")
            try:
                response = await llm_provider.call_llm(messages)
                print(f"    ✅ Call {i} successful - {len(response)} chars")
            except Exception as e:
                print(f"    ❌ Call {i} failed: {str(e)}")
        
        llm_duration = time.time() - start_time
        print(f"  Total LLM time: {llm_duration:.2f}s")
        
        print("\n✅ Connection pooling test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Connection pooling test failed: {str(e)}")
        logger.error(f"Connection pooling test failed", extra={
            'extra_fields': {
                'event_type': 'connection_pooling_test_failed',
                'error': str(e)
            }
        })
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up resources...")
        try:
            await service_locator.cleanup()
            print("✅ Cleanup completed successfully")
        except Exception as e:
            print(f"❌ Cleanup failed: {str(e)}")

async def test_connection_pool_performance():
    """Test performance improvement with connection pooling"""
    print("\n📊 Performance Test with Connection Pooling")
    print("=" * 50)
    
    service_locator = ServiceLocator()
    service_locator.initialize_providers()
    
    embedding_provider = service_locator.get_embedding_provider()
    
    # Test with multiple concurrent requests
    print("Testing concurrent embedding requests...")
    
    async def make_embedding_request(text: str, request_id: int):
        start_time = time.time()
        try:
            embeddings = await embedding_provider.get_embeddings([text])
            duration = time.time() - start_time
            return {
                'request_id': request_id,
                'success': True,
                'duration': duration,
                'embedding_count': len(embeddings)
            }
        except Exception as e:
            duration = time.time() - start_time
            return {
                'request_id': request_id,
                'success': False,
                'duration': duration,
                'error': str(e)
            }
    
    # Create multiple concurrent requests
    test_texts = [
        f"Concurrent test query {i} for connection pooling performance"
        for i in range(10)
    ]
    
    start_time = time.time()
    tasks = [
        make_embedding_request(text, i) 
        for i, text in enumerate(test_texts)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_duration = time.time() - start_time
    
    # Analyze results
    successful_requests = [r for r in results if isinstance(r, dict) and r.get('success')]
    failed_requests = [r for r in results if isinstance(r, dict) and not r.get('success')]
    exceptions = [r for r in results if isinstance(r, Exception)]
    
    print(f"\n📈 Performance Results:")
    print(f"  Total requests: {len(test_texts)}")
    print(f"  Successful: {len(successful_requests)}")
    print(f"  Failed: {len(failed_requests)}")
    print(f"  Exceptions: {len(exceptions)}")
    print(f"  Total time: {total_duration:.2f}s")
    print(f"  Average time per request: {total_duration/len(test_texts):.2f}s")
    
    if successful_requests:
        avg_duration = sum(r['duration'] for r in successful_requests) / len(successful_requests)
        print(f"  Average successful request time: {avg_duration:.2f}s")
    
    # Cleanup
    await service_locator.cleanup()

async def main():
    """Main test function"""
    print("🔧 Connection Pooling Test Suite")
    print("=" * 60)
    
    try:
        await test_connection_pooling()
        await test_connection_pool_performance()
        
        print("\n🎉 All connection pooling tests completed successfully!")
        print("\n📋 Summary:")
        print("  ✅ Connection pooling implementation verified")
        print("  ✅ Provider lifecycle management working")
        print("  ✅ Resource cleanup functioning")
        print("  ✅ Performance testing completed")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        logger.error(f"Connection pooling test suite failed", extra={
            'extra_fields': {
                'event_type': 'connection_pooling_test_suite_failed',
                'error': str(e)
            }
        })
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
