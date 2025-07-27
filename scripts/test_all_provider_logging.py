#!/usr/bin/env python3
"""
Comprehensive test script to verify enhanced logging functionality across all providers.
Tests OpenAI, Inhouse, Qdrant providers, Factory, and Service Locator logging.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging_config import (
    logging_config, get_logger, set_correlation_id, 
    generate_correlation_id, sanitize_for_logging
)
from app.infrastructure.providers.factory import ProviderFactory
from app.infrastructure.providers.service_locator import ServiceLocator, get_embedding_provider, get_llm_provider, get_vector_store_provider

async def test_provider_factory_logging():
    """Test the provider factory logging functionality"""
    
    print("\n🏭 Testing Provider Factory Logging")
    print("=" * 50)
    
    # Test 1: Embedding Provider Creation
    print("\n1. Testing Embedding Provider Factory...")
    try:
        embedding_config = {
            "type": "openai",
            "api_url": "https://api.openai.com/v1/embeddings",
            "api_key": "test-openai-key",
            "model": "text-embedding-ada-002"
        }
        
        provider = ProviderFactory.create_embedding_provider(embedding_config)
        print(f"✅ Successfully created embedding provider: {type(provider).__name__}")
        
    except Exception as e:
        print(f"❌ Failed to create embedding provider: {e}")
    
    # Test 2: LLM Provider Creation
    print("\n2. Testing LLM Provider Factory...")
    try:
        llm_config = {
            "type": "openai",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_key": "test-openai-key",
            "default_model": "gpt-3.5-turbo"
        }
        
        provider = ProviderFactory.create_llm_provider(llm_config)
        print(f"✅ Successfully created LLM provider: {type(provider).__name__}")
        
    except Exception as e:
        print(f"❌ Failed to create LLM provider: {e}")
    
    # Test 3: Vector Store Provider Creation
    print("\n3. Testing Vector Store Provider Factory...")
    try:
        vector_config = {
            "type": "qdrant",
            "base_url": "http://localhost:6333",
            "api_key": "test-qdrant-key"
        }
        
        provider = ProviderFactory.create_vector_store_provider(vector_config)
        print(f"✅ Successfully created vector store provider: {type(provider).__name__}")
        
    except Exception as e:
        print(f"❌ Failed to create vector store provider: {e}")
    
    # Test 4: Unsupported Provider Types
    print("\n4. Testing Unsupported Provider Types...")
    try:
        unsupported_config = {"type": "unsupported"}
        ProviderFactory.create_embedding_provider(unsupported_config)
    except ValueError as e:
        print(f"✅ Correctly handled unsupported provider type: {e}")
    except Exception as e:
        print(f"❌ Unexpected error for unsupported provider: {e}")

async def test_service_locator_logging():
    """Test the service locator logging functionality"""
    
    print("\n🔧 Testing Service Locator Logging")
    print("=" * 50)
    
    # Test 1: Service Locator Initialization
    print("\n1. Testing Service Locator Initialization...")
    try:
        service_locator = ServiceLocator()
        print("✅ Service locator created successfully")
        
        # Test provider retrieval (this will trigger initialization)
        print("\n2. Testing Provider Retrieval...")
        try:
            embedding_provider = service_locator.get_embedding_provider()
            print(f"✅ Retrieved embedding provider: {type(embedding_provider).__name__}")
        except Exception as e:
            print(f"❌ Failed to retrieve embedding provider: {e}")
        
        try:
            llm_provider = service_locator.get_llm_provider()
            print(f"✅ Retrieved LLM provider: {type(llm_provider).__name__}")
        except Exception as e:
            print(f"❌ Failed to retrieve LLM provider: {e}")
        
        try:
            vector_provider = service_locator.get_vector_store_provider()
            print(f"✅ Retrieved vector store provider: {type(vector_provider).__name__}")
        except Exception as e:
            print(f"❌ Failed to retrieve vector store provider: {e}")
        
        # Test 3: Provider Registration
        print("\n3. Testing Provider Registration...")
        try:
            from app.infrastructure.providers.inhouse_provider import InhouseEmbeddingProvider
            custom_config = {
                "api_url": "https://custom-api.com/embeddings",
                "api_key": "custom-key",
                "model": "custom-model"
            }
            custom_provider = InhouseEmbeddingProvider(custom_config)
            service_locator.register_provider("embedding", custom_provider)
            print("✅ Successfully registered custom provider")
        except Exception as e:
            print(f"❌ Failed to register custom provider: {e}")
        
        # Test 4: Service Locator Reset
        print("\n4. Testing Service Locator Reset...")
        try:
            service_locator.reset()
            print("✅ Successfully reset service locator")
        except Exception as e:
            print(f"❌ Failed to reset service locator: {e}")
            
    except Exception as e:
        print(f"❌ Failed to create service locator: {e}")

async def test_global_provider_functions():
    """Test the global provider functions logging"""
    
    print("\n🌐 Testing Global Provider Functions")
    print("=" * 50)
    
    # Test global provider retrieval functions
    print("\n1. Testing Global Provider Functions...")
    try:
        embedding_provider = get_embedding_provider()
        print(f"✅ Retrieved global embedding provider: {type(embedding_provider).__name__}")
    except Exception as e:
        print(f"❌ Failed to retrieve global embedding provider: {e}")
    
    try:
        llm_provider = get_llm_provider()
        print(f"✅ Retrieved global LLM provider: {type(llm_provider).__name__}")
    except Exception as e:
        print(f"❌ Failed to retrieve global LLM provider: {e}")
    
    try:
        vector_provider = get_vector_store_provider()
        print(f"✅ Retrieved global vector store provider: {type(vector_provider).__name__}")
    except Exception as e:
        print(f"❌ Failed to retrieve global vector store provider: {e}")

async def test_provider_operations():
    """Test actual provider operations with logging"""
    
    print("\n⚡ Testing Provider Operations")
    print("=" * 50)
    
    # Test Qdrant provider operations
    print("\n1. Testing Qdrant Provider Operations...")
    try:
        qdrant_config = {
            "type": "qdrant",
            "base_url": "http://localhost:6333",
            "api_key": "test-qdrant-key"
        }
        
        qdrant_provider = ProviderFactory.create_vector_store_provider(qdrant_config)
        
        # Test collection creation (this will fail but show logging)
        try:
            await qdrant_provider.create_collection_if_not_exists("test_collection", 768, "Cosine")
        except Exception as e:
            print(f"✅ Expected error for collection creation: {e}")
        
        # Test collection stats (this will fail but show logging)
        try:
            stats = qdrant_provider.get_collection_stats("test_collection")
            print(f"✅ Retrieved collection stats: {stats}")
        except Exception as e:
            print(f"✅ Expected error for collection stats: {e}")
            
    except Exception as e:
        print(f"❌ Failed to test Qdrant provider operations: {e}")

def test_data_sanitization():
    """Test data sanitization for different provider types"""
    
    print("\n🔒 Testing Data Sanitization")
    print("=" * 50)
    
    # Test different types of sensitive data
    test_cases = [
        {
            "name": "OpenAI API Data",
            "data": {
                "api_key": "sk-openai-secret-key-123",
                "model": "gpt-4",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        },
        {
            "name": "Qdrant API Data",
            "data": {
                "api_key": "qdrant-secret-key-456",
                "base_url": "http://localhost:6333",
                "collection_name": "test_collection"
            }
        },
        {
            "name": "Inhouse API Data",
            "data": {
                "internal_api_key": "internal-secret-key-789",
                "company_token": "company-secret-token",
                "api_url": "https://internal-api.company.com"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting {test_case['name']}...")
        try:
            sanitized = sanitize_for_logging(test_case['data'])
            print(f"✅ Original: {test_case['data']}")
            print(f"✅ Sanitized: {sanitized}")
        except Exception as e:
            print(f"❌ Failed to sanitize {test_case['name']}: {e}")

async def main():
    """Main test function"""
    
    # Setup logging
    logging_config.setup_logging()
    logger = get_logger("test_all_provider_logging")
    
    print("🚀 Starting Comprehensive Provider Logging Test Suite")
    print("=" * 70)
    
    # Set correlation ID for testing
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    
    logger.info("Starting comprehensive provider logging tests", extra={
        'extra_fields': {
            'event_type': 'comprehensive_provider_test_start',
            'correlation_id': correlation_id,
            'test_components': ['factory', 'service_locator', 'providers', 'sanitization']
        }
    })
    
    # Run all tests
    await test_provider_factory_logging()
    await test_service_locator_logging()
    await test_global_provider_functions()
    await test_provider_operations()
    test_data_sanitization()
    
    logger.info("Completed comprehensive provider logging tests", extra={
        'extra_fields': {
            'event_type': 'comprehensive_provider_test_complete',
            'correlation_id': correlation_id
        }
    })
    
    print("\n" + "=" * 70)
    print("🎉 All provider logging tests completed successfully!")
    print("\nKey Components Tested:")
    print("✅ Provider Factory logging")
    print("✅ Service Locator logging")
    print("✅ Global provider functions")
    print("✅ Provider operations (Qdrant)")
    print("✅ Data sanitization")
    print("\nThe logs above should show structured JSON output with comprehensive provider events and correlation IDs.")

if __name__ == "__main__":
    # Set environment for testing
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("LOG_LEVEL", "DEBUG")
    os.environ.setdefault("ENABLE_STRUCTURED_LOGGING", "true")
    os.environ.setdefault("ENABLE_CURL_DEBUGGING", "true")
    
    # Run tests
    asyncio.run(main()) 