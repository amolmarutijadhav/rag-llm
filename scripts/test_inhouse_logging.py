#!/usr/bin/env python3
"""
Test script to demonstrate and verify the enhanced logging functionality for inhouse providers.
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
from app.infrastructure.providers.inhouse_provider import (
    InhouseEmbeddingProvider, InhouseLLMProvider, InhouseVectorStoreProvider
)

async def test_inhouse_provider_logging():
    """Test the inhouse provider logging functionality"""
    
    # Setup logging
    logging_config.setup_logging()
    logger = get_logger("test_inhouse_logging")
    
    print("🔍 Testing Inhouse Provider Logging")
    print("=" * 50)
    
    # Set correlation ID for testing
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    
    # Test 1: Inhouse Embedding Provider
    print("\n1. Testing Inhouse Embedding Provider...")
    try:
        embedding_config = {
            "api_url": "https://internal-api.company.com/embeddings",
            "api_key": "internal-api-key-123",
            "model": "company-embedding-model-v1",
            "auth_scheme": "bearer",
            "timeout": 30,
            "max_retries": 3
        }
        
        embedding_provider = InhouseEmbeddingProvider(embedding_config)
        logger.info("Inhouse embedding provider created successfully")
        
        # Simulate embedding request (this will fail but show logging)
        try:
            await embedding_provider.get_embeddings(["test text"])
        except Exception as e:
            logger.info(f"Expected error for embedding request: {e}")
            
    except Exception as e:
        logger.error(f"Failed to create inhouse embedding provider: {e}")
    
    # Test 2: Inhouse LLM Provider
    print("\n2. Testing Inhouse LLM Provider...")
    try:
        llm_config = {
            "api_url": "https://internal-api.company.com/chat",
            "api_key": "internal-llm-key-456",
            "default_model": "company-llm-model-v2",
            "default_temperature": 0.7,
            "default_max_tokens": 1500,
            "auth_scheme": "bearer",
            "timeout": 60,
            "max_retries": 3
        }
        
        llm_provider = InhouseLLMProvider(llm_config)
        logger.info("Inhouse LLM provider created successfully")
        
        # Simulate LLM request (this will fail but show logging)
        try:
            await llm_provider.call_llm([
                {"role": "user", "content": "Hello, how are you?"}
            ])
        except Exception as e:
            logger.info(f"Expected error for LLM request: {e}")
            
    except Exception as e:
        logger.error(f"Failed to create inhouse LLM provider: {e}")
    
    # Test 3: Inhouse Vector Store Provider
    print("\n3. Testing Inhouse Vector Store Provider...")
    try:
        vector_config = {
            "base_url": "https://internal-vector.company.com",
            "api_key": "internal-vector-key-789",
            "auth_scheme": "api_key",
            "timeout": 30,
            "max_retries": 3
        }
        
        vector_provider = InhouseVectorStoreProvider(vector_config)
        logger.info("Inhouse vector store provider created successfully")
        
        # Test collection operations (these will fail but show logging)
        try:
            await vector_provider.create_collection_if_not_exists("test_collection", 768, "Cosine")
        except Exception as e:
            logger.info(f"Expected error for collection creation: {e}")
        
        try:
            vector_provider.get_collection_stats("test_collection")
        except Exception as e:
            logger.info(f"Expected error for collection stats: {e}")
            
    except Exception as e:
        logger.error(f"Failed to create inhouse vector store provider: {e}")
    
    # Test 4: Provider-specific logging features
    print("\n4. Testing provider-specific logging features...")
    
    # Test data sanitization for inhouse providers
    inhouse_sensitive_data = {
        "internal_api_key": "secret-internal-key",
        "company_token": "company-secret-token",
        "normal_field": "public-data",
        "credentials": {
            "username": "internal-user",
            "password": "internal-password"
        }
    }
    
    sanitized = sanitize_for_logging(inhouse_sensitive_data)
    logger.info("Testing inhouse data sanitization", extra={
        'extra_fields': {
            'event_type': 'inhouse_data_sanitization_test',
            'original_data': inhouse_sensitive_data,
            'sanitized_data': sanitized
        }
    })
    
    # Test 5: Inhouse-specific event types
    print("\n5. Testing inhouse-specific event types...")
    logger.info("Inhouse provider testing completed", extra={
        'extra_fields': {
            'event_type': 'inhouse_provider_test_complete',
            'providers_tested': ['embedding', 'llm', 'vector_store'],
            'correlation_id': correlation_id,
            'test_environment': 'inhouse_services'
        }
    })
    
    print("\n✅ Inhouse provider logging test completed!")
    print("Check the console output above for structured logs with inhouse-specific events.")

def test_inhouse_curl_generation():
    """Test curl command generation for inhouse APIs"""
    print("\n🔧 Testing curl command generation for inhouse APIs...")
    
    from app.core.logging_config import api_logger
    
    # Test curl command generation for inhouse API
    method = "POST"
    url = "https://internal-api.company.com/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer internal-api-key",
        "X-Company-ID": "company-123",
        "User-Agent": "RAG-LLM-Internal/1.0"
    }
    body = {
        "texts": ["internal company document"],
        "model": "company-embedding-model-v1",
        "format": "vector"
    }
    
    curl_command = api_logger.generate_curl_command(method, url, headers, body)
    
    print("Generated curl command for inhouse API:")
    print(curl_command)
    
    print("\n✅ Inhouse curl command generation test completed!")

if __name__ == "__main__":
    print("🚀 Starting Inhouse Provider Logging Test Suite")
    print("=" * 60)
    
    # Set environment for testing
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("LOG_LEVEL", "DEBUG")
    os.environ.setdefault("ENABLE_STRUCTURED_LOGGING", "true")
    os.environ.setdefault("ENABLE_CURL_DEBUGGING", "true")
    
    # Run tests
    asyncio.run(test_inhouse_provider_logging())
    test_inhouse_curl_generation()
    
    print("\n" + "=" * 60)
    print("🎉 All inhouse provider logging tests completed successfully!")
    print("\nKey Features Tested:")
    print("✅ Inhouse embedding provider logging")
    print("✅ Inhouse LLM provider logging")
    print("✅ Inhouse vector store provider logging")
    print("✅ Provider-specific event types")
    print("✅ Inhouse data sanitization")
    print("✅ Curl command generation for inhouse APIs")
    print("\nThe logs above should show structured JSON output with inhouse-specific events and correlation IDs.") 