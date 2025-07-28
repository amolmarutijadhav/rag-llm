import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.domain.services.rag_service import RAGService
from app.infrastructure.vector_store.vector_store import VectorStore
from app.infrastructure.document_processing.loader import DocumentLoader
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider, VectorStoreProvider


@pytest.mark.unit
class TestRAGService:
    """Test suite for RAG service."""

    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store."""
        mock = Mock(spec=VectorStore)
        mock.add_documents = AsyncMock(return_value=True)
        mock.search = AsyncMock(return_value=[])
        mock.get_collection_stats = Mock(return_value={
            "total_documents": 0,
            "collection_name": "test"
        })
        return mock

    @pytest.fixture
    def mock_document_loader(self):
        """Mock document loader."""
        mock = Mock(spec=DocumentLoader)
        mock.load_document = Mock(return_value=([], None))  # (documents, ocr_text)
        mock.load_text = Mock(return_value=[])
        return mock

    @pytest.fixture
    def mock_embedding_provider(self):
        """Mock embedding provider."""
        mock = Mock(spec=EmbeddingProvider)
        mock.get_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
        mock.get_model_info = Mock(return_value={
            "provider": "test",
            "model": "test-model",
            "vector_size": 1536
        })
        return mock

    @pytest.fixture
    def mock_llm_provider(self):
        """Mock LLM provider."""
        mock = Mock(spec=LLMProvider)
        mock.call_llm = AsyncMock(return_value="Test answer")
        mock.call_llm_api = AsyncMock(return_value="Test answer")
        mock.get_model_info = Mock(return_value={
            "provider": "test",
            "default_model": "test-model"
        })
        return mock

    @pytest.fixture
    def mock_vector_store_provider(self):
        """Mock vector store provider."""
        mock = Mock(spec=VectorStoreProvider)
        mock.insert_vectors = AsyncMock(return_value=True)
        mock.search_vectors = AsyncMock(return_value=[])
        mock.get_collection_stats = Mock(return_value={
            "total_documents": 0,
            "collection_name": "test"
        })
        mock.create_collection_if_not_exists = AsyncMock(return_value=True)
        mock.delete_collection = Mock(return_value=True)
        mock.delete_all_points = Mock(return_value=True)
        return mock

    @pytest.fixture
    def rag_service(self, mock_vector_store, mock_document_loader, 
                   mock_embedding_provider, mock_llm_provider, mock_vector_store_provider):
        """RAG service with mocked dependencies."""
        with patch('app.domain.services.rag_service.VectorStore', return_value=mock_vector_store), \
             patch('app.domain.services.rag_service.DocumentLoader', return_value=mock_document_loader):
            service = RAGService(
                embedding_provider=mock_embedding_provider,
                llm_provider=mock_llm_provider,
                vector_store_provider=mock_vector_store_provider
            )
            # Replace the actual instances with mocks
            service.vector_store = mock_vector_store
            service.document_loader = mock_document_loader
            return service

    @pytest.mark.asyncio
    async def test_ask_question_success(self, rag_service, mock_vector_store_provider, mock_llm_provider):
        """Test successful question asking."""
        # Mock search results
        mock_vector_store_provider.search_vectors.return_value = [
            {
                "payload": {
                    "content": "Python was created by Guido van Rossum",
                    "metadata": {"source": "test.txt"}
                },
                "score": 0.95
            }
        ]
        
        # Mock LLM response
        mock_llm_provider.call_llm.return_value = "Python was created by Guido van Rossum."
        
        result = await rag_service.ask_question("Who created Python?", top_k=3)
        
        assert result["success"] == True
        assert "Python" in result["answer"]
        assert len(result["sources"]) == 1
        assert result["sources"][0]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_ask_question_no_results(self, rag_service, mock_vector_store_provider):
        """Test question asking with no search results."""
        mock_vector_store_provider.search_vectors.return_value = []
        
        result = await rag_service.ask_question("Unknown question", top_k=3)
        
        assert result["success"] == False
        assert len(result["sources"]) == 0

    @pytest.mark.asyncio
    async def test_ask_question_llm_error(self, rag_service, mock_vector_store_provider, mock_llm_provider):
        """Test question asking when LLM fails."""
        mock_vector_store_provider.search_vectors.return_value = [
            {"payload": {"content": "test", "metadata": {}}, "score": 0.9}
        ]
        
        mock_llm_provider.call_llm.side_effect = Exception("LLM error")
        
        result = await rag_service.ask_question("test", top_k=3)
        assert result["success"] == False
        assert "Error processing question" in result["answer"]

    @pytest.mark.asyncio
    async def test_add_document_success(self, rag_service, mock_document_loader, mock_vector_store):
        """Test successful document addition."""
        # Mock document loading - returns tuple (documents, ocr_text)
        mock_document_loader.load_document.return_value = ([
            {"content": "test content", "metadata": {"source": "test.txt"}}
        ], "extracted ocr text")
        
        result = await rag_service.add_document("test.txt")
        
        assert result["success"] == True
        assert "added successfully" in result["message"]
        assert result["chunks_processed"] == 1
        assert result["extracted_text"] == "extracted ocr text"

    @pytest.mark.asyncio
    async def test_add_document_loading_error(self, rag_service, mock_document_loader):
        """Test document addition when loading fails."""
        mock_document_loader.load_document.side_effect = Exception("Loading error")
        
        result = await rag_service.add_document("test.txt")
        
        assert result["success"] == False
        assert "Error processing document" in result["message"]

    @pytest.mark.asyncio
    async def test_add_document_vector_store_error(self, rag_service, mock_document_loader, mock_vector_store):
        """Test document addition when vector store fails."""
        mock_document_loader.load_document.return_value = ([
            {"content": "test content", "metadata": {"source": "test.txt"}}
        ], None)
        mock_vector_store.add_documents.return_value = False
        
        result = await rag_service.add_document("test.txt")
        
        assert result["success"] == False
        assert "Failed to add document" in result["message"]

    @pytest.mark.asyncio
    async def test_add_text_success(self, rag_service, mock_document_loader, mock_vector_store):
        """Test successful text addition."""
        mock_document_loader.load_text.return_value = [
            {"content": "test content", "metadata": {"source": "test_input"}}
        ]
        
        result = await rag_service.add_text("test content", "test_input")
        
        assert result["success"] == True
        assert "added successfully" in result["message"]
        assert result["chunks_processed"] == 1

    @pytest.mark.asyncio
    async def test_add_text_empty(self, rag_service):
        """Test text addition with empty text."""
        result = await rag_service.add_text("", "test_input")
        
        assert result["success"] == False
        assert "Text cannot be empty" in result["message"]

    def test_get_stats_success(self, rag_service, mock_vector_store_provider, mock_embedding_provider, mock_llm_provider):
        """Test successful stats retrieval."""
        result = rag_service.get_stats()
        
        assert result["success"] == True
        assert "vector_store" in result
        assert "total_documents" in result["vector_store"]
        assert "collection_name" in result["vector_store"]
        assert "vector_size" in result["vector_store"]
        assert "supported_formats" in result
        assert "chunk_size" in result
        assert "chunk_overlap" in result

    def test_get_stats_vector_store_error(self, rag_service, mock_vector_store_provider):
        """Test stats retrieval when vector store fails."""
        mock_vector_store_provider.get_collection_stats.side_effect = Exception("Stats error")
        
        result = rag_service.get_stats()
        
        assert result["success"] == False
        assert "Error getting statistics" in result["message"]

    def test_clear_knowledge_base_success(self, rag_service, mock_vector_store_provider):
        """Test successful knowledge base clearing."""
        result = rag_service.clear_knowledge_base()
        
        assert result["success"] == True
        assert "cleared successfully" in result["message"]

    def test_clear_knowledge_base_error(self, rag_service, mock_vector_store_provider):
        """Test knowledge base clearing when it fails."""
        mock_vector_store_provider.delete_all_points.return_value = False
        
        result = rag_service.clear_knowledge_base()
        
        assert result["success"] == False
        assert "Failed to clear" in result["message"]


@pytest.mark.unit
class TestRAGServiceIntegration:
    """Integration tests for RAG service."""

    @pytest.mark.asyncio
    async def test_full_rag_workflow(self):
        """Test complete RAG workflow with mocked providers."""
        # Create mock providers
        mock_embedding_provider = Mock(spec=EmbeddingProvider)
        mock_embedding_provider.get_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
        mock_embedding_provider.get_model_info = Mock(return_value={"provider": "test"})
        
        mock_llm_provider = Mock(spec=LLMProvider)
        mock_llm_provider.call_llm = AsyncMock(return_value="Test answer")
        mock_llm_provider.get_model_info = Mock(return_value={"provider": "test"})
        
        mock_vector_store_provider = Mock(spec=VectorStoreProvider)
        mock_vector_store_provider.insert_vectors = AsyncMock(return_value=True)
        mock_vector_store_provider.search_vectors = AsyncMock(return_value=[
            {"payload": {"content": "test content"}, "score": 0.9}
        ])
        mock_vector_store_provider.get_collection_stats = Mock(return_value={"total_documents": 1})
        
        # Create RAG service with mock providers
        rag_service = RAGService(
            embedding_provider=mock_embedding_provider,
            llm_provider=mock_llm_provider,
            vector_store_provider=mock_vector_store_provider
        )
        
        # Test the workflow
        result = await rag_service.ask_question("test question")
        
        assert result["success"] == True
        assert "Test answer" in result["answer"] 