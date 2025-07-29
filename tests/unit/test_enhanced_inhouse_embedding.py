"""
Unit tests for the enhanced InhouseEmbeddingProvider with single text processing.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.infrastructure.providers.inhouse_provider import InhouseEmbeddingProvider


class TestInhouseEmbeddingProvider:
    """Test cases for enhanced InhouseEmbeddingProvider."""
    
    @pytest.fixture
    def basic_config(self):
        """Basic configuration for testing."""
        return {
            "api_url": "https://test-embeddings.com/api/v1/embed",
            "api_key": "test-api-key",
            "model": "test-embedding-model",
            "max_concurrent_requests": 3,
            "request_delay": 0.1
        }
    
    @pytest.fixture
    def provider(self, basic_config):
        """Create provider instance for testing."""
        return InhouseEmbeddingProvider(basic_config)
    
    def test_initialization(self, basic_config):
        """Test provider initialization with enhanced configuration."""
        provider = InhouseEmbeddingProvider(basic_config)
        
        assert provider.api_url == "https://test-embeddings.com/api/v1/embed"
        assert provider.api_key == "test-api-key"
        assert provider.model == "test-embedding-model"
        assert provider.max_concurrent_requests == 3
        assert provider.request_delay == 0.1
    
    def test_initialization_defaults(self):
        """Test provider initialization with default values."""
        config = {
            "api_url": "https://test-embeddings.com/api/v1/embed",
            "api_key": "test-api-key"
        }
        
        provider = InhouseEmbeddingProvider(config)
        
        assert provider.max_concurrent_requests == 5  # Default value
        assert provider.request_delay == 0.1  # Default value
    
    def test_initialization_missing_url(self):
        """Test initialization fails without API URL."""
        config = {
            "api_key": "test-api-key"
        }
        
        with pytest.raises(ValueError, match="In-house embedding API URL is required"):
            InhouseEmbeddingProvider(config)
    
    @pytest.mark.asyncio
    async def test_get_single_embedding_success(self, provider):
        """Test successful single embedding generation."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
        
        with patch.object(provider, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await provider.get_single_embedding("test text")
            
            # Verify request was made correctly
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "POST"  # method
            assert call_args[0][1] == provider.api_url  # url
            
            # Verify payload structure
            payload = call_args[1]['data']
            assert payload["text"] == "test text"
            assert payload["embeddings_model"] == provider.model
            assert payload["format"] == "vector"
            
            # Verify result
            assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
    
    @pytest.mark.asyncio
    async def test_get_single_embedding_different_formats(self, provider):
        """Test single embedding with different response formats."""
        test_cases = [
            # Format 1: Direct embedding
            ({"embedding": [0.1, 0.2, 0.3]}, [0.1, 0.2, 0.3]),
            # Format 2: Vector field
            ({"vector": [0.4, 0.5, 0.6]}, [0.4, 0.5, 0.6]),
            # Format 3: Data array
            ({"data": [{"embedding": [0.7, 0.8, 0.9]}]}, [0.7, 0.8, 0.9]),
            # Format 4: Embeddings array
            ({"embeddings": [[0.1, 0.2, 0.3]]}, [0.1, 0.2, 0.3])
        ]
        
        for response_data, expected_embedding in test_cases:
            mock_response = MagicMock()
            mock_response.json.return_value = response_data
            
            with patch.object(provider, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                result = await provider.get_single_embedding("test text")
                assert result == expected_embedding
    
    @pytest.mark.asyncio
    async def test_get_single_embedding_unknown_format(self, provider):
        """Test single embedding with unknown response format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"unknown_field": [0.1, 0.2, 0.3]}
        
        with patch.object(provider, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            with pytest.raises(Exception, match="In-house single embedding API error: Unknown embedding response format"):
                await provider.get_single_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_get_single_embedding_failure(self, provider):
        """Test single embedding failure handling."""
        with patch.object(provider, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("API Error")
            
            with pytest.raises(Exception, match="In-house single embedding API error: API Error"):
                await provider.get_single_embedding("test text")
    
    @pytest.mark.asyncio
    async def test_get_embeddings_single_text(self, provider):
        """Test batch processing with single text."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "embedding": [0.1, 0.2, 0.3]
        }
        
        with patch.object(provider, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await provider.get_embeddings(["test text"])
            
            assert len(result) == 1
            assert result[0] == [0.1, 0.2, 0.3]
    
    @pytest.mark.asyncio
    async def test_get_embeddings_multiple_texts(self, provider):
        """Test batch processing with multiple texts."""
        # Mock responses for each text
        responses = [
            {"embedding": [0.1, 0.2, 0.3]},
            {"embedding": [0.4, 0.5, 0.6]},
            {"embedding": [0.7, 0.8, 0.9]}
        ]
        
        mock_responses = [MagicMock() for _ in responses]
        for mock_resp, resp_data in zip(mock_responses, responses):
            mock_resp.json.return_value = resp_data
        
        with patch.object(provider, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = mock_responses
            
            result = await provider.get_embeddings(["text1", "text2", "text3"])
            
            assert len(result) == 3
            assert result[0] == [0.1, 0.2, 0.3]
            assert result[1] == [0.4, 0.5, 0.6]
            assert result[2] == [0.7, 0.8, 0.9]
    
    @pytest.mark.asyncio
    async def test_get_embeddings_with_failures(self, provider):
        """Test batch processing with some failures."""
        # Mock responses: success, failure, success
        mock_response1 = MagicMock()
        mock_response1.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
        
        mock_response3 = MagicMock()
        mock_response3.json.return_value = {"embedding": [0.7, 0.8, 0.9]}
        
        with patch.object(provider, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = [
                mock_response1,  # Success
                Exception("API Error"),  # Failure
                mock_response3   # Success
            ]
            
            result = await provider.get_embeddings(["text1", "text2", "text3"])
            
            assert len(result) == 3
            assert result[0] == [0.1, 0.2, 0.3]  # Success
            assert result[1] == []  # Failure - empty embedding
            assert result[2] == [0.7, 0.8, 0.9]  # Success
    
    @pytest.mark.asyncio
    async def test_concurrency_control(self, provider):
        """Test that concurrency is properly controlled."""
        # Create a provider with low concurrency for testing
        config = {
            "api_url": "https://test-embeddings.com/api/v1/embed",
            "api_key": "test-api-key",
            "max_concurrent_requests": 2,
            "request_delay": 0.01  # Small delay for testing
        }
        test_provider = InhouseEmbeddingProvider(config)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
        
        request_times = []
        
        async def mock_request_with_timing(*args, **kwargs):
            request_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.1)  # Simulate API delay
            return mock_response
        
        with patch.object(test_provider, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = mock_request_with_timing
            
            # Process 4 texts with max_concurrent_requests=2
            start_time = asyncio.get_event_loop().time()
            result = await test_provider.get_embeddings(["text1", "text2", "text3", "text4"])
            end_time = asyncio.get_event_loop().time()
            
            # Should have 4 successful requests
            assert len(result) == 4
            assert all(len(emb) > 0 for emb in result)
            
            # Should have some concurrency (not all requests at the same time)
            # With max_concurrent_requests=2, we expect some overlap but not all 4 at once
            assert len(request_times) == 4
    
    def test_get_model_info(self, provider):
        """Test model info includes enhanced configuration."""
        model_info = provider.get_model_info()
        
        assert model_info["provider"] == "inhouse"
        assert model_info["model"] == provider.model
        assert model_info["api_url"] == provider.api_url
        assert model_info["vector_size"] == 768
        assert model_info["processing_mode"] == "single_text"
        assert model_info["max_concurrent_requests"] == 3
        assert model_info["request_delay"] == 0.1
    
    @pytest.mark.asyncio
    async def test_empty_texts_list(self, provider):
        """Test handling of empty texts list."""
        result = await provider.get_embeddings([])
        assert result == []
    
    @pytest.mark.asyncio
    async def test_single_empty_text(self, provider):
        """Test handling of single empty text."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
        
        with patch.object(provider, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await provider.get_single_embedding("")
            assert result == [0.1, 0.2, 0.3]  # API should handle empty text
    
    @pytest.mark.asyncio
    async def test_form_data_request_format(self, provider):
        """Test that requests are sent as form data instead of JSON."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3]}
        
        with patch.object(provider, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            await provider.get_single_embedding("test text")
            
            # Verify request was made with form data
            call_args = mock_request.call_args
            assert call_args[0][0] == "POST"  # method
            assert call_args[0][1] == provider.api_url  # url
            
            # Verify headers contain form data content type
            headers = call_args[0][2]  # headers
            assert headers["Content-Type"] == "application/x-www-form-urlencoded"
            
            # Verify data parameter is used instead of json_data
            assert 'data' in call_args[1]
            assert 'json_data' not in call_args[1]
            
            # Verify payload structure
            payload = call_args[1]['data']
            assert payload["text"] == "test text"
            assert payload["embeddings_model"] == provider.model
            assert payload["format"] == "vector"


if __name__ == "__main__":
    pytest.main([__file__]) 