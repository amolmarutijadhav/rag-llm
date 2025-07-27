"""
Test helpers for the new provider architecture.
These helpers make it easier to mock providers in integration tests.
"""

from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider, VectorStoreProvider


class MockProviderHelper:
    """Helper class for creating mock providers for testing."""
    
    @staticmethod
    def create_mock_embedding_provider() -> Mock:
        """Create a mock embedding provider."""
        mock = Mock(spec=EmbeddingProvider)
        mock.get_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3] * 512])  # 1536 dimensions
        mock.get_model_info = Mock(return_value={
            "provider": "test",
            "model": "test-embedding-model",
            "vector_size": 1536
        })
        return mock
    
    @staticmethod
    def create_mock_llm_provider() -> Mock:
        """Create a mock LLM provider."""
        mock = Mock(spec=LLMProvider)
        mock.call_llm = AsyncMock(return_value="This is a test response from the LLM.")
        mock.call_llm_api = AsyncMock(return_value={
            "choices": [
                {
                    "message": {
                        "content": "This is a test response from the LLM."
                    }
                }
            ],
            "usage": {"total_tokens": 10}
        })
        mock.get_model_info = Mock(return_value={
            "provider": "test",
            "default_model": "test-llm-model"
        })
        return mock
    
    @staticmethod
    def create_mock_vector_store_provider() -> Mock:
        """Create a mock vector store provider."""
        mock = Mock(spec=VectorStoreProvider)
        mock.insert_vectors = AsyncMock(return_value=True)
        mock.search_vectors = AsyncMock(return_value=[])
        mock.get_collection_stats = Mock(return_value={
            "total_documents": 0,
            "collection_name": "test_collection",
            "vector_size": 1536
        })
        mock.create_collection_if_not_exists = AsyncMock(return_value=True)
        mock.delete_collection = Mock(return_value=True)
        mock.delete_all_points = Mock(return_value=True)
        return mock


def patch_providers_for_test():
    """
    Context manager to patch all providers for testing.
    Returns a tuple of (embedding_mock, llm_mock, vector_store_mock)
    """
    embedding_mock = MockProviderHelper.create_mock_embedding_provider()
    llm_mock = MockProviderHelper.create_mock_llm_provider()
    vector_store_mock = MockProviderHelper.create_mock_vector_store_provider()
    
    patches = [
        patch('app.infrastructure.providers.get_embedding_provider', return_value=embedding_mock),
        patch('app.infrastructure.providers.get_llm_provider', return_value=llm_mock),
        patch('app.infrastructure.providers.get_vector_store_provider', return_value=vector_store_mock)
    ]
    
    return patches, (embedding_mock, llm_mock, vector_store_mock)


def patch_providers_for_rag_service():
    """
    Context manager to patch providers specifically for RAG service tests.
    Returns a tuple of (embedding_mock, llm_mock, vector_store_mock)
    """
    embedding_mock = MockProviderHelper.create_mock_embedding_provider()
    llm_mock = MockProviderHelper.create_mock_llm_provider()
    vector_store_mock = MockProviderHelper.create_mock_vector_store_provider()
    
    patches = [
        patch('app.domain.services.rag_service.get_embedding_provider', return_value=embedding_mock),
        patch('app.domain.services.rag_service.get_llm_provider', return_value=llm_mock),
        patch('app.domain.services.rag_service.get_vector_store_provider', return_value=vector_store_mock)
    ]
    
    return patches, (embedding_mock, llm_mock, vector_store_mock)


def patch_providers_for_vector_store():
    """
    Context manager to patch providers specifically for VectorStore tests.
    Returns a tuple of (embedding_mock, vector_store_mock)
    """
    embedding_mock = MockProviderHelper.create_mock_embedding_provider()
    vector_store_mock = MockProviderHelper.create_mock_vector_store_provider()
    
    patches = [
        patch('app.infrastructure.vector_store.vector_store.get_embedding_provider', return_value=embedding_mock),
        patch('app.infrastructure.vector_store.vector_store.get_vector_store_provider', return_value=vector_store_mock)
    ]
    
    return patches, (embedding_mock, vector_store_mock)


def patch_providers_for_chat_route():
    """
    Context manager to patch providers specifically for chat route tests.
    Returns the LLM mock.
    """
    llm_mock = MockProviderHelper.create_mock_llm_provider()
    
    patches = [
        patch('app.api.routes.chat.get_llm_provider', return_value=llm_mock)
    ]
    
    return patches, llm_mock


def create_search_results_with_content(content_list: List[str]) -> List[Dict[str, Any]]:
    """
    Create mock search results with specified content.
    
    Args:
        content_list: List of content strings to include in search results
        
    Returns:
        List of mock search result dictionaries
    """
    results = []
    for i, content in enumerate(content_list):
        result = {
            "payload": {
                "content": content,
                "metadata": {"source": f"test_source_{i}"}
            },
            "score": 0.9 - (i * 0.1)  # Decreasing scores
        }
        results.append(result)
    return results


def create_embedding_response_for_texts(texts: List[str]) -> List[List[float]]:
    """
    Create mock embedding responses for a list of texts.
    
    Args:
        texts: List of text strings
        
    Returns:
        List of embedding vectors (each vector is 1536 dimensions)
    """
    return [[0.1, 0.2, 0.3] * 512 for _ in texts]  # 1536 dimensions


def create_llm_response_for_question(question: str, context: str = "") -> str:
    """
    Create a mock LLM response for a given question.
    
    Args:
        question: The question being asked
        context: Optional context to include in response
        
    Returns:
        Mock LLM response string
    """
    if context:
        return f"Based on the context: {context}. Answer to '{question}': This is a test response."
    else:
        return f"Answer to '{question}': This is a test response from the LLM."


def create_llm_api_response_for_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a mock LLM API response for a given request.
    
    Args:
        request: The LLM API request
        
    Returns:
        Mock LLM API response dictionary
    """
    messages = request.get("messages", [])
    last_user_message = ""
    
    # Extract the last user message
    for message in reversed(messages):
        if message.get("role") == "user":
            last_user_message = message.get("content", "")
            break
    
    return {
        "choices": [
            {
                "message": {
                    "content": f"Response to: {last_user_message}"
                }
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "model": request.get("model", "test-model"),
        "id": "test-response-id"
    } 