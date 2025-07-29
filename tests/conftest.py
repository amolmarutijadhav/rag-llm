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
def clean_app():
    """Create a clean app instance for each test to avoid shared state issues."""
    # Import here to ensure we get a fresh app instance
    from app.main import app as fresh_app
    return fresh_app


@pytest.fixture
def async_client(clean_app):
    """HTTP client for testing API endpoints."""
    # Use TestClient for testing with correct constructor
    return TestClient(clean_app)


@pytest.fixture
async def async_client_real(clean_app):
    """Real async HTTP client for testing API endpoints."""
    async with AsyncClient(app=clean_app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sync_client(clean_app):
    """Synchronous HTTP client for testing API endpoints."""
    return TestClient(clean_app)


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


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for enhanced chat completion testing."""
    mock_provider = Mock()
    mock_provider.call_llm = AsyncMock(return_value="This is a test response from the LLM.")
    mock_provider.call_llm_api = AsyncMock(return_value={
        "choices": [
            {
                "message": {
                    "content": "This is a test response from the LLM."
                }
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    })
    return mock_provider


@pytest.fixture
def mock_enhanced_chat_completion_service(mock_rag_service, mock_llm_provider):
    """Mock enhanced chat completion service for testing."""
    from app.domain.services.enhanced_chat_completion_service import EnhancedChatCompletionService
    
    # Create a mock service that returns a proper response
    mock_service = Mock(spec=EnhancedChatCompletionService)
    mock_service.process_request = AsyncMock(return_value={
        "id": "chatcmpl-test-123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the enhanced chat completion service."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "sources": [
            {
                "content": "Test source content",
                "metadata": {"source": "test.txt"},
                "score": 0.95
            }
        ],
        "metadata": {
            "conversation_aware": True,
            "strategy_used": "topic_tracking",
            "enhanced_queries_count": 3,
            "conversation_context": {
                "topics": ["test", "topic"],
                "entities": ["test"],
                "conversation_length": 2
            },
            "processing_plugins": ["conversation_context", "multi_query_rag", "response_enhancement"]
        }
    })
    
    return mock_service 