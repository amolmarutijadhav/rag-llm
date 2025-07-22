"""
Test helper utilities for common testing operations
"""

import json
import tempfile
import os
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock
import pytest
from fastapi.testclient import TestClient

def create_temp_file(content: str, extension: str = ".txt") -> str:
    """Create a temporary file with given content"""
    with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False) as f:
        f.write(content)
        return f.name

def cleanup_temp_file(file_path: str):
    """Clean up a temporary file"""
    if os.path.exists(file_path):
        os.unlink(file_path)

def assert_response_structure(response_data: Dict[str, Any], expected_fields: List[str]):
    """Assert that response has expected structure"""
    for field in expected_fields:
        assert field in response_data, f"Missing field: {field}"

def assert_success_response(response_data: Dict[str, Any]):
    """Assert that response indicates success"""
    assert "success" in response_data
    assert response_data["success"] is True

def assert_error_response(response_data: Dict[str, Any], expected_status: int = 400):
    """Assert that response indicates error"""
    assert "success" in response_data
    assert response_data["success"] is False

def create_mock_openai_response(content: str = "Test response") -> Dict[str, Any]:
    """Create a mock OpenAI API response"""
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15
        }
    }

def create_mock_embeddings_response(embedding_size: int = 1536) -> Dict[str, Any]:
    """Create a mock embeddings API response"""
    return {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": [0.1] * embedding_size,
                "index": 0
            }
        ],
        "model": "text-embedding-ada-002",
        "usage": {
            "prompt_tokens": 5,
            "total_tokens": 5
        }
    }

def create_mock_qdrant_search_response(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a mock Qdrant search response"""
    results = []
    for i, doc in enumerate(documents):
        results.append({
            "id": f"doc_{i}",
            "score": 0.9 - (i * 0.1),
            "payload": {
                "content": doc["content"],
                "metadata": doc.get("metadata", {})
            }
        })
    
    return {"result": results}

class MockExternalAPIService:
    """Mock external API service for testing"""
    
    def __init__(self):
        self.get_embeddings = AsyncMock(return_value=[[0.1] * 1536])
        self.insert_vectors = AsyncMock(return_value=True)
        self.search_vectors = AsyncMock(return_value=[])
        self.call_llm = AsyncMock(return_value="Mock response")
        self.call_openai_completions = AsyncMock(return_value=create_mock_openai_response())
        self.get_collection_stats = Mock(return_value={
            "total_documents": 0,
            "collection_name": "test_collection",
            "vector_size": 1536
        })
        self.delete_collection = Mock(return_value=True)

class MockVectorStore:
    """Mock vector store for testing"""
    
    def __init__(self):
        self.add_documents = AsyncMock(return_value=True)
        self.search = AsyncMock(return_value=[])
        self.get_collection_stats = Mock(return_value={
            "total_documents": 0,
            "collection_name": "test_collection"
        })
        self.delete_collection = Mock(return_value=True)

def assert_rag_metadata(response_data: Dict[str, Any]):
    """Assert that RAG metadata is present in chat completion response"""
    assert "rag_metadata" in response_data
    metadata = response_data["rag_metadata"]
    assert "agent_persona_preserved" in metadata
    assert "context_documents_found" in metadata
    assert "original_message_count" in metadata
    assert "enhanced_message_count" in metadata

def assert_chat_completion_response(response_data: Dict[str, Any]):
    """Assert that chat completion response has correct structure"""
    assert "id" in response_data
    assert "choices" in response_data
    assert len(response_data["choices"]) > 0
    assert "message" in response_data["choices"][0]
    assert "content" in response_data["choices"][0]["message"]

@pytest.fixture
def temp_file_factory():
    """Fixture for creating temporary files"""
    files = []
    
    def create_file(content: str, extension: str = ".txt") -> str:
        file_path = create_temp_file(content, extension)
        files.append(file_path)
        return file_path
    
    yield create_file
    
    # Cleanup
    for file_path in files:
        cleanup_temp_file(file_path) 