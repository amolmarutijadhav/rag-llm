#!/usr/bin/env python3
"""
End-to-end tests for RAG LLM API endpoints
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import requests
import json
from datetime import datetime
from app.core.config import Config

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8000")
ADMIN_API_KEY = os.getenv("CLEAR_ENDPOINT_API_KEY", getattr(Config, "CLEAR_ENDPOINT_API_KEY", "admin-secret-key-change-me"))
CONFIRM_TOKEN = os.getenv("CLEAR_ENDPOINT_CONFIRMATION_TOKEN", getattr(Config, "CLEAR_ENDPOINT_CONFIRMATION_TOKEN", "CONFIRM_DELETE_ALL_DATA"))

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
        response = requests.get(f"{BASE_URL}/questions/stats")
        print(f"✅ /questions/stats - Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ /questions/stats - Error: {e}")

def test_add_text_endpoint():
    """Test add text endpoint"""
    print("\n📝 Testing add text endpoint...")
    
    test_data = {
        "text": "Java is a high-level, class-based, object-oriented programming language developed by James Gosling at Sun Microsystems in 1995. It is designed to have as few implementation dependencies as possible and follows the 'Write Once, Run Anywhere' principle.",
        "source_name": "java_info"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/documents/add-text",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ /documents/add-text - Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ /documents/add-text - Error: {e}")
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
            f"{BASE_URL}/questions/ask",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ /questions/ask - Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ /questions/ask - Error: {e}")

def test_clear_endpoint():
    """Test clear endpoint"""
    print("\n🗑️ Testing clear endpoint...")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/documents/clear-secure",
            headers={"Authorization": f"Bearer {ADMIN_API_KEY}", "Content-Type": "application/json"},
            json={"confirmation_token": CONFIRM_TOKEN, "reason": "E2E API test cleanup"}
        )
        print(f"✅ /documents/clear-secure - Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"❌ /documents/clear-secure - Error: {e}")

def main():
    """Run all API tests"""
    print("Starting RAG LLM API Tests")
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