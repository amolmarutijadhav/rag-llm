import pytest
from unittest.mock import patch, AsyncMock, Mock
from app.infrastructure.providers import ProviderFactory, ServiceLocator
from app.infrastructure.providers.openai_provider import OpenAIEmbeddingProvider, OpenAILLMProvider
from app.infrastructure.providers.qdrant_provider import QdrantVectorStoreProvider
from app.infrastructure.providers.inhouse_provider import InhouseEmbeddingProvider, InhouseLLMProvider, InhouseVectorStoreProvider
from app.core.config import Config


@pytest.mark.unit
class TestProviderFactory:
    """Test suite for ProviderFactory"""

    def test_create_embedding_provider_openai(self):
        """Test creating OpenAI embedding provider"""
        config = {
            "type": "openai",
            "api_url": "https://api.openai.com/v1/embeddings",
            "api_key": "test_key",
            "model": "text-embedding-ada-002"
        }
        
        provider = ProviderFactory.create_embedding_provider(config)
        
        assert isinstance(provider, OpenAIEmbeddingProvider)
        assert provider.api_url == "https://api.openai.com/v1/embeddings"
        assert provider.api_key == "test_key"
        assert provider.model == "text-embedding-ada-002"

    def test_create_embedding_provider_inhouse(self):
        """Test creating in-house embedding provider"""
        config = {
            "type": "inhouse",
            "api_url": "https://inhouse-api.com/embeddings",
            "api_key": "test_key",
            "model": "inhouse-model"
        }
        
        provider = ProviderFactory.create_embedding_provider(config)
        
        assert isinstance(provider, InhouseEmbeddingProvider)
        assert provider.api_url == "https://inhouse-api.com/embeddings"
        assert provider.api_key == "test_key"
        assert provider.model == "inhouse-model"

    def test_create_embedding_provider_unsupported(self):
        """Test creating unsupported embedding provider"""
        config = {"type": "unsupported"}
        
        with pytest.raises(ValueError, match="Unsupported embedding provider type"):
            ProviderFactory.create_embedding_provider(config)

    def test_create_llm_provider_openai(self):
        """Test creating OpenAI LLM provider"""
        config = {
            "type": "openai",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_key": "test_key",
            "default_model": "gpt-3.5-turbo"
        }
        
        provider = ProviderFactory.create_llm_provider(config)
        
        assert isinstance(provider, OpenAILLMProvider)
        assert provider.api_url == "https://api.openai.com/v1/chat/completions"
        assert provider.api_key == "test_key"
        assert provider.default_model == "gpt-3.5-turbo"

    def test_create_llm_provider_inhouse(self):
        """Test creating in-house LLM provider"""
        config = {
            "type": "inhouse",
            "api_url": "https://inhouse-api.com/llm",
            "api_key": "test_key",
            "default_model": "inhouse-model"
        }
        
        provider = ProviderFactory.create_llm_provider(config)
        
        assert isinstance(provider, InhouseLLMProvider)
        assert provider.api_url == "https://inhouse-api.com/llm"
        assert provider.api_key == "test_key"
        assert provider.default_model == "inhouse-model"

    def test_create_vector_store_provider_qdrant(self):
        """Test creating Qdrant vector store provider"""
        config = {
            "type": "qdrant",
            "base_url": "https://qdrant.example.com",
            "api_key": "test_key"
        }
        
        provider = ProviderFactory.create_vector_store_provider(config)
        
        assert isinstance(provider, QdrantVectorStoreProvider)
        assert provider.base_url == "https://qdrant.example.com"
        assert provider.api_key == "test_key"

    def test_create_vector_store_provider_inhouse(self):
        """Test creating in-house vector store provider"""
        config = {
            "type": "inhouse",
            "base_url": "https://inhouse-vector-store.com",
            "api_key": "test_key"
        }
        
        provider = ProviderFactory.create_vector_store_provider(config)
        
        assert isinstance(provider, InhouseVectorStoreProvider)
        assert provider.base_url == "https://inhouse-vector-store.com"
        assert provider.api_key == "test_key"

    def test_create_all_providers(self):
        """Test creating all providers at once"""
        embedding_config = {"type": "openai", "api_key": "test_key"}
        llm_config = {"type": "openai", "api_key": "test_key"}
        vector_store_config = {"type": "qdrant", "base_url": "https://test.qdrant.com", "api_key": "test_key"}
        
        embedding_provider, llm_provider, vector_store_provider = ProviderFactory.create_all_providers(
            embedding_config, llm_config, vector_store_config
        )
        
        assert isinstance(embedding_provider, OpenAIEmbeddingProvider)
        assert isinstance(llm_provider, OpenAILLMProvider)
        assert isinstance(vector_store_provider, QdrantVectorStoreProvider)


