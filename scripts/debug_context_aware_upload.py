#!/usr/bin/env python3
"""
Debug script for context-aware document upload functionality.
This script helps identify the exact point of failure.
"""

import asyncio
import os
import tempfile
from pathlib import Path
from app.domain.services.context_aware_rag_service import ContextAwareRAGService
from app.domain.models.requests import DocumentContext, DocumentUploadRequest
from app.infrastructure.providers import get_embedding_provider, get_vector_store_provider, get_llm_provider
from app.core.logging_config import get_logger

logger = get_logger(__name__)

async def test_provider_initialization():
    """Test if providers can be initialized correctly"""
    print("🔍 Testing provider initialization...")
    
    try:
        # Test embedding provider
        print("  Testing embedding provider...")
        embedding_provider = get_embedding_provider()
        print(f"    ✅ Embedding provider: {type(embedding_provider).__name__}")
        
        # Test vector store provider
        print("  Testing vector store provider...")
        vector_store_provider = get_vector_store_provider()
        print(f"    ✅ Vector store provider: {type(vector_store_provider).__name__}")
        
        # Test LLM provider
        print("  Testing LLM provider...")
        llm_provider = get_llm_provider()
        print(f"    ✅ LLM provider: {type(llm_provider).__name__}")
        
        return True
    except Exception as e:
        print(f"    ❌ Provider initialization failed: {e}")
        return False

async def test_rag_service_initialization():
    """Test if RAG service can be initialized correctly"""
    print("\n🔍 Testing RAG service initialization...")
    
    try:
        from app.domain.services.rag_service import RAGService
        
        # Test RAG service with providers
        embedding_provider = get_embedding_provider()
        vector_store_provider = get_vector_store_provider()
        llm_provider = get_llm_provider()
        
        rag_service = RAGService(
            embedding_provider=embedding_provider,
            llm_provider=llm_provider,
            vector_store_provider=vector_store_provider
        )
        
        print(f"    ✅ RAG service initialized: {type(rag_service).__name__}")
        print(f"    ✅ Vector store: {type(rag_service.vector_store).__name__}")
        print(f"    ✅ Document loader: {type(rag_service.document_loader).__name__}")
        
        return rag_service
    except Exception as e:
        print(f"    ❌ RAG service initialization failed: {e}")
        return None

async def test_context_aware_rag_service_initialization():
    """Test if context-aware RAG service can be initialized correctly"""
    print("\n🔍 Testing context-aware RAG service initialization...")
    
    try:
        # Test with providers
        embedding_provider = get_embedding_provider()
        vector_store_provider = get_vector_store_provider()
        llm_provider = get_llm_provider()
        
        context_aware_service = ContextAwareRAGService(
            embedding_provider=embedding_provider,
            llm_provider=llm_provider,
            vector_store_provider=vector_store_provider
        )
        
        print(f"    ✅ Context-aware RAG service initialized: {type(context_aware_service).__name__}")
        print(f"    ✅ RAG service: {type(context_aware_service.rag_service).__name__}")
        print(f"    ✅ Vector store: {type(context_aware_service.rag_service.vector_store).__name__}")
        
        return context_aware_service
    except Exception as e:
        print(f"    ❌ Context-aware RAG service initialization failed: {e}")
        return None

async def test_document_loading():
    """Test if document loading works"""
    print("\n🔍 Testing document loading...")
    
    try:
        # Create a test file
        test_content = "This is a test document for debugging context-aware upload."
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write(test_content)
        temp_file.close()
        
        # Test RAG service document loading
        rag_service = await test_rag_service_initialization()
        if not rag_service:
            return False
        
        documents, ocr_text = rag_service.document_loader.load_document(temp_file.name)
        
        print(f"    ✅ Document loaded successfully")
        print(f"    ✅ Documents count: {len(documents)}")
        print(f"    ✅ OCR text: {ocr_text if ocr_text else 'None'}")
        
        # Clean up
        os.unlink(temp_file.name)
        
        return True
    except Exception as e:
        print(f"    ❌ Document loading failed: {e}")
        return False

