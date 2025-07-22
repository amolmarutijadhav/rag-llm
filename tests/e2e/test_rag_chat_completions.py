#!/usr/bin/env python3
"""
Test script for RAG-enhanced chat completions endpoint
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_rag_chat_completions_basic():
    """Test basic RAG chat completions with multi-agentic structure"""
    print("🔍 Testing RAG chat completions (basic)...")
    
    test_request = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful customer service agent for TechCorp. You are friendly, professional, and knowledgeable about our products."
            },
            {
                "role": "user",
                "content": "What are the specifications of the X1 laptop?"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ /chat/completions - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Model: {result.get('model', 'N/A')}")
            print(f"   Usage: {result.get('usage', 'N/A')}")
            print(f"   RAG Metadata: {result.get('rag_metadata', 'N/A')}")
            
            # Print the first choice content
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                print(f"   Role: {choice.get('message', {}).get('role', 'N/A')}")
                content = choice.get('message', {}).get('content', '')
                print(f"   Content: {content[:200]}{'...' if len(content) > 200 else ''}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ /chat/completions - Error: {e}")

def test_rag_chat_completions_conversation():
    """Test RAG chat completions with conversation history"""
    print("\n💬 Testing RAG chat completions (conversation)...")
    
    test_request = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a technical support specialist for SoftwareCorp. You help users with software installation and troubleshooting."
            },
            {
                "role": "user",
                "content": "I'm having trouble installing the software"
            },
            {
                "role": "assistant",
                "content": "I'd be happy to help you with the installation. What specific error are you encountering?"
            },
            {
                "role": "user",
                "content": "It says 'permission denied' when I try to run the installer"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ /chat/completions (conversation) - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   RAG Metadata: {result.get('rag_metadata', 'N/A')}")
            
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                content = choice.get('message', {}).get('content', '')
                print(f"   Response: {content[:200]}{'...' if len(content) > 200 else ''}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ /chat/completions (conversation) - Error: {e}")

def test_rag_chat_completions_invalid_structure():
    """Test RAG chat completions with invalid message structure"""
    print("\n⚠️ Testing RAG chat completions (invalid structure)...")
    
    # Test without system message
    test_request = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": "What are the specifications of the X1 laptop?"
            }
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ /chat/completions (no system) - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Expected error: {response.json()}")
            
    except Exception as e:
        print(f"❌ /chat/completions (no system) - Error: {e}")

def test_rag_chat_completions_no_user_message():
    """Test RAG chat completions with no user message"""
    print("\n⚠️ Testing RAG chat completions (no user message)...")
    
    test_request = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            }
        ],
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ /chat/completions (no user) - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Expected error: {response.json()}")
            
    except Exception as e:
        print(f"❌ /chat/completions (no user) - Error: {e}")

def test_rag_chat_completions_streaming():
    """Test RAG chat completions with streaming"""
    print("\n🌊 Testing RAG chat completions (streaming)...")
    
    test_request = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that provides detailed explanations."
            },
            {
                "role": "user",
                "content": "Explain how machine learning works in detail"
            }
        ],
        "temperature": 0.7,
        "stream": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            json=test_request,
            headers={"Content-Type": "application/json"},
            stream=True
        )
        print(f"✅ /chat/completions (streaming) - Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   Streaming response received")
            # Note: The current implementation doesn't support streaming yet
            # This test is for future enhancement
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ /chat/completions (streaming) - Error: {e}")

def main():
    """Run all RAG chat completions tests"""
    print("🚀 Starting RAG Chat Completions Tests")
    print("=" * 60)
    
    # Test basic functionality
    test_rag_chat_completions_basic()
    
    # Test conversation history
    test_rag_chat_completions_conversation()
    
    # Test error cases
    test_rag_chat_completions_invalid_structure()
    test_rag_chat_completions_no_user_message()
    
    # Test streaming (for future enhancement)
    test_rag_chat_completions_streaming()
    
    print("\n" + "=" * 60)
    print("✅ RAG Chat Completions testing completed!")

if __name__ == "__main__":
    main() 