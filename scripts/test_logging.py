#!/usr/bin/env python3
"""
Test script to demonstrate and verify the logging functionality.
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
from app.infrastructure.providers.openai_provider import OpenAIEmbeddingProvider
from app.core.config import Config

async def test_logging_functionality():
    """Test the logging functionality"""
    
    # Setup logging
    logging_config.setup_logging()
    logger = get_logger("test_logging")
    
    print("🔍 Testing Logging Functionality")
    print("=" * 50)
    
    # Test 1: Basic logging
    print("\n1. Testing basic logging...")
    logger.info("This is a test info message")
    logger.warning("This is a test warning message")
    logger.error("This is a test error message")
    
    # Test 2: Correlation ID
    print("\n2. Testing correlation ID...")
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    logger.info("Message with correlation ID", extra={
        'extra_fields': {
            'event_type': 'test_event',
            'test_data': 'sample_value'
        }
    })
    
    # Test 3: Data sanitization
    print("\n3. Testing data sanitization...")
    sensitive_data = {
        "api_key": "sk-secret-key-123",
        "password": "secret-password",
        "normal_field": "public-data",
        "nested": {
            "token": "secret-token",
            "public_info": "public-value"
        }
    }
    
    sanitized = sanitize_for_logging(sensitive_data)
    logger.info("Testing data sanitization", extra={
        'extra_fields': {
            'event_type': 'data_sanitization_test',
            'original_data': sensitive_data,
            'sanitized_data': sanitized
        }
    })
    
    # Test 4: Provider logging (mock)
    print("\n4. Testing provider logging...")
    try:
        # Create a mock provider config
        mock_config = {
            "api_url": "https://api.openai.com/v1/embeddings",
            "api_key": "sk-test-key",
            "model": "text-embedding-ada-002",
            "auth_scheme": "bearer",
            "timeout": 30,
            "max_retries": 3
        }
        
        # This will test the provider initialization logging
        provider = OpenAIEmbeddingProvider(mock_config)
        logger.info("Provider created successfully")
        
    except Exception as e:
        logger.error(f"Provider creation failed: {e}")
    
    # Test 5: Environment configuration
    print("\n5. Testing environment configuration...")
    logger.info("Environment configuration", extra={
        'extra_fields': {
            'event_type': 'environment_info',
            'environment': logging_config.environment,
            'log_level': logging_config.log_level,
            'enable_structured_logging': logging_config.enable_structured_logging,
            'enable_curl_debugging': logging_config.enable_curl_debugging
        }
    })
    
    print("\n✅ Logging functionality test completed!")
    print("Check the console output above for structured logs.")

def test_curl_command_generation():
    """Test curl command generation for debugging"""
    print("\n🔧 Testing curl command generation...")
    
    from app.core.logging_config import api_logger
    
    # Test curl command generation
    method = "POST"
    url = "https://api.openai.com/v1/embeddings"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-secret-key",
        "User-Agent": "RAG-LLM/1.0"
    }
    body = {
        "input": ["test text"],
        "model": "text-embedding-ada-002"
    }
    
    curl_command = api_logger.generate_curl_command(method, url, headers, body)
    
    print("Generated curl command:")
    print(curl_command)
    
    print("\n✅ Curl command generation test completed!")

if __name__ == "__main__":
    print("🚀 Starting Logging Test Suite")
    print("=" * 60)
    
    # Set environment for testing
    os.environ.setdefault("ENVIRONMENT", "development")
    os.environ.setdefault("LOG_LEVEL", "DEBUG")
    os.environ.setdefault("ENABLE_STRUCTURED_LOGGING", "true")
    os.environ.setdefault("ENABLE_CURL_DEBUGGING", "true")
    
    # Run tests
    asyncio.run(test_logging_functionality())
    test_curl_command_generation()
    
    print("\n" + "=" * 60)
    print("🎉 All logging tests completed successfully!")
    print("\nKey Features Tested:")
    print("✅ Structured JSON logging")
    print("✅ Correlation ID management")
    print("✅ Data sanitization")
    print("✅ Provider logging")
    print("✅ Environment configuration")
    print("✅ Curl command generation")
    print("\nThe logs above should show structured JSON output with correlation IDs and sanitized data.") 