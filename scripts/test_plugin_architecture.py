#!/usr/bin/env python3
"""
Test script to validate the plugin architecture is working correctly.
This script tests the basic functionality of the new provider system.
"""

import asyncio
import os
import sys
from typing import Dict, Any

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.infrastructure.providers import ProviderFactory, ServiceLocator
from app.core.config import Config


async def test_provider_creation():
    """Test that providers can be created successfully."""
    print("🧪 Testing Provider Creation...")
    
    try:
        # Get configurations
        embedding_config = Config.get_embedding_provider_config()
        llm_config = Config.get_llm_provider_config()
        vector_store_config = Config.get_vector_store_provider_config()
        
        print(f"  📋 Embedding Provider Type: {embedding_config.get('type')}")
        print(f"  📋 LLM Provider Type: {llm_config.get('type')}")
        print(f"  📋 Vector Store Provider Type: {vector_store_config.get('type')}")
        
        # Create providers using factory
        embedding_provider = ProviderFactory.create_embedding_provider(embedding_config)
        llm_provider = ProviderFactory.create_llm_provider(llm_config)
        vector_store_provider = ProviderFactory.create_vector_store_provider(vector_store_config)
        
        print("  ✅ All providers created successfully!")
        
        # Test provider info methods
        embedding_info = embedding_provider.get_model_info()
        llm_info = llm_provider.get_model_info()
        
        print(f"  📊 Embedding Provider: {embedding_info.get('provider')} - {embedding_info.get('model')}")
        print(f"  📊 LLM Provider: {llm_info.get('provider')} - {llm_info.get('default_model')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error creating providers: {e}")
        return False


async def test_service_locator():
    """Test that the service locator works correctly."""
    print("\n🧪 Testing Service Locator...")
    
    try:
        # Create a new service locator instance
        service_locator = ServiceLocator()
        
        # Initialize providers
        service_locator.initialize_providers()
        
        # Get providers
        embedding_provider = service_locator.get_embedding_provider()
        llm_provider = service_locator.get_llm_provider()
        vector_store_provider = service_locator.get_vector_store_provider()
        
        print("  ✅ Service locator working correctly!")
        print(f"  📊 Retrieved {type(embedding_provider).__name__}")
        print(f"  📊 Retrieved {type(llm_provider).__name__}")
        print(f"  📊 Retrieved {type(vector_store_provider).__name__}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error with service locator: {e}")
        return False


async def test_rag_service_integration():
    """Test that RAG service can be initialized with new providers."""
    print("\n🧪 Testing RAG Service Integration...")
    
    try:
        from app.domain.services.rag_service import RAGService
        
        # Create RAG service (should use providers from service locator)
        rag_service = RAGService()
        
        print("  ✅ RAG service initialized successfully!")
        print(f"  📊 Using embedding provider: {type(rag_service.embedding_provider).__name__}")
        print(f"  📊 Using LLM provider: {type(rag_service.llm_provider).__name__}")
        print(f"  📊 Using vector store provider: {type(rag_service.vector_store_provider).__name__}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error initializing RAG service: {e}")
        return False


async def test_vector_store_integration():
    """Test that VectorStore can be initialized with new providers."""
    print("\n🧪 Testing VectorStore Integration...")
    
    try:
        from app.infrastructure.vector_store.vector_store import VectorStore
        
        # Create VectorStore (should use providers from service locator)
        vector_store = VectorStore()
        
        print("  ✅ VectorStore initialized successfully!")
        print(f"  📊 Using embedding provider: {type(vector_store.embedding_provider).__name__}")
        print(f"  📊 Using vector store provider: {type(vector_store.vector_store_provider).__name__}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error initializing VectorStore: {e}")
        return False


async def test_configuration():
    """Test that configuration is properly set up."""
    print("\n🧪 Testing Configuration...")
    
    try:
        # Test provider type configuration
        embedding_type = Config.PROVIDER_EMBEDDING_TYPE
        llm_type = Config.PROVIDER_LLM_TYPE
        vector_store_type = Config.PROVIDER_VECTOR_STORE_TYPE
        
        print(f"  📋 Provider Types:")
        print(f"    - Embedding: {embedding_type}")
        print(f"    - LLM: {llm_type}")
        print(f"    - Vector Store: {vector_store_type}")
        
        # Test that configuration methods work
        embedding_config = Config.get_embedding_provider_config()
        llm_config = Config.get_llm_provider_config()
        vector_store_config = Config.get_vector_store_provider_config()
        
        print("  ✅ Configuration methods working correctly!")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error with configuration: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Plugin Architecture Validation Test")
    print("=" * 50)
    
    tests = [
        test_configuration,
        test_provider_creation,
        test_service_locator,
        test_rag_service_integration,
        test_vector_store_integration
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(results)
    total = len(results)
    
    for i, result in enumerate(results):
        status = "✅ PASS" if result else "❌ FAIL"
        test_name = tests[i].__name__.replace('_', ' ').title()
        print(f"  {status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Plugin architecture is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the configuration and implementation.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 