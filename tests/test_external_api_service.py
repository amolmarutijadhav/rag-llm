import pytest
from unittest.mock import patch, AsyncMock
from src.external_api_service import ExternalAPIService
from src.config import Config

@pytest.mark.asyncio
class TestExternalAPIService:
    """Test suite for ExternalAPIService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.api_service = ExternalAPIService()
    
    @patch('httpx.AsyncClient.post')
    async def test_get_embeddings_success(self, mock_post):
        """Test successful embedding generation"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3] * 512}  # 1536 dimensions
            ]
        }
        mock_post.return_value = mock_response
        
        # Test
        texts = ["Hello world"]
        embeddings = await self.api_service.get_embeddings(texts)
        
        # Assertions
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 1536
        mock_post.assert_called_once()
    
    @patch('httpx.AsyncClient.put')
    async def test_insert_vectors_success(self, mock_put):
        """Test successful vector insertion"""
        # Mock response
        mock_response = AsyncMock()
        mock_put.return_value = mock_response
        
        # Test
        points = [
            {
                "id": "test-id",
                "vector": [0.1, 0.2, 0.3] * 512,
                "payload": {"content": "test content"}
            }
        ]
        result = await self.api_service.insert_vectors(points)
        
        # Assertions
        assert result is True
        mock_put.assert_called_once()
    
    @patch('httpx.AsyncClient.post')
    async def test_search_vectors_success(self, mock_post):
        """Test successful vector search"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "result": [
                {
                    "id": "test-id",
                    "score": 0.95,
                    "payload": {"content": "test content"}
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Test
        query_vector = [0.1, 0.2, 0.3] * 512
        results = await self.api_service.search_vectors(query_vector, 3)
        
        # Assertions
        assert len(results) == 1
        assert results[0]["score"] == 0.95
        mock_post.assert_called_once()
    
    @patch('httpx.AsyncClient.post')
    async def test_call_llm_success(self, mock_post):
        """Test successful LLM call"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is a test response"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Test
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        response = await self.api_service.call_llm(messages)
        
        # Assertions
        assert response == "This is a test response"
        mock_post.assert_called_once()
    
    def test_configuration_loaded(self):
        """Test that configuration is properly loaded"""
        assert hasattr(Config, 'EMBEDDING_API_URL')
        assert hasattr(Config, 'VECTOR_INSERT_API_URL')
        assert hasattr(Config, 'VECTOR_SEARCH_API_URL')
        assert hasattr(Config, 'LLM_API_URL')
        assert hasattr(Config, 'REQUEST_TIMEOUT')
        assert hasattr(Config, 'MAX_RETRIES')
    
    def test_headers_configured(self):
        """Test that headers are properly configured"""
        assert 'Authorization' in self.api_service.openai_headers
        assert 'Content-Type' in self.api_service.openai_headers
        assert 'api-key' in self.api_service.qdrant_headers
        assert 'Content-Type' in self.api_service.qdrant_headers 