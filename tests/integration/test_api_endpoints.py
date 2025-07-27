import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from fastapi import HTTPException

from app.main import app


@pytest.mark.api
class TestAPIEndpoints:
    """Test suite for API endpoints."""

    def test_health_check(self, async_client):
        """Test health check endpoint."""
        response = async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_root_endpoint(self, async_client):
        """Test root endpoint."""
        response = async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    @pytest.mark.rag
    @patch('app.api.routes.questions.rag_service.ask_question')
    def test_ask_question_success(self, mock_ask_question, async_client):
        """Test successful question asking."""
        # Mock RAG service response
        mock_ask_question.return_value = {
            "success": True,
            "answer": "Python was created by Guido van Rossum.",
            "sources": [
                {
                    "content": "Python is a programming language created by Guido van Rossum.",
                    "metadata": {"source": "test.txt"},
                    "score": 0.95
                }
            ]
        }

        response = async_client.post("/questions/ask", json={
            "question": "Who created Python?",
            "top_k": 3
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Python was created by Guido van Rossum" in data["answer"]
        assert len(data["sources"]) == 1

    @pytest.mark.rag
    def test_ask_question_invalid_request(self, async_client):
        """Test question asking with invalid request."""
        response = async_client.post("/questions/ask", json={
            "invalid_field": "test"
        })

        assert response.status_code == 422  # Validation error

    @pytest.mark.rag
    @patch('app.api.routes.questions.rag_service.ask_question')
    def test_ask_question_service_error(self, mock_ask_question, async_client):
        """Test question asking with service error."""
        # Mock RAG service error
        mock_ask_question.return_value = {
            "success": False,
            "answer": "Error processing request",
            "sources": []
        }

        response = async_client.post("/questions/ask", json={
            "question": "Test question?"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "Error processing request" in data["answer"]

    @pytest.mark.rag
    @patch('app.api.routes.documents.rag_service.add_document')
    def test_add_document_success(self, mock_add_document, async_client):
        """Test successful document upload."""
        # Mock RAG service response
        mock_add_document.return_value = {
            "success": True,
            "message": "Document 'test.txt' added successfully",
            "chunks_processed": 5
        }

        # Create a mock file
        from io import BytesIO
        file_content = b"This is a test document content."
        files = {"file": ("test.txt", BytesIO(file_content), "text/plain")}

        response = async_client.post("/documents/upload", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "added successfully" in data["message"]

    @pytest.mark.rag
    def test_add_document_invalid_format(self, async_client):
        """Test document upload with invalid format."""
        # Create a mock file with invalid format
        from io import BytesIO
        file_content = b"This is a test document content."
        files = {"file": ("test.xyz", BytesIO(file_content), "application/octet-stream")}

        response = async_client.post("/documents/upload", files=files)

        assert response.status_code == 400
        data = response.json()
        assert "Unsupported file format" in data["detail"]

    @pytest.mark.rag
    @patch('app.api.routes.questions.rag_service')
    def test_add_text_success(self, mock_rag_service, async_client):
        """Test successful text addition."""
        # Mock RAG service response
        mock_rag_service.add_text.return_value = {
            "success": True,
            "message": "Text added successfully",
            "chunks_processed": 2
        }

        response = async_client.post("/documents/add-text", json={
            "text": "This is some test text to add to the knowledge base.",
            "source_name": "test_input"
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "added successfully" in data["message"]

    @pytest.mark.rag
    def test_add_text_empty(self, async_client):
        """Test text addition with empty text."""
        response = async_client.post("/documents/add-text", json={
            "text": "",
            "source_name": "test_input"
        })

        assert response.status_code == 422  # Validation error for empty text

    @pytest.mark.rag
    @patch('app.api.routes.questions.rag_service')
    def test_get_stats_success(self, mock_rag_service, async_client):
        """Test successful stats retrieval."""
        # Mock RAG service response
        mock_rag_service.get_stats.return_value = {
            "success": True,
            "vector_store": {
                "total_documents": 10,
                "collection_name": "test_collection"
            },
            "supported_formats": [".pdf", ".txt", ".docx"],
            "chunk_size": 1000,
            "chunk_overlap": 200
        }

        response = async_client.get("/questions/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "vector_store" in data
        assert "supported_formats" in data

    @pytest.mark.api
    def test_docs_endpoint(self, async_client):
        """Test that docs endpoint is accessible."""
        response = async_client.get("/docs")
        assert response.status_code == 200 