@pytest.mark.unit
class TestServiceLocator:
    """Test suite for ServiceLocator"""

    def test_initialize_providers(self):
        """Test provider initialization"""
        service_locator = ServiceLocator()
        
        # Should not be initialized initially
        assert not service_locator._initialized
        
        # Initialize providers
        service_locator.initialize_providers()
        
        # Should be initialized now
        assert service_locator._initialized
        assert "embedding" in service_locator._providers
        assert "llm" in service_locator._providers
        assert "vector_store" in service_locator._providers

    def test_get_embedding_provider(self):
        """Test getting embedding provider"""
        service_locator = ServiceLocator()
        
        # Should auto-initialize when getting provider
        provider = service_locator.get_embedding_provider()
        
        assert provider is not None
        assert service_locator._initialized

    def test_get_llm_provider(self):
        """Test getting LLM provider"""
        service_locator = ServiceLocator()
        
        provider = service_locator.get_llm_provider()
        
        assert provider is not None
        assert service_locator._initialized

    def test_get_vector_store_provider(self):
        """Test getting vector store provider"""
        service_locator = ServiceLocator()
        
        provider = service_locator.get_vector_store_provider()
        
        assert provider is not None
        assert service_locator._initialized

    def test_register_custom_provider(self):
        """Test registering custom provider"""
        service_locator = ServiceLocator()
        mock_provider = Mock()
        
        service_locator.register_provider("embedding", mock_provider)
        
        assert service_locator._initialized
        assert service_locator._providers["embedding"] == mock_provider

    def test_reset(self):
        """Test resetting service locator"""
        service_locator = ServiceLocator()
        service_locator.initialize_providers()
        
        assert service_locator._initialized
        assert len(service_locator._providers) > 0
        
        service_locator.reset()
        
        assert not service_locator._initialized
        assert len(service_locator._providers) == 0