async def test_vector_store_operations():
    """Test if vector store operations work"""
    print("\n🔍 Testing vector store operations...")
    
    try:
        rag_service = await test_rag_service_initialization()
        if not rag_service:
            return False
        
        # Test getting collection stats
        stats = rag_service.vector_store.get_collection_stats()
        print(f"    ✅ Collection stats retrieved: {stats}")
        
        # Test embedding generation
        test_texts = ["This is a test document"]
        embeddings = await rag_service.vector_store.embedding_provider.get_embeddings(test_texts)
        print(f"    ✅ Embeddings generated: {len(embeddings)} embeddings, {len(embeddings[0])} dimensions")
        
        return True
    except Exception as e:
        print(f"    ❌ Vector store operations failed: {e}")
        return False

async def test_full_context_aware_upload():
    """Test the full context-aware upload process"""
    print("\n🔍 Testing full context-aware upload process...")
    
    try:
        # Initialize service
        context_aware_service = await test_context_aware_rag_service_initialization()
        if not context_aware_service:
            return False
        
        # Create test file
        test_content = "This is a test document for context-aware upload debugging."
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write(test_content)
        temp_file.close()
        
        # Create document context
        context = DocumentContext(
            context_type=["technical"],
            content_domain=["api_documentation"],
            document_category=["user_guide"],
            relevance_tags=["test", "debug"],
            description="Test document for debugging"
        )
        
        # Create upload request
        upload_request = DocumentUploadRequest(
            file_path=temp_file.name,
            context=context
        )
        
        # Test upload
        result = await context_aware_service.add_document_with_context(upload_request)
        
        print(f"    ✅ Upload result: {result}")
        
        # Clean up
        os.unlink(temp_file.name)
        
        return result.get('success', False)
    except Exception as e:
        print(f"    ❌ Full context-aware upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all debug tests"""
    print("🚀 Starting Context-Aware Upload Debug Tests")
    print("=" * 60)
    
    # Test each component step by step
    provider_ok = await test_provider_initialization()
    if not provider_ok:
        print("\n❌ Provider initialization failed. Check your .env configuration.")
        return
    
    rag_service_ok = await test_rag_service_initialization()
    if not rag_service_ok:
        print("\n❌ RAG service initialization failed.")
        return
    
    context_aware_ok = await test_context_aware_rag_service_initialization()
    if not context_aware_ok:
        print("\n❌ Context-aware RAG service initialization failed.")
        return
    
    document_loading_ok = await test_document_loading()
    if not document_loading_ok:
        print("\n❌ Document loading failed.")
        return
    
    vector_store_ok = await test_vector_store_operations()
    if not vector_store_ok:
        print("\n❌ Vector store operations failed.")
        return
    
    full_upload_ok = await test_full_context_aware_upload()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Debug Test Summary:")
    print(f"   Provider Initialization: {'✅' if provider_ok else '❌'}")
    print(f"   RAG Service Initialization: {'✅' if rag_service_ok else '❌'}")
    print(f"   Context-Aware Service: {'✅' if context_aware_ok else '❌'}")
    print(f"   Document Loading: {'✅' if document_loading_ok else '❌'}")
    print(f"   Vector Store Operations: {'✅' if vector_store_ok else '❌'}")
    print(f"   Full Upload Process: {'✅' if full_upload_ok else '❌'}")
    
    if all([provider_ok, rag_service_ok, context_aware_ok, document_loading_ok, vector_store_ok, full_upload_ok]):
        print("\n🎉 All tests passed! Context-aware upload should work correctly.")
    else:
        print("\n🔧 Some tests failed. Check the output above for specific issues.")
        print("\n💡 Troubleshooting tips:")
        print("   1. Check your .env file for correct API keys")
        print("   2. Verify provider URLs are accessible")
        print("   3. Test with mock providers first")
        print("   4. Check network connectivity")

if __name__ == "__main__":
    asyncio.run(main()) 