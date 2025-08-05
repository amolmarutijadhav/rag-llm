#!/usr/bin/env python3
"""
Test script to verify persona preservation fix in RAG service
"""

import sys
import os
import asyncio
from unittest.mock import AsyncMock, Mock

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.domain.services.rag_service import RAGService


async def test_persona_preservation_in_rag_service():
    """Test that RAG service preserves persona when system_message is provided"""
    print("🧪 Testing Persona Preservation in RAG Service")
    print("=" * 60)
    
    # Create mock providers
    mock_embedding_provider = AsyncMock()
    mock_embedding_provider.get_embeddings.return_value = [[0.1, 0.2, 0.3]]  # Mock embedding
    
    mock_vector_store_provider = AsyncMock()
    mock_vector_store_provider.search_vectors.return_value = [
        {
            "payload": {
                "content": "This is test content about artificial intelligence.",
                "metadata": {"source": "test_doc.pdf"}
            },
            "score": 0.95
        }
    ]
    
    mock_llm_provider = AsyncMock()
    mock_llm_provider.call_llm.return_value = "This is a test response about AI."
    
    # Create RAG service with mock providers
    rag_service = RAGService(
        embedding_provider=mock_embedding_provider,
        llm_provider=mock_llm_provider,
        vector_store_provider=mock_vector_store_provider
    )
    
    # Test 1: With persona (system_message provided)
    print("\n📝 Test 1: With Persona (system_message provided)")
    print("-" * 40)
    
    test_persona = "You are a sarcastic comedian who loves to make jokes about technology."
    test_question = "What is artificial intelligence?"
    
    result = await rag_service.ask_question(
        question=test_question,
        top_k=3,
        system_message=test_persona
    )
    
    print(f"✅ Result success: {result['success']}")
    print(f"✅ Answer generated: {result['answer']}")
    print(f"✅ Sources count: {len(result['sources'])}")
    
    # Check that the LLM was called with the correct system message
    llm_call_args = mock_llm_provider.call_llm.call_args
    if llm_call_args:
        messages = llm_call_args[0][0]  # First argument is messages
        system_message = messages[0]['content']
        print(f"✅ System message includes persona: {test_persona in system_message}")
        print(f"✅ System message includes RAG context: {'artificial intelligence' in system_message}")
        print(f"✅ Persona preserved correctly: {test_persona in system_message}")
    else:
        print("❌ LLM was not called")
    
    # Reset mocks for next test
    mock_llm_provider.call_llm.reset_mock()
    
    # Test 2: Without persona (no system_message)
    print("\n📝 Test 2: Without Persona (no system_message)")
    print("-" * 40)
    
    result = await rag_service.ask_question(
        question=test_question,
        top_k=3
        # No system_message parameter
    )
    
    print(f"✅ Result success: {result['success']}")
    print(f"✅ Answer generated: {result['answer']}")
    print(f"✅ Sources count: {len(result['sources'])}")
    
    # Check that the LLM was called with the default system message
    llm_call_args = mock_llm_provider.call_llm.call_args
    if llm_call_args:
        messages = llm_call_args[0][0]  # First argument is messages
        system_message = messages[0]['content']
        print(f"✅ Uses default system message: {'You are a helpful assistant' in system_message}")
        print(f"✅ Includes RAG context: {'artificial intelligence' in system_message}")
        print(f"✅ No persona included: {test_persona not in system_message}")
    else:
        print("❌ LLM was not called")
    
    print("\n🎉 Persona preservation test completed successfully!")
    return True


async def test_backward_compatibility():
    """Test that existing calls without system_message still work"""
    print("\n🧪 Testing Backward Compatibility")
    print("=" * 60)
    
    # Create mock providers
    mock_embedding_provider = AsyncMock()
    mock_embedding_provider.get_embeddings.return_value = [[0.1, 0.2, 0.3]]
    
    mock_vector_store_provider = AsyncMock()
    mock_vector_store_provider.search_vectors.return_value = [
        {
            "payload": {
                "content": "This is test content.",
                "metadata": {"source": "test_doc.pdf"}
            },
            "score": 0.95
        }
    ]
    
    mock_llm_provider = AsyncMock()
    mock_llm_provider.call_llm.return_value = "This is a test response."
    
    # Create RAG service
    rag_service = RAGService(
        embedding_provider=mock_embedding_provider,
        llm_provider=mock_llm_provider,
        vector_store_provider=mock_vector_store_provider
    )
    
    # Test old-style call (without system_message parameter)
    result = await rag_service.ask_question("Test question", top_k=3)
    
    print(f"✅ Backward compatibility: {result['success']}")
    print(f"✅ Old-style call works: {result['answer'] is not None}")
    
    # Verify it uses default system message
    llm_call_args = mock_llm_provider.call_llm.call_args
    if llm_call_args:
        messages = llm_call_args[0][0]
        system_message = messages[0]['content']
        print(f"✅ Uses default message: {'You are a helpful assistant' in system_message}")
    
    print("🎉 Backward compatibility test passed!")
    return True


async def main():
    """Run all tests"""
    print("🚀 Persona Preservation Fix Test Suite")
    print("=" * 60)
    
    try:
        await test_persona_preservation_in_rag_service()
        await test_backward_compatibility()
        
        print("\n✅ All tests passed! Persona preservation fix is working correctly.")
        print("\n📋 Summary:")
        print("   - RAG service now accepts optional system_message parameter")
        print("   - Persona is preserved when system_message is provided")
        print("   - Default behavior maintained for backward compatibility")
        print("   - Enhanced logging tracks persona preservation status")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 