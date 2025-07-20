#!/usr/bin/env python3
"""
Search functionality test script for RAG LLM API
Useful for testing search functionality and verifying field handling
"""

import asyncio
import json
from src.vector_store import VectorStore

async def test_search():
    """Test the search functionality"""
    print("🔍 Testing search functionality...")
    
    vector_store = VectorStore()
    
    # Test search
    query = "Who created Java?"
    print(f"Query: {query}")
    
    try:
        results = await vector_store.search(query, top_k=3)
        print(f"✅ Search completed. Found {len(results)} results")
        
        if results:
            print("\n📋 Search Results:")
            for i, result in enumerate(results):
                print(f"\n--- Result {i+1} ---")
                content = result.get('content', 'N/A')
                print(f"Content: {content[:100]}{'...' if len(content) > 100 else ''}")
                print(f"Metadata: {result.get('metadata', {})}")
                print(f"Score: {result.get('score', 'N/A')}")
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
        import traceback
        traceback.print_exc()

async def test_multiple_queries():
    """Test multiple queries to verify field handling"""
    print("\n🧪 Testing multiple queries...")
    
    vector_store = VectorStore()
    queries = [
        "Who created Java?",
        "What is Python?",
        "Programming languages"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        try:
            results = await vector_store.search(query, top_k=2)
            print(f"Found {len(results)} results")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("🚀 RAG LLM Search Test")
    print("=" * 50)
    
    # Run basic search test
    asyncio.run(test_search())
    
    # Run multiple query test
    asyncio.run(test_multiple_queries())
    
    print("\n✅ Search testing completed!") 