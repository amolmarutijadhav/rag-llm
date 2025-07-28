"""
Example usage of the enhanced InhouseLLMProvider with preprocessor and postprocessor functionality.

This example demonstrates how to configure and use the InhouseLLMProvider with:
1. Static fields for authentication
2. Custom conversation handling
3. OpenAI-like response generation
"""

import asyncio
import os
from typing import List, Dict, Any
from app.infrastructure.providers.inhouse_provider import InhouseLLMProvider

def example_basic_configuration():
    """Example 1: Basic configuration with minimal static fields."""
    
    config = {
        "api_url": "https://inhouse-llm.company.com/api/v1/chat",
        "api_key": "your-api-key-here",
        "default_model": "company-llm-v2",
        "default_temperature": 0.1,
        "default_max_tokens": 1000,
        
        # Minimal static fields
        "static_fields": {
            "client_id": "rag-llm-system",
            "version": "1.0"
        }
    }
    
    return InhouseLLMProvider(config)

def example_comprehensive_configuration():
    """Example 2: Comprehensive configuration with full static fields."""
    
    config = {
        "api_url": "https://inhouse-llm.company.com/api/v1/chat",
        "api_key": "your-api-key-here",
        "default_model": "company-llm-v2",
        "default_temperature": 0.1,
        "default_max_tokens": 1000,
        
        # Comprehensive static fields for authentication/identification
        "static_fields": {
            "client_id": "rag-llm-system",
            "version": "2.0",
            "environment": "production",
            "request_source": "api",
            "auth_token": "static-auth-token-123",
            "organization_id": "org-12345",
            "project_id": "proj-67890",
            "user_id": "user-abc123",
            "session_id": "session-xyz789"
        }
    }
    
    return InhouseLLMProvider(config)

async def example_conversation_handling():
    """Example 4: Demonstrate conversation handling capabilities."""
    
    provider = example_basic_configuration()
    
    # Example 1: Simple user question
    print("=== Example 1: Simple User Question ===")
    messages = [
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    response = await provider.call_llm(messages)
    print(f"Response: {response}")
    print()
    
    # Example 2: Conversation with system prompt
    print("=== Example 2: Conversation with System Prompt ===")
    messages = [
        {"role": "system", "content": "You are a helpful assistant that provides concise answers."},
        {"role": "user", "content": "What is the capital of France?"},
        {"role": "assistant", "content": "The capital of France is Paris."},
        {"role": "user", "content": "What about Germany?"}
    ]
    
    response = await provider.call_llm(messages)
    print(f"Response: {response}")
    print()

async def example_api_calls():
    """Example 5: Demonstrate different API call methods."""
    
    provider = example_comprehensive_configuration()
    
    # Example 1: Simple call_llm (returns content string)
    print("=== Example 1: Simple call_llm ===")
    messages = [
        {"role": "user", "content": "What is 2 + 2?"}
    ]
    
    response = await provider.call_llm(messages)
    print(f"Content response: {response}")
    print()
    
    # Example 2: call_llm_api with full response
    print("=== Example 2: call_llm_api with Full Response ===")
    request = {
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2 + 2?"}
        ],
        "model": "company-llm-v2",
        "temperature": 0.5,
        "max_tokens": 500
    }
    
    full_response = await provider.call_llm_api(request, return_full_response=True)
    print(f"Full response structure:")
    print(f"  ID: {full_response.get('id')}")
    print(f"  Model: {full_response.get('model')}")
    print(f"  Content: {full_response.get('choices', [{}])[0].get('message', {}).get('content')}")
    print(f"  Usage: {full_response.get('usage')}")
    print()

def main():
    """Run all examples."""
    print("🚀 InhouseLLMProvider Usage Examples")
    print("=" * 50)
    print()
    
    # Run examples
    asyncio.run(example_conversation_handling())
    asyncio.run(example_api_calls())
    
    print("✅ All examples completed!")
    print()
    print("📝 Configuration Notes:")
    print("- Set INHOUSE_LLM_API_URL in your .env file")
    print("- Configure static_fields for authentication")
    print("- The provider automatically handles conversation formatting")
    print("- Responses are automatically converted to OpenAI-like format")

if __name__ == "__main__":
    main() 