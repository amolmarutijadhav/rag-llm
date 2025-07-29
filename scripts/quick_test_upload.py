#!/usr/bin/env python3
"""
Quick test script to verify context-aware upload fix.
"""

import asyncio
import tempfile
import os
import sys

# Add current directory to path for imports
sys.path.append('.')

from app.domain.services.context_aware_rag_service import ContextAwareRAGService
from app.domain.models.requests import DocumentContext, DocumentUploadRequest
from app.infrastructure.providers import get_embedding_provider, get_vector_store_provider, get_llm_provider

async def quick_test():
    """Quick test of context-aware upload"""
    print("🚀 Quick Test: Context-Aware Upload")
    print("=" * 40)
    
    try:
        # Get providers
        print("1. Getting providers...")
        embedding_provider = get_embedding_provider()
        vector_store_provider = get_vector_store_provider()
        llm_provider = get_llm_provider()
        print(f"   ✅ Embedding: {type(embedding_provider).__name__}")
        print(f"   ✅ Vector Store: {type(vector_store_provider).__name__}")
        print(f"   ✅ LLM: {type(llm_provider).__name__}")
        
        # Initialize service
        print("\n2. Initializing context-aware service...")
        service = ContextAwareRAGService(
            embedding_provider=embedding_provider,
            llm_provider=llm_provider,
            vector_store_provider=vector_store_provider
        )
        print("   ✅ Service initialized")
        
        # Create test file
        print("\n3. Creating test file...")
        test_content = "This is a test document for context-aware upload."
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        temp_file.write(test_content)
        temp_file.close()
        print(f"   ✅ Test file created: {temp_file.name}")
        
        # Create context
        print("\n4. Creating document context...")
        context = DocumentContext(
            context_type=["technical"],
            content_domain=["api_documentation"],
            document_category=["user_guide"],
            relevance_tags=["test"],
            description="Test document"
        )
        print("   ✅ Context created")
        
        # Create request
        print("\n5. Creating upload request...")
        request = DocumentUploadRequest(
            file_path=temp_file.name,
            context=context
        )
        print("   ✅ Request created")
        
        # Test upload
        print("\n6. Testing upload...")
        result = await service.add_document_with_context(request)
        print(f"   ✅ Upload result: {result}")
        
        # Clean up
        os.unlink(temp_file.name)
        print("\n7. Cleanup completed")
        
        print("\n🎉 Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(quick_test()) 