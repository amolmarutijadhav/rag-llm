import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.api
class TestAPIEndpoints:
    """Test suite for API endpoints using sync client."""

    def test_health_check(self, sync_client):
        """Test health check endpoint."""
        response = sync_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_root_endpoint(self, sync_client):
        """Test root endpoint."""
        response = sync_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data

    @pytest.mark.rag
    def test_ask_question_success(self, sync_client, sample_question_response):
        """Test successful question asking."""
        with patch('app.api.routes.questions.rag_service') as mock_rag:
            mock_rag.ask_question = AsyncMock(return_value=sample_question_response)
            
            response = sync_client.post("/questions/ask", json={
                "question": "Who created Python?",
                "top_k": 3
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert "Python" in data["answer"]
            assert len(data["sources"]) > 0
            assert "score" in data["sources"][0]

    @pytest.mark.rag
    def test_ask_question_invalid_request(self, sync_client):
        """Test question asking with invalid request."""
        response = sync_client.post("/questions/ask", json={
            "invalid_field": "test"  # Invalid field instead of empty question
        })
        assert response.status_code == 422  # Validation error

    @pytest.mark.rag
    def test_ask_question_service_error(self, sync_client):
        """Test question asking when service fails."""
        with patch('app.api.routes.questions.rag_service') as mock_rag:
            mock_rag.ask_question = AsyncMock(side_effect=Exception("Service error"))
            
            response = sync_client.post("/questions/ask", json={
                "question": "Who created Python?",
                "top_k": 3
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    def test_upload_document_success(self, sync_client, sample_document_response):
        """Test successful document upload."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'test.txt' added successfully",
                "chunks_processed": 2
            }
            
            files = {"file": ("test.txt", b"Python is a programming language", "text/plain")}
            response = sync_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert data["chunks_processed"] == 2

    def test_upload_document_unsupported_format(self, sync_client):
        """Test document upload with unsupported format."""
        files = {"file": ("test.xyz", b"content", "application/octet-stream")}
        response = sync_client.post("/documents/upload", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported file format" in data["detail"]

    def test_upload_document_too_large(self, sync_client):
        """Test document upload with file too large."""
        # Create a large file content
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        
        files = {"file": ("large.txt", large_content, "text/plain")}
        response = sync_client.post("/documents/upload", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "File too large" in data["detail"]

    @pytest.mark.rag
    def test_add_text_success(self, sync_client, sample_document_response):
        """Test successful text addition."""
        with patch('app.api.routes.documents.rag_service.add_text') as mock_add_text:
            mock_add_text.return_value = {
                "success": True,
                "message": "Text from 'python_info' added successfully",
                "chunks_processed": 2
            }
            
            response = sync_client.post("/documents/add-text", json={
                "text": "Python is a programming language created by Guido van Rossum.",
                "source_name": "python_info"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert "added successfully" in data["message"]

    @pytest.mark.rag
    def test_add_text_empty_text(self, sync_client):
        """Test text addition with empty text."""
        response = sync_client.post("/documents/add-text", json={
            "text": "",
            "source_name": "empty"
        })
        assert response.status_code == 422  # Validation error

    def test_get_stats_success(self, sync_client, sample_stats_response):
        """Test successful stats retrieval."""
        with patch('app.api.routes.questions.rag_service') as mock_rag:
            mock_rag.get_stats.return_value = sample_stats_response
            
            response = sync_client.get("/questions/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert "vector_store" in data
            assert data["vector_store"]["total_documents"] == 10
            assert data["vector_store"]["vector_size"] == 1536

    def test_get_stats_service_error(self, sync_client):
        """Test stats retrieval when service fails."""
        with patch('app.api.routes.questions.rag_service') as mock_rag:
            mock_rag.get_stats.side_effect = Exception("Service error")
            
            response = sync_client.get("/questions/stats")
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    @pytest.mark.rag
    def test_clear_knowledge_base_success(self, sync_client, sample_document_response):
        """Test successful knowledge base clearing."""
        with patch('app.api.routes.questions.rag_service') as mock_rag:
            mock_rag.clear_knowledge_base.return_value = sample_document_response
            
            response = sync_client.delete("/documents/clear")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True

    @pytest.mark.rag
    def test_clear_knowledge_base_service_error(self, sync_client):
        """Test knowledge base clearing when service fails."""
        with patch('app.api.routes.documents.rag_service.clear_knowledge_base') as mock_clear:
            mock_clear.side_effect = Exception("Service error")
            
            response = sync_client.delete("/documents/clear")
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data


@pytest.mark.api
class TestAPIValidation:
    """Test API request validation."""

    def test_ask_question_missing_fields(self, sync_client):
        """Test question asking with missing required fields."""
        response = sync_client.post("/questions/ask", json={})
        assert response.status_code == 422

    def test_ask_question_invalid_top_k(self, sync_client):
        """Test question asking with invalid top_k value."""
        response = sync_client.post("/questions/ask", json={
            "question": "test",
            "top_k": -1  # Invalid negative value
        })
        assert response.status_code == 422

    def test_add_text_missing_text(self, sync_client):
        """Test text addition with missing text field."""
        response = sync_client.post("/documents/add-text", json={
            "source_name": "test"
        })
        assert response.status_code == 422

    def test_upload_document_missing_file(self, sync_client):
        """Test document upload with missing file."""
        response = sync_client.post("/documents/upload")
        assert response.status_code == 422 