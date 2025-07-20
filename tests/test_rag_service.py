import pytest
from unittest.mock import Mock, patch
from src.rag_service import RAGService
from src.vector_store import VectorStore
from src.document_loader import DocumentLoader


@pytest.mark.unit
class TestRAGService:
    """Test suite for RAG service."""

    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store."""
        mock = Mock(spec=VectorStore)
        mock.add_documents = Mock(return_value=True)
        mock.search = Mock(return_value=[])
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
        return mock

    @pytest.fixture
    def rag_service(self, mock_vector_store, mock_document_loader):
        """RAG service with mocked dependencies."""
        with patch('src.rag_service.VectorStore', return_value=mock_vector_store), \
             patch('src.rag_service.DocumentLoader', return_value=mock_document_loader):
            service = RAGService()
            # Replace the actual instances with mocks
            service.vector_store = mock_vector_store
            service.document_loader = mock_document_loader
            return service

    def test_ask_question_success(self, rag_service, mock_vector_store):
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
        with patch.object(rag_service, 'llm') as mock_llm:
            mock_llm.invoke.return_value.content = "Python was created by Guido van Rossum."
            
            result = rag_service.ask_question("Who created Python?", top_k=3)
            
            assert result["success"] == True
            assert "Python" in result["answer"]
            assert len(result["sources"]) == 1
            assert result["sources"][0]["score"] == 0.95

    def test_ask_question_no_results(self, rag_service, mock_vector_store):
        """Test question asking with no search results."""
        mock_vector_store.search.return_value = []
        
        with patch.object(rag_service, 'llm') as mock_llm:
            mock_llm.invoke.return_value.content = "I don't have information about that."
            
            result = rag_service.ask_question("Unknown question", top_k=3)
            
            assert result["success"] == False
            assert len(result["sources"]) == 0

    def test_ask_question_llm_error(self, rag_service, mock_vector_store):
        """Test question asking when LLM fails."""
        mock_vector_store.search.return_value = [
            {"content": "test", "metadata": {}, "score": 0.9}
        ]
        
        with patch.object(rag_service, 'llm') as mock_llm:
            mock_llm.invoke.side_effect = Exception("LLM error")
            
            result = rag_service.ask_question("test", top_k=3)
            assert result["success"] == False
            assert "Error generating answer" in result["answer"]

    def test_add_document_success(self, rag_service, mock_document_loader, mock_vector_store):
        """Test successful document addition."""
        # Mock document loading
        mock_document_loader.load_document.return_value = [
            {
                "id": "doc1",
                "content": "Python is a programming language",
                "metadata": {"source": "test.txt"}
            }
        ]
        
        result = rag_service.add_document("test.txt")
        
        assert result["success"] == True
        assert result["chunks_processed"] == 1
        assert "test.txt" in result["message"]

    def test_add_document_loading_error(self, rag_service, mock_document_loader):
        """Test document addition when loading fails."""
        mock_document_loader.load_document.side_effect = Exception("Loading error")
        
        result = rag_service.add_document("test.txt")
        assert result["success"] == False
        assert "Error processing document" in result["message"]

    def test_add_document_vector_store_error(self, rag_service, mock_document_loader, mock_vector_store):
        """Test document addition when vector store fails."""
        mock_document_loader.load_document.return_value = [
            {"id": "doc1", "content": "test", "metadata": {}}
        ]
        mock_vector_store.add_documents.return_value = False
        
        result = rag_service.add_document("test.txt")
        
        assert result["success"] == False
        assert "Failed to add document" in result["message"]

    def test_add_text_success(self, rag_service, mock_document_loader, mock_vector_store):
        """Test successful text addition."""
        # Ensure the document loader is properly mocked
        rag_service.document_loader = mock_document_loader
        
        result = rag_service.add_text(
            "Python is a programming language",
            "python_info"
        )
        
        print(f"Add text result: {result}")
        
        assert result["success"] == True
        assert "python_info" in result["message"]
        assert result["chunks_processed"] > 0

    def test_add_text_empty(self, rag_service):
        """Test text addition with empty text."""
        result = rag_service.add_text("", "empty")
        
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
        mock_vector_store.delete_collection.return_value = True
        
        result = rag_service.clear_knowledge_base()
        
        assert result["success"] == True
        assert "Knowledge base cleared" in result["message"]

    def test_clear_knowledge_base_error(self, rag_service, mock_vector_store):
        """Test knowledge base clearing when it fails."""
        mock_vector_store.delete_collection.return_value = False
        
        result = rag_service.clear_knowledge_base()
        
        assert result["success"] == False
        assert "Failed to clear" in result["message"]


@pytest.mark.unit
class TestRAGServiceIntegration:
    """Test RAG service integration scenarios."""

    def test_full_rag_workflow(self):
        """Test complete RAG workflow."""
        with patch('src.rag_service.VectorStore') as mock_vs_class, \
             patch('src.rag_service.DocumentLoader') as mock_dl_class, \
             patch('src.rag_service.ChatOpenAI') as mock_llm_class:
            
            # Setup mocks
            mock_vector_store = Mock()
            mock_vector_store.add_documents = Mock(return_value=True)
            mock_vector_store.search = Mock(return_value=[
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
            
            mock_llm = Mock()
            mock_llm.invoke.return_value.content = "Python is a programming language."
            mock_llm_class.return_value = mock_llm
            
            # Create service
            service = RAGService()
            
            # Test document addition
            doc_result = service.add_document("test.txt")
            assert doc_result["success"] == True
            
            # Test question asking
            q_result = service.ask_question("What is Python?")
            assert q_result["success"] == True
            assert "Python" in q_result["answer"]
            
            # Test stats
            stats_result = service.get_stats()
            assert stats_result["success"] == True
            assert stats_result["vector_store"]["total_documents"] == 1 