@pytest.mark.unit
class TestOpenAIEmbeddingProvider:
    """Test suite for OpenAI embedding provider"""

    @pytest.fixture
    def provider(self):
        """Create OpenAI embedding provider"""
        config = {
            "api_url": "https://api.openai.com/v1/embeddings",
            "api_key": "test_key",
            "model": "text-embedding-ada-002"
        }
        return OpenAIEmbeddingProvider(config)

    def test_initialization(self, provider):
        """Test provider initialization"""
        assert provider.api_url == "https://api.openai.com/v1/embeddings"
        assert provider.api_key == "test_key"
        assert provider.model == "text-embedding-ada-002"

    def test_initialization_missing_api_key(self):
        """Test initialization with missing API key"""
        config = {
            "api_url": "https://api.openai.com/v1/embeddings",
            "model": "text-embedding-ada-002"
        }
        
        with pytest.raises(ValueError, match="OpenAI API key is required"):
            OpenAIEmbeddingProvider(config)

    @patch('app.infrastructure.providers.openai_provider.OpenAIEmbeddingProvider._make_request')
    @pytest.mark.asyncio
    async def test_get_embeddings(self, mock_request, provider):
        """Test getting embeddings"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3] * 512}
            ]
        }
        mock_request.return_value = mock_response
        
        texts = ["Hello world"]
        embeddings = await provider.get_embeddings(texts)
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 1536

    def test_get_model_info(self, provider):
        """Test getting model info"""
        info = provider.get_model_info()
        
        assert info["provider"] == "openai"
        assert info["model"] == "text-embedding-ada-002"
        assert info["vector_size"] == 1536


@pytest.mark.unit
class TestOpenAILLMProvider:
    """Test suite for OpenAI LLM provider"""

    @pytest.fixture
    def provider(self):
        """Create OpenAI LLM provider"""
        config = {
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_key": "test_key",
            "default_model": "gpt-3.5-turbo"
        }
        return OpenAILLMProvider(config)

    def test_initialization(self, provider):
        """Test provider initialization"""
        assert provider.api_url == "https://api.openai.com/v1/chat/completions"
        assert provider.api_key == "test_key"
        assert provider.default_model == "gpt-3.5-turbo"

    @patch('app.infrastructure.providers.openai_provider.OpenAILLMProvider._make_request')
    @pytest.mark.asyncio
    async def test_call_llm(self, mock_request, provider):
        """Test calling LLM"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is a test response"
                    }
                }
            ]
        }
        mock_request.return_value = mock_response
        
        messages = [{"role": "user", "content": "Hello"}]
        response = await provider.call_llm(messages)
        
        assert response == "This is a test response"

    @patch('app.infrastructure.providers.openai_provider.OpenAILLMProvider._make_request')
    @pytest.mark.asyncio
    async def test_call_llm_api_full_response(self, mock_request, provider):
        """Test calling LLM API with full response"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is a test response"
                    }
                }
            ],
            "usage": {"total_tokens": 10}
        }
        mock_request.return_value = mock_response
        
        request = {"messages": [{"role": "user", "content": "Hello"}]}
        response = await provider.call_llm_api(request, return_full_response=True)
        
        assert "choices" in response
        assert "usage" in response

    def test_get_model_info(self, provider):
        """Test getting model info"""
        info = provider.get_model_info()
        
        assert info["provider"] == "openai"
        assert info["default_model"] == "gpt-3.5-turbo"


@pytest.mark.unit
class TestQdrantVectorStoreProvider:
    """Test suite for Qdrant vector store provider"""

    @pytest.fixture
    def provider(self):
        """Create Qdrant vector store provider"""
        config = {
            "base_url": "https://qdrant.example.com",
            "api_key": "test_key"
        }
        return QdrantVectorStoreProvider(config)

    def test_initialization(self, provider):
        """Test provider initialization"""
        assert provider.base_url == "https://qdrant.example.com"
        assert provider.api_key == "test_key"

    def test_url_generation(self, provider):
        """Test URL generation methods"""
        collection_name = "test_collection"
        
        assert provider._get_collection_url(collection_name) == "https://qdrant.example.com/collections/test_collection"
        assert provider._get_points_url(collection_name) == "https://qdrant.example.com/collections/test_collection/points"
        assert provider._get_search_url(collection_name) == "https://qdrant.example.com/collections/test_collection/points/search"

    @patch('app.infrastructure.providers.qdrant_provider.QdrantVectorStoreProvider._make_request')
    @pytest.mark.asyncio
    async def test_create_collection_if_not_exists(self, mock_request, provider):
        """Test creating collection if it doesn't exist"""
        # Mock collection doesn't exist (404)
        mock_request.side_effect = [Exception("Not found"), Mock()]
        
        result = await provider.create_collection_if_not_exists("test_collection", 1536, "Cosine")
        
        assert result is True
        assert mock_request.call_count == 2

    @patch('app.infrastructure.providers.qdrant_provider.QdrantVectorStoreProvider._make_request')
    @pytest.mark.asyncio
    async def test_insert_vectors(self, mock_request, provider):
        """Test inserting vectors"""
        mock_request.return_value = Mock()
        
        points = [
            {
                "id": "test-id",
                "vector": [0.1, 0.2, 0.3] * 512,
                "payload": {"content": "test content"}
            }
        ]
        
        result = await provider.insert_vectors(points, "test_collection")
        
        assert result is True

    @patch('app.infrastructure.providers.qdrant_provider.QdrantVectorStoreProvider._make_request')
    @pytest.mark.asyncio
    async def test_search_vectors(self, mock_request, provider):
        """Test searching vectors"""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "result": [
                {
                    "id": "test-id",
                    "score": 0.95,
                    "payload": {"content": "test content"}
                }
            ]
        }
        mock_request.return_value = mock_response
        
        query_vector = [0.1, 0.2, 0.3] * 512
        results = await provider.search_vectors(query_vector, 3, "test_collection")
        
        assert len(results) == 1
        assert results[0]["score"] == 0.95

    def test_get_collection_stats_fallback(self, provider):
        """Test getting collection stats with fallback behavior"""
        # Test fallback behavior when collection doesn't exist
        stats = provider.get_collection_stats("nonexistent_collection")
        
        assert stats["total_documents"] == 0
        assert stats["collection_name"] == "nonexistent_collection"
        assert stats["vector_size"] == 1536 