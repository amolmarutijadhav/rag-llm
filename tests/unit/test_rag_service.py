import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.domain.services.rag_service import RAGService
from app.infrastructure.vector_store.vector_store import VectorStore
from app.infrastructure.document_processing.loader import DocumentLoader


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
        mock.load_document = Mock(return_value=[])
        mock.load_text = Mock(return_value=[])
        return mock

    @pytest.fixture
    def mock_api_service(self):
        """Mock external API service."""
        mock = Mock()
        mock.call_llm = AsyncMock(return_value="Test answer")
        return mock

    @pytest.fixture
    def rag_service(self, mock_vector_store, mock_document_loader, mock_api_service):
        """RAG service with mocked dependencies."""
        with patch('app.domain.services.rag_service.VectorStore', return_value=mock_vector_store), \
             patch('app.domain.services.rag_service.DocumentLoader', return_value=mock_document_loader), \
             patch('app.domain.services.rag_service.ExternalAPIService', return_value=mock_api_service):
            service = RAGService()
            # Replace the actual instances with mocks
            service.vector_store = mock_vector_store
            service.document_loader = mock_document_loader
            service.api_service = mock_api_service
            return service

    @pytest.mark.asyncio
    async def test_ask_question_success(self, rag_service, mock_vector_store, mock_api_service):
        """Test successful question asking."""
        # Mock search results
        mock_vector_store.search.return_value = [
            {
                "content": "Python was created by Guido van Rossum",
                "metadata": {"source": "test.txt"},
                "score": 0.95
            }
        ]
        
        # Mock LLM response
        mock_api_service.call_llm.return_value = "Python was created by Guido van Rossum."
        
        result = await rag_service.ask_question("Who created Python?", top_k=3)
        
        assert result["success"] == True
        assert "Python" in result["answer"]
        assert len(result["sources"]) == 1
        assert result["sources"][0]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_ask_question_no_results(self, rag_service, mock_vector_store):
        """Test question asking with no search results."""
        mock_vector_store.search.return_value = []
        
        result = await rag_service.ask_question("Unknown question", top_k=3)
        
        assert result["success"] == False
        assert len(result["sources"]) == 0

    @pytest.mark.asyncio
    async def test_ask_question_llm_error(self, rag_service, mock_vector_store, mock_api_service):
        """Test question asking when LLM fails."""
        mock_vector_store.search.return_value = [
            {"content": "test", "metadata": {}, "score": 0.9}
        ]
        
        mock_api_service.call_llm.side_effect = Exception("LLM error")
        
        result = await rag_service.ask_question("test", top_k=3)
        assert result["success"] == False
        assert "Error generating answer" in result["answer"]

    @pytest.mark.asyncio
    async def test_add_document_success(self, rag_service, mock_document_loader, mock_vector_store):
        """Test successful document addition."""
        # Mock document loading
        mock_document_loader.load_document.return_value = [
            {
                "id": "doc1",
                "content": "Python is a programming language",
                "metadata": {"source": "test.txt"}
            }
        ]
        
        result = await rag_service.add_document("test.txt")
        
        assert result["success"] == True
        assert result["chunks_processed"] == 1
        assert "test.txt" in result["message"]

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
        mock_document_loader.load_document.return_value = [
            {"id": "doc1", "content": "test", "metadata": {}}
        ]
        mock_vector_store.add_documents.return_value = False
        
        result = await rag_service.add_document("test.txt")
        
        assert result["success"] == False
        assert "Failed to add document" in result["message"]

    @pytest.mark.asyncio
    async def test_add_text_success(self, rag_service, mock_document_loader, mock_vector_store):
        """Test successful text addition."""
        # Mock text loading
        mock_document_loader.load_text.return_value = [
            {
                "id": "text1",
                "content": "Python is a programming language",
                "metadata": {"source": "python_info"}
            }
        ]
        
        result = await rag_service.add_text(
            "Python is a programming language",
            "python_info"
        )
        
        assert result["success"] == True
        assert "python_info" in result["message"]
        assert result["chunks_processed"] > 0

    @pytest.mark.asyncio
    async def test_add_text_empty(self, rag_service):
        """Test text addition with empty text."""
        result = await rag_service.add_text("", "empty")
        
        assert result["success"] == False
        assert "Error processing text" in result["message"]

    def test_get_stats_success(self, rag_service, mock_vector_store):
        """Test successful stats retrieval."""
        result = rag_service.get_stats()
        
        assert result["success"] == True
        assert "vector_store" in result
        assert "supported_formats" in result
        assert "chunk_size" in result

    def test_get_stats_vector_store_error(self, rag_service, mock_vector_store):
        """Test stats retrieval when vector store fails."""
        mock_vector_store.get_collection_stats.side_effect = Exception("Vector store error")
        
        result = rag_service.get_stats()
        
        assert result["success"] == False
        assert "Error getting stats" in result["message"]

    def test_clear_knowledge_base_success(self, rag_service, mock_vector_store):
        """Test successful knowledge base clearing."""
        mock_vector_store.clear_all_points.return_value = True
        
        result = rag_service.clear_knowledge_base()
        
        assert result["success"] == True
        assert "Knowledge base cleared" in result["message"]

    def test_clear_knowledge_base_error(self, rag_service, mock_vector_store):
        """Test knowledge base clearing when it fails."""
        mock_vector_store.clear_all_points.return_value = False
        
        result = rag_service.clear_knowledge_base()
        
        assert result["success"] == False
        assert "Failed to clear" in result["message"]


@pytest.mark.unit
class TestRAGServiceIntegration:
    """Test RAG service integration scenarios."""

    @pytest.mark.asyncio
    async def test_full_rag_workflow(self):
        """Test complete RAG workflow."""
        with patch('app.domain.services.rag_service.VectorStore') as mock_vs_class, \
             patch('app.domain.services.rag_service.DocumentLoader') as mock_dl_class, \
             patch('app.domain.services.rag_service.ExternalAPIService') as mock_api_class:
            
            # Setup mocks
            mock_vector_store = Mock()
            mock_vector_store.add_documents = AsyncMock(return_value=True)
            mock_vector_store.search = AsyncMock(return_value=[
                {"content": "Python info", "metadata": {}, "score": 0.9}
            ])
            mock_vector_store.get_collection_stats = Mock(return_value={
                "total_documents": 1,
                "collection_name": "test"
            })
            mock_vs_class.return_value = mock_vector_store
            
            mock_document_loader = Mock()
            mock_document_loader.load_document = Mock(return_value=[
                {"id": "doc1", "content": "Python info", "metadata": {}}
            ])
            mock_dl_class.return_value = mock_document_loader
            
            mock_api_service = Mock()
            mock_api_service.call_llm = AsyncMock(return_value="Python is a programming language")
            mock_api_class.return_value = mock_api_service
            
            # Create service and test workflow
            service = RAGService()
            
            # Test document addition
            result = await service.add_document("test.txt")
            assert result["success"] == True
            
            # Test question asking
            result = await service.ask_question("What is Python?")
            assert result["success"] == True
            assert "Python" in result["answer"] 