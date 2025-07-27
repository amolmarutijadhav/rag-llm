#!/usr/bin/env python3
"""
OCR-specific test helpers for the plugin architecture.
Provides mock providers and patching utilities for OCR tests.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any, List
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider, VectorStoreProvider


class OCRTestHelpers:
    """Helper class for creating mock providers and utilities for OCR tests."""
    
    @staticmethod
    def create_mock_embedding_provider() -> Mock:
        """Create a mock embedding provider for OCR tests."""
        mock_provider = Mock(spec=EmbeddingProvider)
        mock_provider.get_embeddings.return_value = [[0.1, 0.2, 0.3] * 1536]
        mock_provider.get_model_info.return_value = {
            "model": "text-embedding-ada-002",
            "dimensions": 1536,
            "provider": "openai"
        }
        return mock_provider
    
    @staticmethod
    def create_mock_vector_store_provider() -> Mock:
        """Create a mock vector store provider for OCR tests."""
        mock_provider = Mock(spec=VectorStoreProvider)
        mock_provider.create_collection_if_not_exists.return_value = True
        mock_provider.insert_vectors.return_value = True
        mock_provider.search_vectors.return_value = [
            {
                "content": "Sample OCR extracted text content",
                "metadata": {"source": "test.pdf", "page": 0, "chunk_index": 0, "has_images": True},
                "score": 0.95
            }
        ]
        mock_provider.get_collection_stats.return_value = {
            "total_documents": 1,
            "total_points": 1,
            "collection_name": "test-collection"
        }
        mock_provider.delete_collection.return_value = True
        mock_provider.delete_all_points.return_value = True
        return mock_provider
    
    @staticmethod
    def create_mock_llm_provider() -> Mock:
        """Create a mock LLM provider for OCR tests."""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.call_llm.return_value = "This is a sample response from the LLM provider."
        mock_provider.call_llm_api.return_value = {
            "choices": [{"message": {"content": "This is a sample response from the LLM provider."}}]
        }
        mock_provider.get_model_info.return_value = {
            "model": "gpt-3.5-turbo",
            "provider": "openai",
            "max_tokens": 4096
        }
        return mock_provider
    
    @staticmethod
    def create_mock_ocr_providers() -> Dict[str, Mock]:
        """Create all mock providers needed for OCR tests."""
        return {
            "embedding_provider": OCRTestHelpers.create_mock_embedding_provider(),
            "vector_store_provider": OCRTestHelpers.create_mock_vector_store_provider(),
            "llm_provider": OCRTestHelpers.create_mock_llm_provider()
        }


class OCRProviderPatcher:
    """Context manager for patching provider retrieval in OCR tests."""
    
    def __init__(self, mock_providers: Dict[str, Mock]):
        self.mock_providers = mock_providers
        self.patches = []
    
    def __enter__(self):
        """Set up patches for provider retrieval."""
        # Patch the global provider functions
        self.patches.append(
            patch('app.infrastructure.providers.get_embedding_provider', 
                  return_value=self.mock_providers["embedding_provider"])
        )
        self.patches.append(
            patch('app.infrastructure.providers.get_vector_store_provider', 
                  return_value=self.mock_providers["vector_store_provider"])
        )
        self.patches.append(
            patch('app.infrastructure.providers.get_llm_provider', 
                  return_value=self.mock_providers["llm_provider"])
        )
        
        # Start all patches
        for p in self.patches:
            p.start()
        
        return self.mock_providers
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up patches."""
        for p in self.patches:
            p.stop()


def patch_ocr_providers_for_test():
    """Decorator/context manager for patching OCR providers in tests."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            mock_providers = OCRTestHelpers.create_mock_ocr_providers()
            with OCRProviderPatcher(mock_providers) as providers:
                return func(*args, **kwargs)
        return wrapper
    return decorator


def create_ocr_test_rag_service():
    """Create a RAGService instance with mock providers for OCR tests."""
    from app.domain.services.rag_service import RAGService
    
    mock_providers = OCRTestHelpers.create_mock_ocr_providers()
    
    return RAGService(
        embedding_provider=mock_providers["embedding_provider"],
        vector_store_provider=mock_providers["vector_store_provider"],
        llm_provider=mock_providers["llm_provider"]
    )


def create_ocr_test_vector_store():
    """Create a VectorStore instance with mock providers for OCR tests."""
    from app.infrastructure.vector_store.vector_store import VectorStore
    
    mock_providers = OCRTestHelpers.create_mock_ocr_providers()
    
    return VectorStore(
        embedding_provider=mock_providers["embedding_provider"],
        vector_store_provider=mock_providers["vector_store_provider"]
    )


# Helper functions for creating mock responses
def create_ocr_embedding_response(texts: List[str]) -> List[List[float]]:
    """Create mock embedding response for OCR texts."""
    return [[0.1, 0.2, 0.3] * 1536 for _ in texts]


def create_ocr_search_results(content: str = "Sample OCR extracted text") -> List[Dict[str, Any]]:
    """Create mock search results for OCR content."""
    return [
        {
            "content": content,
            "metadata": {
                "source": "test.pdf",
                "page": 0,
                "chunk_index": 0,
                "has_images": True
            },
            "score": 0.95
        }
    ]


def create_ocr_llm_response(answer: str = "This is a sample OCR-related answer.") -> str:
    """Create mock LLM response for OCR questions."""
    return answer


def create_ocr_llm_api_response(answer: str = "This is a sample OCR-related answer.") -> Dict[str, Any]:
    """Create mock LLM API response for OCR questions."""
    return {
        "choices": [
            {
                "message": {
                    "content": answer
                }
            }
        ]
    } 