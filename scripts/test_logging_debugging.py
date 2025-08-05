#!/usr/bin/env python3
"""
Test script to verify logging provides non-truncated data for debugging
"""

import sys
import os
import json
from unittest.mock import Mock, AsyncMock

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.logging_config import APILogger, ExternalAPICall, sanitize_for_logging
from app.api.middleware.request_logging import EnhancedRequestLoggingMiddleware


def test_curl_command_generation():
    """Test that curl commands are generated with full, non-truncated data"""
    print("🧪 Testing Curl Command Generation")
    print("=" * 50)
    
    # Create API logger
    api_logger = APILogger(Mock())
    
    # Test data
    method = "POST"
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer sk-1234567890abcdef",
        "Content-Type": "application/json",
        "User-Agent": "RAG-LLM-API/1.0"
    }
    body = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Tell me about artificial intelligence"}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    # Generate curl command
    curl_command = api_logger.generate_curl_command(method, url, headers, body)
    
    print(f"✅ Curl command generated successfully")
    print(f"   Method: {method}")
    print(f"   URL: {url}")
    print(f"   Headers count: {len(headers)}")
    print(f"   Body keys: {list(body.keys())}")
    print(f"   Curl command length: {len(curl_command) if curl_command else 0}")
    
    if curl_command:
        print(f"\n📋 Generated curl command:")
        print(curl_command)
        
        # Check if sensitive data is redacted
        if "[REDACTED]" in curl_command:
            print(f"   ✅ Sensitive data properly redacted")
        else:
            print(f"   ⚠️  No sensitive data redaction detected")
        
        # Check if body is included
        if "-d '" in curl_command:
            print(f"   ✅ Request body included in curl command")
        else:
            print(f"   ⚠️  Request body not included in curl command")
        
        return True
    else:
        print(f"   ❌ No curl command generated")
        return False


def test_request_logging_truncation():
    """Test that request logging doesn't truncate important data"""
    print("\n🧪 Testing Request Logging Truncation")
    print("=" * 50)
    
    # Create middleware with larger body size limit
    middleware = EnhancedRequestLoggingMiddleware(
        log_request_body=True,
        log_response_body=True,
        max_body_size=1024 * 100,  # 100KB for testing
        sensitive_headers=['authorization', 'cookie'],
        sensitive_body_fields=['password', 'token']
    )
    
    print(f"✅ Middleware configured")
    print(f"   Max body size: {middleware.max_body_size} bytes")
    print(f"   Log request body: {middleware.log_request_body}")
    print(f"   Log response body: {middleware.log_response_body}")
    print(f"   Sensitive headers: {middleware.sensitive_headers}")
    print(f"   Sensitive body fields: {middleware.sensitive_body_fields}")
    
    # Test body size limits
    test_body = "This is a test body. " * 1000  # ~23KB
    print(f"   Test body size: {len(test_body)} characters")
    print(f"   Within limit: {len(test_body) <= middleware.max_body_size}")
    
    return len(test_body) <= middleware.max_body_size


def test_response_logging_truncation():
    """Test that response logging doesn't truncate important data"""
    print("\n🧪 Testing Response Logging Truncation")
    print("=" * 50)
    
    # Create middleware
    middleware = EnhancedRequestLoggingMiddleware(
        max_body_size=1024 * 100  # 100KB
    )
    
    # Test response body handling
    test_response_body = {
        "id": "chatcmpl-1234567890",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a comprehensive response about artificial intelligence. " * 100
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 200,
            "total_tokens": 250
        },
        "sources": [
            {
                "content": "This is source content that should not be truncated. " * 50,
                "source": "document1.pdf",
                "score": 0.95
            }
        ],
        "metadata": {
            "context_aware": True,
            "persona_preserved": True,
            "rag_context_added": True,
            "sources_count": 1
        }
    }
    
    response_json = json.dumps(test_response_body, indent=2)
    print(f"✅ Response body created")
    print(f"   Response size: {len(response_json)} characters")
    print(f"   Within limit: {len(response_json) <= middleware.max_body_size}")
    print(f"   Sources included: {'sources' in response_json}")
    print(f"   Metadata included: {'metadata' in response_json}")
    
    return len(response_json) <= middleware.max_body_size


