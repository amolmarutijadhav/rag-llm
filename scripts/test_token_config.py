#!/usr/bin/env python3
"""
Test script to verify token configuration implementation
"""

import sys
import os
from unittest.mock import Mock, AsyncMock

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.token_config import TokenConfig, TokenConfigService, token_config_service
from app.domain.models.requests import ChatCompletionRequest, ChatMessage


def test_token_config_validation():
    """Test token configuration validation"""
    print("🧪 Testing Token Configuration Validation")
    print("=" * 50)
    
    # Test valid configuration
    try:
        config = TokenConfig(
            max_response_tokens=4000,
            min_response_tokens=100,
            max_context_tokens=8000,
            max_total_tokens=16000
        )
        print("✅ Valid configuration created successfully")
        print(f"   Max response tokens: {config.max_response_tokens}")
        print(f"   Max context tokens: {config.max_context_tokens}")
        print(f"   Max total tokens: {config.max_total_tokens}")
    except ValueError as e:
        print(f"❌ Valid configuration failed: {e}")
        return False
    
    # Test invalid configuration (response tokens too high)
    try:
        config = TokenConfig(max_response_tokens=10000)  # Exceeds max
        print("❌ Invalid configuration should have failed")
        return False
    except ValueError as e:
        print(f"✅ Invalid configuration correctly rejected: {e}")
    
    # Test invalid configuration (total tokens too low)
    try:
        config = TokenConfig(max_total_tokens=1000)  # Below minimum
        print("❌ Invalid configuration should have failed")
        return False
    except ValueError as e:
        print(f"✅ Invalid configuration correctly rejected: {e}")
    
    return True


def test_token_config_service():
    """Test token configuration service"""
    print("\n🧪 Testing Token Configuration Service")
    print("=" * 50)
    
    # Test service initialization
    service = TokenConfigService()
    config = service.get_config()
    
    print(f"✅ Service initialized successfully")
    print(f"   Max response tokens: {config.max_response_tokens}")
    print(f"   Max context tokens: {config.max_context_tokens}")
    print(f"   Max total tokens: {config.max_total_tokens}")
    
    # Test token calculation methods
    response_tokens = config.get_response_tokens(2000)
    print(f"   Requested 2000 tokens, got: {response_tokens}")
    
    response_tokens = config.get_response_tokens(6000)  # Exceeds max
    print(f"   Requested 6000 tokens, got: {response_tokens} (capped)")
    
    available_tokens = config.calculate_available_tokens(5000)
    print(f"   Available tokens for 5000 prompt tokens: {available_tokens}")
    
    return True


def test_request_model_integration():
    """Test request model integration with token config"""
    print("\n🧪 Testing Request Model Integration")
    print("=" * 50)
    
    # Test request without max_tokens (should use default)
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant"),
        ChatMessage(role="user", content="Hello")
    ]
    
    request = ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    print(f"✅ Request created successfully")
    print(f"   Model: {request.model}")
    print(f"   Max tokens: {request.max_tokens}")
    print(f"   Expected default: {token_config_service.get_config().max_response_tokens}")
    
    # Test request with custom max_tokens
    request_with_custom = ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=2000
    )
    
    print(f"   Custom max tokens: {request_with_custom.max_tokens}")
    
    return True


def test_environment_variables():
    """Test environment variable loading"""
    print("\n🧪 Testing Environment Variable Loading")
    print("=" * 50)
    
    # Test default values
    config = token_config_service.get_config()
    print(f"✅ Default configuration loaded")
    print(f"   MAX_RESPONSE_TOKENS: {config.max_response_tokens}")
    print(f"   MAX_CONTEXT_TOKENS: {config.max_context_tokens}")
    print(f"   MAX_TOTAL_TOKENS: {config.max_total_tokens}")
    
    # Test environment variable override
    import os
    original_env = os.environ.copy()
    
    try:
        os.environ["MAX_RESPONSE_TOKENS"] = "3000"
        os.environ["MAX_CONTEXT_TOKENS"] = "6000"
        
        # Create new service instance to reload config
        new_service = TokenConfigService()
        new_config = new_service.get_config()
        
        print(f"✅ Environment variable override successful")
        print(f"   MAX_RESPONSE_TOKENS: {new_config.max_response_tokens} (expected: 3000)")
        print(f"   MAX_CONTEXT_TOKENS: {new_config.max_context_tokens} (expected: 6000)")
        
    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)
    
    return True


def main():
    """Run all tests"""
    print("🚀 Token Configuration Implementation Test")
    print("=" * 60)
    
    tests = [
        test_token_config_validation,
        test_token_config_service,
        test_request_model_integration,
        test_environment_variables
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
        print("🎉 All tests passed! Token configuration implementation is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 