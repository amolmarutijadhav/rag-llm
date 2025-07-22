#!/usr/bin/env python3
"""
Test script to demonstrate RAG-enhanced chat completions with knowledge base data
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_rag_chat_with_java_data():
    """Test RAG chat completions with Java knowledge base data"""
    print("🔍 Testing RAG chat completions with Java data...")
    
    # Test 1: Customer service agent asking about Java
    test_request_1 = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful customer service agent for TechCorp. You are friendly, professional, and knowledgeable about programming languages and technology."
            },
            {
                "role": "user",
                "content": "Who created Java and when?"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            json=test_request_1,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Test 1 - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   RAG Metadata: {result.get('rag_metadata', 'N/A')}")
            
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                content = choice.get('message', {}).get('content', '')
                print(f"   Response: {content}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test 1 - Error: {e}")

def test_rag_chat_with_technical_agent():
    """Test RAG chat completions with technical support agent"""
    print("\n🔧 Testing RAG chat completions with technical agent...")
    
    test_request_2 = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a technical support specialist for SoftwareCorp. You help developers with programming language questions and provide detailed technical explanations."
            },
            {
                "role": "user",
                "content": "What are the key features of Java as a programming language?"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            json=test_request_2,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Test 2 - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   RAG Metadata: {result.get('rag_metadata', 'N/A')}")
            
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                content = choice.get('message', {}).get('content', '')
                print(f"   Response: {content}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test 2 - Error: {e}")

def test_rag_chat_conversation():
    """Test RAG chat completions with conversation history"""
    print("\n💬 Testing RAG chat completions with conversation...")
    
    test_request_3 = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a knowledgeable programming instructor. You help students understand programming concepts and provide clear, educational explanations."
            },
            {
                "role": "user",
                "content": "Tell me about Java"
            },
            {
                "role": "assistant",
                "content": "Java is a popular programming language. What specific aspect would you like to know more about?"
            },
            {
                "role": "user",
                "content": "What does 'Write Once, Run Anywhere' mean in Java?"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 350
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            json=test_request_3,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Test 3 - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   RAG Metadata: {result.get('rag_metadata', 'N/A')}")
            
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                content = choice.get('message', {}).get('content', '')
                print(f"   Response: {content}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test 3 - Error: {e}")

def test_rag_chat_no_context():
    """Test RAG chat completions with question that has no context"""
    print("\n❓ Testing RAG chat completions with no relevant context...")
    
    test_request_4 = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that provides information based on available knowledge."
            },
            {
                "role": "user",
                "content": "What is the capital of France?"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            json=test_request_4,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Test 4 - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   RAG Metadata: {result.get('rag_metadata', 'N/A')}")
            
            if 'choices' in result and len(result['choices']) > 0:
                choice = result['choices'][0]
                content = choice.get('message', {}).get('content', '')
                print(f"   Response: {content}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test 4 - Error: {e}")

def main():
    """Run all RAG tests with knowledge base data"""
    print("🚀 Starting RAG Chat Completions Tests with Knowledge Base Data")
    print("=" * 70)
    
    # Test with different agent personas and Java data
    test_rag_chat_with_java_data()
    test_rag_chat_with_technical_agent()
    test_rag_chat_conversation()
    test_rag_chat_no_context()
    
    print("\n" + "=" * 70)
    print("✅ RAG Chat Completions testing with knowledge base completed!")

if __name__ == "__main__":
    main() 