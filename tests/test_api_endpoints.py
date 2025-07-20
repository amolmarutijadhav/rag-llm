import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from fastapi import HTTPException

from src.main import app


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
        assert data["version"] == "1.0.0"
        assert "timestamp" in data

    @pytest.mark.rag
    def test_ask_question_success(self, async_client, sample_question_response):
        """Test successful question asking."""
        with patch('src.main.rag_service') as mock_rag:
            mock_rag.ask_question.return_value = sample_question_response
            
            response = async_client.post("/ask", json={
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
    async def test_ask_question_invalid_request(self, async_client: AsyncClient):
        """Test question asking with invalid request."""
        response = await async_client.post("/ask", json={
            "question": "",  # Empty question
            "top_k": 3
        })
        assert response.status_code == 422  # Validation error

    @pytest.mark.rag
    async def test_ask_question_service_error(self, async_client: AsyncClient):
        """Test question asking when service fails."""
        with patch('src.main.rag_service') as mock_rag:
            mock_rag.ask_question.side_effect = Exception("Service error")
            
            response = await async_client.post("/ask", json={
                "question": "Who created Python?",
                "top_k": 3
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    async def test_upload_document_success(self, async_client: AsyncClient, sample_document_response):
        """Test successful document upload."""
        with patch('src.main.rag_service') as mock_rag:
            mock_rag.add_document.return_value = sample_document_response
            
            files = {"file": ("test.txt", b"Python is a programming language", "text/plain")}
            response = await async_client.post("/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert data["chunks_added"] == 2

    async def test_upload_document_unsupported_format(self, async_client: AsyncClient):
        """Test document upload with unsupported format."""
        files = {"file": ("test.xyz", b"content", "application/octet-stream")}
        response = await async_client.post("/upload", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported file format" in data["detail"]

    async def test_upload_document_too_large(self, async_client: AsyncClient):
        """Test document upload with file too large."""
        # Create a large file content
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        
        files = {"file": ("large.txt", large_content, "text/plain")}
        response = await async_client.post("/upload", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "File too large" in data["detail"]

    @pytest.mark.rag
    async def test_add_text_success(self, async_client: AsyncClient, sample_document_response):
        """Test successful text addition."""
        with patch('src.main.rag_service') as mock_rag:
            mock_rag.add_text.return_value = sample_document_response
            
            response = await async_client.post("/add-text", json={
                "text": "Python is a programming language created by Guido van Rossum.",
                "source_name": "python_info"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert data["source_name"] == "python_info"

    @pytest.mark.rag
    async def test_add_text_empty_text(self, async_client: AsyncClient):
        """Test text addition with empty text."""
        response = await async_client.post("/add-text", json={
            "text": "",
            "source_name": "empty"
        })
        assert response.status_code == 422  # Validation error

    async def test_get_stats_success(self, async_client: AsyncClient, sample_stats_response):
        """Test successful stats retrieval."""
        with patch('src.main.rag_service') as mock_rag:
            mock_rag.get_stats.return_value = sample_stats_response
            
            response = await async_client.get("/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True
            assert "vector_store" in data
            assert data["vector_store"]["total_documents"] == 10
            assert data["vector_store"]["vector_size"] == 1536

    async def test_get_stats_service_error(self, async_client: AsyncClient):
        """Test stats retrieval when service fails."""
        with patch('src.main.rag_service') as mock_rag:
            mock_rag.get_stats.side_effect = Exception("Service error")
            
            response = await async_client.get("/stats")
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    @pytest.mark.rag
    async def test_clear_knowledge_base_success(self, async_client: AsyncClient, sample_document_response):
        """Test successful knowledge base clearing."""
        with patch('src.main.rag_service') as mock_rag:
            mock_rag.clear_knowledge_base.return_value = sample_document_response
            
            response = await async_client.delete("/clear")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] == True

    @pytest.mark.rag
    async def test_clear_knowledge_base_service_error(self, async_client: AsyncClient):
        """Test knowledge base clearing when service fails."""
        with patch('src.main.rag_service') as mock_rag:
            mock_rag.clear_knowledge_base.side_effect = Exception("Service error")
            
            response = await async_client.delete("/clear")
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data


@pytest.mark.api
@pytest.mark.asyncio
class TestAPIValidation:
    """Test API request validation."""

    async def test_ask_question_missing_fields(self, async_client: AsyncClient):
        """Test question asking with missing required fields."""
        response = await async_client.post("/ask", json={})
        assert response.status_code == 422

    async def test_ask_question_invalid_top_k(self, async_client: AsyncClient):
        """Test question asking with invalid top_k value."""
        response = await async_client.post("/ask", json={
            "question": "test",
            "top_k": -1  # Invalid negative value
        })
        assert response.status_code == 422

    async def test_add_text_missing_text(self, async_client: AsyncClient):
        """Test text addition with missing text field."""
        response = await async_client.post("/add-text", json={
            "source_name": "test"
        })
        assert response.status_code == 422

    async def test_upload_document_missing_file(self, async_client: AsyncClient):
        """Test document upload with missing file."""
        response = await async_client.post("/upload")
        assert response.status_code == 422 