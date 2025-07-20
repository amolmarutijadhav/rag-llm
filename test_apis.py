#!/usr/bin/env python3
"""
Simple script to test the RAG LLM API endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health_endpoints():
    """Test health check endpoints"""
    print("🔍 Testing health endpoints...")
    
    # Test /health
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ /health - Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ /health - Error: {e}")
    
    # Test root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ / - Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ / - Error: {e}")

def test_stats_endpoint():
    """Test stats endpoint"""
    print("\n📊 Testing stats endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/stats")
        print(f"✅ /stats - Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ /stats - Error: {e}")

def test_add_text_endpoint():
    """Test add text endpoint"""
    print("\n📝 Testing add text endpoint...")
    
    test_data = {
        "text": "Java is a high-level, class-based, object-oriented programming language developed by James Gosling at Sun Microsystems in 1995. It is designed to have as few implementation dependencies as possible and follows the 'Write Once, Run Anywhere' principle.",
        "source_name": "java_info"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/add-text",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ /add-text - Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ /add-text - Error: {e}")
        return False

def test_ask_question_endpoint():
    """Test ask question endpoint"""
    print("\n❓ Testing ask question endpoint...")
    
    test_data = {
        "question": "Who created Java?",
        "top_k": 3
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ /ask - Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ /ask - Error: {e}")

def test_clear_endpoint():
    """Test clear endpoint"""
    print("\n🗑️ Testing clear endpoint...")
    
    try:
        response = requests.delete(f"{BASE_URL}/clear")
        print(f"✅ /clear - Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ /clear - Error: {e}")

def main():
    """Run all API tests"""
    print("🚀 Starting RAG LLM API Tests")
    print("=" * 50)
    
    # Test health endpoints
    test_health_endpoints()
    
    # Test stats endpoint
    test_stats_endpoint()
    
    # Test add text endpoint
    text_added = test_add_text_endpoint()
    
    # Test ask question endpoint (only if text was added successfully)
    if text_added:
        test_ask_question_endpoint()
    
    # Test clear endpoint
    test_clear_endpoint()
    
    print("\n" + "=" * 50)
    print("✅ API testing completed!")

if __name__ == "__main__":
    main() 