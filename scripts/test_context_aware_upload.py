#!/usr/bin/env python3
"""
Test script for context-aware document upload functionality.
This script helps debug upload issues by testing different scenarios.
"""

import asyncio
import os
import tempfile
import requests
from pathlib import Path

def create_test_file(content: str, filename: str = "test_document.txt") -> str:
    """Create a temporary test file with given content"""
    temp_dir = Path(tempfile.gettempdir())
    test_file_path = temp_dir / filename
    
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(test_file_path)

def test_health_endpoint(base_url: str = "http://localhost:8000"):
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health endpoint: {response.status_code} - {response.text}")
        return True
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False

def test_provider_health(base_url: str = "http://localhost:8000"):
    """Test the provider health endpoint"""
    print("\n🔍 Testing provider health...")
    try:
        response = requests.get(f"{base_url}/context-aware-documents/health")
        print(f"✅ Provider health: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json().get("status") == "healthy"
    except Exception as e:
        print(f"❌ Provider health check failed: {e}")
        return False

def test_context_options(base_url: str = "http://localhost:8000"):
    """Test the context options endpoint"""
    print("\n🔍 Testing context options...")
    try:
        response = requests.get(f"{base_url}/context-aware-documents/context-options")
        print(f"✅ Context options: {response.status_code}")
        print(f"Available context types: {response.json().get('context_types', [])}")
        return True
    except Exception as e:
        print(f"❌ Context options failed: {e}")
        return False

def test_text_upload(base_url: str = "http://localhost:8000"):
    """Test text upload with context"""
    print("\n🔍 Testing text upload with context...")
    
    test_text = "This is a test document for context-aware upload. It contains technical information about API documentation."
    
    data = {
        'text': test_text,
        'context_type': 'technical',
        'content_domain': 'api_documentation',
        'document_category': 'user_guide',
        'relevance_tags': 'api, documentation, test',
        'description': 'Test document for debugging upload issues'
    }
    
    try:
        response = requests.post(f"{base_url}/context-aware-documents/upload-text", data=data)
        print(f"✅ Text upload: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Text upload failed: {e}")
        return False

def test_file_upload(base_url: str = "http://localhost:8000"):
    """Test file upload with context"""
    print("\n🔍 Testing file upload with context...")
    
    # Create test file
    test_content = "This is a test file for context-aware upload.\nIt contains multiple lines of technical content.\nThis should help debug any upload issues."
    test_file_path = create_test_file(test_content, "test_upload.txt")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'context_type': 'technical',
                'content_domain': 'api_documentation',
                'document_category': 'user_guide',
                'relevance_tags': 'api, documentation, test, file',
                'description': 'Test file for debugging upload issues'
            }
            
            response = requests.post(f"{base_url}/context-aware-documents/upload", files=files, data=data)
            print(f"✅ File upload: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
    except Exception as e:
        print(f"❌ File upload failed: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_stats(base_url: str = "http://localhost:8000"):
    """Test getting stats"""
    print("\n🔍 Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/context-aware-documents/stats")
        print(f"✅ Stats: {response.status_code}")
        print(f"Stats: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Stats failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Context-Aware Document Upload Tests")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Test basic endpoints
    health_ok = test_health_endpoint(base_url)
    provider_ok = test_provider_health(base_url)
    options_ok = test_context_options(base_url)
    
    if not health_ok:
        print("\n❌ Server is not running. Please start the server first:")
        print("   python scripts/run.py")
        return
    
    if not provider_ok:
        print("\n⚠️  Provider health check failed. This might indicate configuration issues.")
        print("   Check your .env file for correct API keys and URLs.")
    
    # Test upload functionality
    text_upload_ok = test_text_upload(base_url)
    file_upload_ok = test_file_upload(base_url)
    
    # Test stats
    stats_ok = test_stats(base_url)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Health Endpoint: {'✅' if health_ok else '❌'}")
    print(f"   Provider Health: {'✅' if provider_ok else '❌'}")
    print(f"   Context Options: {'✅' if options_ok else '❌'}")
    print(f"   Text Upload: {'✅' if text_upload_ok else '❌'}")
    print(f"   File Upload: {'✅' if file_upload_ok else '❌'}")
    print(f"   Stats: {'✅' if stats_ok else '❌'}")
    
    if all([health_ok, text_upload_ok, file_upload_ok]):
        print("\n🎉 All tests passed! Context-aware upload is working correctly.")
    else:
        print("\n🔧 Some tests failed. Check the logs above for details.")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure the server is running: python scripts/run.py")
        print("   2. Check your .env file for correct API keys")
        print("   3. Verify provider configuration")
        print("   4. Check server logs for detailed error messages")

if __name__ == "__main__":
    main() 