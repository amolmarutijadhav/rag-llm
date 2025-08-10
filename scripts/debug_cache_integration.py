#!/usr/bin/env python3
"""
Debug Cache Integration for Enhanced Chat Completion Service

This script helps debug the cache integration issues identified in the performance tests.
It tests individual components to isolate the problems.
"""
import asyncio
import json
import time
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.cache_service import cache_service, InMemoryCache
from app.domain.models.requests import ChatCompletionRequest, ChatMessage
from app.domain.services.enhanced_chat_completion_service import EnhancedChatCompletionService
from app.domain.services.rag_service import RAGService
from app.infrastructure.providers.service_locator import ServiceLocator

async def test_cache_service_basic():
    """Test basic cache service functionality"""
    print("🔍 Testing basic cache service functionality...")
    
    # Test basic cache operations
    test_key = "test_embedding_key"
    test_value = [0.1, 0.2, 0.3, 0.4, 0.5]
    
    # Test set
    result = await cache_service.set_embedding("test_query", test_value)
    print(f"✅ Set embedding result: {result}")
    
    # Test get
    retrieved = await cache_service.get_embedding("test_query")
    print(f"✅ Retrieved embedding: {retrieved}")
    print(f"✅ Values match: {retrieved == test_value}")
    
    # Test cache stats
    stats = await cache_service.get_all_stats()
    print(f"✅ Cache stats: {json.dumps(stats, indent=2)}")

async def test_cache_key_generation():
    """Test cache key generation consistency"""
    print("\n🔍 Testing cache key generation...")
    
    # Test embedding cache key generation
    query1 = "What are the key requirements for a business requirements document?"
    query2 = "What are the key requirements for a business requirements document?"  # Same query
    
    # Get keys
    key1 = cache_service.embedding_cache._generate_key(query1)
    key2 = cache_service.embedding_cache._generate_key(query2)
    
    print(f"✅ Query 1 key: {key1}")
    print(f"✅ Query 2 key: {key2}")
    print(f"✅ Keys match: {key1 == key2}")
    
    # Test search cache key generation
    vector1 = [0.1, 0.2, 0.3]
    vector2 = [0.1, 0.2, 0.3]  # Same vector
    
    search_key1 = cache_service.search_cache._generate_key(vector1, 5, "test_collection")
    search_key2 = cache_service.search_cache._generate_key(vector2, 5, "test_collection")
    
    print(f"✅ Search key 1: {search_key1}")
    print(f"✅ Search key 2: {search_key2}")
    print(f"✅ Search keys match: {search_key1 == search_key2}")

async def test_enhanced_service_cache_integration():
    """Test cache integration in enhanced service"""
    print("\n🔍 Testing enhanced service cache integration...")
    
    try:
        # Initialize services
        service_locator = ServiceLocator()
        service_locator.initialize_providers()
        embedding_provider = service_locator.get_embedding_provider()
        llm_provider = service_locator.get_llm_provider()
        vector_store_provider = service_locator.get_vector_store_provider()
        rag_service = RAGService(embedding_provider, llm_provider, vector_store_provider)
        enhanced_service = EnhancedChatCompletionService(rag_service, llm_provider)
        
        # Create test request
        test_request = ChatCompletionRequest(
            messages=[
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content="What are the key requirements for a business requirements document?")
            ],
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        print("✅ Services initialized successfully")
        
        # Clear cache before test
        await cache_service.clear_all()
        print("✅ Cache cleared")
        
        # Get initial cache stats
        initial_stats = await cache_service.get_all_stats()
        print(f"✅ Initial cache stats: {json.dumps(initial_stats, indent=2)}")
        
        # Process request
        print("🔄 Processing request...")
        start_time = time.time()
        response = await enhanced_service.process_request(test_request)
        end_time = time.time()
        
        print(f"✅ Request processed in {end_time - start_time:.2f}s")
        print(f"✅ Response received: {response['choices'][0]['message']['content'][:100] if isinstance(response, dict) else 'Response object'}...")
        
        # Get final cache stats
        final_stats = await cache_service.get_all_stats()
        print(f"✅ Final cache stats: {json.dumps(final_stats, indent=2)}")
        
        # Check if cache was used
        embedding_cache_entries = final_stats.get('embedding_cache', {}).get('total_entries', 0)
        search_cache_entries = final_stats.get('search_cache', {}).get('total_entries', 0)
        
        print(f"✅ Embedding cache entries: {embedding_cache_entries}")
        print(f"✅ Search cache entries: {search_cache_entries}")
        
        if embedding_cache_entries > 0 or search_cache_entries > 0:
            print("✅ Cache integration is working!")
        else:
            print("❌ Cache integration is NOT working - no entries found")
            
    except Exception as e:
        print(f"❌ Error testing enhanced service: {e}")
        import traceback
        traceback.print_exc()

async def test_plugin_manager():
    """Test plugin manager functionality"""
    print("\n🔍 Testing plugin manager...")
    
    try:
        # Initialize services
        service_locator = ServiceLocator()
        service_locator.initialize_providers()
        embedding_provider = service_locator.get_embedding_provider()
        llm_provider = service_locator.get_llm_provider()
        vector_store_provider = service_locator.get_vector_store_provider()
        rag_service = RAGService(embedding_provider, llm_provider, vector_store_provider)
        
        # Test plugin manager initialization
        from app.domain.services.enhanced_chat_completion_service import ChatCompletionPluginManager, ConversationContextPlugin, MultiQueryRAGPlugin, ResponseEnhancementPlugin, ConversationStrategyFactory
        
        strategy_factory = ConversationStrategyFactory()
        plugin_manager = ChatCompletionPluginManager()
        
        # Register plugins
        plugin_manager.register_plugin(ConversationContextPlugin(strategy_factory))
        plugin_manager.register_plugin(MultiQueryRAGPlugin(rag_service))
        plugin_manager.register_plugin(ResponseEnhancementPlugin(llm_provider))
        
        print("✅ Plugin manager initialized successfully")
        print(f"✅ Registered plugins: {len(plugin_manager.plugins)}")
        
        # Test plugin processing
        test_request = ChatCompletionRequest(
            messages=[
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content="What are the key requirements for a business requirements document?")
            ],
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        from app.domain.services.enhanced_chat_completion_service import ProcessingContext
        context = ProcessingContext(request=test_request)
        
        print("🔄 Testing plugin processing...")
        result_context = await plugin_manager.process_request(context)
        
        print("✅ Plugin processing completed")
        print(f"✅ Enhanced queries: {len(result_context.enhanced_queries) if result_context.enhanced_queries else 0}")
        print(f"✅ RAG results: {len(result_context.rag_results) if result_context.rag_results else 0}")
        
    except Exception as e:
        print(f"❌ Error testing plugin manager: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main debug function"""
    print("🚀 Starting Cache Integration Debug")
    print("=" * 50)
    
    # Test 1: Basic cache service
    await test_cache_service_basic()
    
    # Test 2: Cache key generation
    await test_cache_key_generation()
    
    # Test 3: Plugin manager
    await test_plugin_manager()
    
    # Test 4: Enhanced service cache integration
    await test_enhanced_service_cache_integration()
    
    print("\n" + "=" * 50)
    print("🏁 Cache Integration Debug Complete")

if __name__ == "__main__":
    asyncio.run(main())