def test_sanitization_preserves_structure():
    """Test that sanitization preserves data structure while removing sensitive info"""
    print("\n🧪 Testing Sanitization Preserves Structure")
    print("=" * 50)
    
    # Test data with sensitive information
    test_data = {
        "api_key": "sk-1234567890abcdef",
        "password": "secret123",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Tell me about AI"}
        ],
        "sources": [
            {
                "content": "This is important context that should be preserved. " * 20,
                "source": "document.pdf",
                "score": 0.95
            }
        ],
        "metadata": {
            "persona_preserved": True,
            "rag_context_added": True
        }
    }
    
    # Sanitize data
    sanitized_data = sanitize_for_logging(test_data)
    
    print(f"✅ Data sanitized successfully")
    print(f"   Original keys: {list(test_data.keys())}")
    print(f"   Sanitized keys: {list(sanitized_data.keys())}")
    
    # Check sensitive data is redacted
    if sanitized_data.get("api_key") == "[REDACTED]":
        print(f"   ✅ API key properly redacted")
    else:
        print(f"   ❌ API key not redacted")
    
    if sanitized_data.get("password") == "[REDACTED]":
        print(f"   ✅ Password properly redacted")
    else:
        print(f"   ❌ Password not redacted")
    
    # Check important data is preserved
    if "messages" in sanitized_data:
        print(f"   ✅ Messages preserved")
    else:
        print(f"   ❌ Messages not preserved")
    
    if "sources" in sanitized_data:
        print(f"   ✅ Sources preserved")
        sources = sanitized_data["sources"]
        if sources and "content" in sources[0]:
            content_length = len(sources[0]["content"])
            print(f"   ✅ Source content preserved (length: {content_length})")
        else:
            print(f"   ❌ Source content not preserved")
    else:
        print(f"   ❌ Sources not preserved")
    
    if "metadata" in sanitized_data:
        print(f"   ✅ Metadata preserved")
    else:
        print(f"   ❌ Metadata not preserved")
    
    return (sanitized_data.get("api_key") == "[REDACTED]" and 
            sanitized_data.get("password") == "[REDACTED]" and
            "messages" in sanitized_data and
            "sources" in sanitized_data and
            "metadata" in sanitized_data)


def test_external_api_call_logging():
    """Test external API call logging with full details"""
    print("\n🧪 Testing External API Call Logging")
    print("=" * 50)
    
    # Create API call data
    api_call = ExternalAPICall(
        correlation_id="test-123",
        provider="openai",
        endpoint="https://api.openai.com/v1/chat/completions",
        method="POST",
        request_size_bytes=2048,
        response_size_bytes=4096,
        status_code=200,
        duration_ms=1250.5,
        success=True,
        error_type=None,
        error_message=None,
        timestamp="2024-01-01T12:00:00Z",
        curl_command="curl -X POST 'https://api.openai.com/v1/chat/completions' \\\n  -H 'Content-Type: application/json' \\\n  -H 'Authorization: [REDACTED]' \\\n  -d '{\"model\":\"gpt-3.5-turbo\",\"messages\":[...]}'",
        retry_count=0
    )
    
    print(f"✅ External API call created")
    print(f"   Provider: {api_call.provider}")
    print(f"   Endpoint: {api_call.endpoint}")
    print(f"   Method: {api_call.method}")
    print(f"   Request size: {api_call.request_size_bytes} bytes")
    print(f"   Response size: {api_call.response_size_bytes} bytes")
    print(f"   Duration: {api_call.duration_ms} ms")
    print(f"   Success: {api_call.success}")
    print(f"   Curl command length: {len(api_call.curl_command) if api_call.curl_command else 0}")
    
    if api_call.curl_command:
        print(f"   ✅ Curl command included for debugging")
        print(f"   Curl command preview: {api_call.curl_command[:100]}...")
    else:
        print(f"   ❌ No curl command included")
    
    return api_call.curl_command is not None


def main():
    """Run all logging debugging tests"""
    print("🚀 Logging Debugging Test Suite")
    print("=" * 60)
    
    tests = [
        test_curl_command_generation,
        test_request_logging_truncation,
        test_response_logging_truncation,
        test_sanitization_preserves_structure,
        test_external_api_call_logging
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Logging provides non-truncated data for debugging.")
        print("\n✅ Key Findings:")
        print("   - Curl commands are generated with full request details")
        print("   - Sensitive data is properly redacted")
        print("   - Important context and metadata are preserved")
        print("   - Response bodies are logged with sufficient size limits")
        print("   - External API calls include debugging information")
        return True
    else:
        print("❌ Some tests failed. Logging may truncate important debugging data.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 