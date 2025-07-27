import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, AsyncMock
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.domain.services.rag_service import RAGService
from app.infrastructure.vector_store.vector_store import VectorStore
from app.infrastructure.document_processing.loader import DocumentLoader


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def async_client():
    """HTTP client for testing API endpoints."""
    # Use TestClient for testing with correct constructor
    return TestClient(app)


@pytest.fixture
def sync_client():
    """Synchronous HTTP client for testing API endpoints."""
    return TestClient(app)


@pytest.fixture
def mock_rag_service():
    """Mock RAG service for unit testing."""
    mock_service = Mock(spec=RAGService)
    mock_service.ask_question = AsyncMock()
    mock_service.add_document = AsyncMock()
    mock_service.add_text = AsyncMock()
    mock_service.get_stats = Mock()
    mock_service.clear_knowledge_base = Mock()
    return mock_service


@pytest.fixture
def mock_vector_store():
    """Mock vector store for unit testing."""
    mock_store = Mock(spec=VectorStore)
    mock_store.add_documents = AsyncMock(return_value=True)
    mock_store.search = AsyncMock(return_value=[
        {
            "content": "Python was created by Guido van Rossum",
            "metadata": {"source": "test.txt"},
            "score": 0.95
        }
    ])
    mock_store.get_collection_stats = Mock(return_value={
        "total_documents": 0,
        "collection_name": "test_collection"
    })
    mock_store.delete_collection = Mock(return_value=True)
    mock_store.clear_all_points = Mock(return_value=True)
    return mock_store


@pytest.fixture
def mock_document_loader():
    """Mock document loader for unit testing."""
    mock_loader = Mock(spec=DocumentLoader)
    mock_loader.load_document = Mock(return_value=[
        {
            "id": "doc1",
            "content": "Python is a programming language",
            "metadata": {"source": "test.txt"}
        }
    ])
    mock_loader.load_text = Mock(return_value=[
        {
            "id": "text1",
            "content": "Python is a programming language",
            "metadata": {"source": "text_input", "chunk_index": 0}
        }
    ])
    return mock_loader


@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        {
            "id": "doc1",
            "content": "Python is a programming language created by Guido van Rossum.",
            "metadata": {"source": "test.txt", "page": 1}
        },
        {
            "id": "doc2", 
            "content": "Machine learning is a subset of artificial intelligence.",
            "metadata": {"source": "test.txt", "page": 2}
        }
    ]


@pytest.fixture
def sample_question_response():
    """Sample question response for testing."""
    return {
        "success": True,
        "answer": "Python was created by Guido van Rossum in 1991.",
        "sources": [
            {
                "content": "Python is a programming language created by Guido van Rossum.",
                "metadata": {"source": "test.txt"},
                "score": 0.95
            }
        ],
        "context_used": "Python is a programming language created by Guido van Rossum."
    }


@pytest.fixture
def sample_document_response():
    """Sample document response for testing."""
    return {
        "success": True,
        "message": "Document added successfully",
        "chunks_processed": 2
    }


@pytest.fixture
def sample_stats_response():
    """Sample stats response for testing."""
    return {
        "success": True,
        "vector_store": {
            "total_documents": 10,
            "collection_name": "test_collection",
            "vector_size": 1536
        },
        "supported_formats": [".pdf", ".txt", ".docx"],
        "chunk_size": 1000,
        "chunk_overlap": 200
    } 