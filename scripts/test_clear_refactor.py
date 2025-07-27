#!/usr/bin/env python3
"""
Test script to verify the clear endpoint refactoring.
This script tests that the /clear endpoint now deletes all points in the collection
instead of deleting the entire collection.
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.domain.services.rag_service import RAGService
from app.infrastructure.vector_store.vector_store import VectorStore
from app.infrastructure.external.external_api_service import ExternalAPIService

async def test_clear_functionality():
    """Test that clear_knowledge_base uses clear_all_points instead of delete_collection"""
    
    print("🧪 Testing clear endpoint refactoring...")
    
    # Create a mock external API service
    class MockExternalAPIService:
        def __init__(self):
            self.delete_collection_called = False
            self.delete_all_points_called = False
        
        def delete_collection(self):
            self.delete_collection_called = True
            return True
        
        def delete_all_points(self):
            self.delete_all_points_called = True
            return True
    
    # Create a mock vector store
    class MockVectorStore:
        def __init__(self):
            self.api_service = MockExternalAPIService()
            self.delete_collection_called = False
            self.clear_all_points_called = False
        
        def delete_collection(self):
            self.delete_collection_called = True
            return self.api_service.delete_collection()
        
        def clear_all_points(self):
            self.clear_all_points_called = True
            return self.api_service.delete_all_points()
    
    # Create RAG service with mock vector store
    rag_service = RAGService()
    mock_vector_store = MockVectorStore()
    rag_service.vector_store = mock_vector_store
    
    # Test the clear functionality
    result = rag_service.clear_knowledge_base()
    
    # Verify the behavior
    print(f"✅ Clear result: {result}")
    
    if result["success"]:
        print("✅ Clear operation was successful")
    else:
        print("❌ Clear operation failed")
        return False
    
    if mock_vector_store.clear_all_points_called:
        print("✅ clear_all_points() was called (correct behavior)")
    else:
        print("❌ clear_all_points() was not called")
        return False
    
    if mock_vector_store.delete_collection_called:
        print("❌ delete_collection() was called (incorrect behavior)")
        return False
    else:
        print("✅ delete_collection() was not called (correct behavior)")
    
    if mock_vector_store.api_service.delete_all_points_called:
        print("✅ External API delete_all_points() was called")
    else:
        print("❌ External API delete_all_points() was not called")
        return False
    
    if mock_vector_store.api_service.delete_collection_called:
        print("❌ External API delete_collection() was called (incorrect)")
        return False
    else:
        print("✅ External API delete_collection() was not called (correct)")
    
    print("\n🎉 All tests passed! The clear endpoint now correctly deletes all points instead of the collection.")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_clear_functionality())
    sys.exit(0 if success else 1) 