"""
Integration tests for the plugin architecture.
These tests demonstrate that the plugin architecture works end-to-end.
"""

import pytest
from unittest.mock import patch, AsyncMock, Mock
from tests.utils.provider_test_helpers import MockProviderHelper, patch_providers_for_test
from app.domain.services.rag_service import RAGService
from app.infrastructure.vector_store.vector_store import VectorStore
from app.infrastructure.providers import ProviderFactory, ServiceLocator
from app.core.config import Config


@pytest.mark.integration
class TestPluginArchitectureIntegration:
    """Integration tests for plugin architecture."""

    @pytest.mark.asyncio
    async def test_rag_service_with_mock_providers(self):
        """Test RAG service with mock providers."""
        # Create mock providers
        embedding_provider = MockProviderHelper.create_mock_embedding_provider()
        llm_provider = MockProviderHelper.create_mock_llm_provider()
        vector_store_provider = MockProviderHelper.create_mock_vector_store_provider()
        
        # Mock the service locator calls to return our mock providers
        with patch('app.domain.services.rag_service.get_embedding_provider', return_value=embedding_provider), \
             patch('app.domain.services.rag_service.get_llm_provider', return_value=llm_provider), \
             patch('app.domain.services.rag_service.get_vector_store_provider', return_value=vector_store_provider), \
             patch('app.infrastructure.vector_store.vector_store.get_embedding_provider', return_value=embedding_provider), \
             patch('app.infrastructure.vector_store.vector_store.get_vector_store_provider', return_value=vector_store_provider):
            
            # Create RAG service with injected providers
            rag_service = RAGService(
                embedding_provider=embedding_provider,
                llm_provider=llm_provider,
                vector_store_provider=vector_store_provider
            )
            
            # Test that providers are correctly injected
            assert rag_service.embedding_provider == embedding_provider
            assert rag_service.llm_provider == llm_provider
            assert rag_service.vector_store_provider == vector_store_provider
            
            # Test that vector store uses the injected providers
            assert rag_service.vector_store.embedding_provider == embedding_provider
            assert rag_service.vector_store.vector_store_provider == vector_store_provider

    @pytest.mark.asyncio
    async def test_vector_store_with_mock_providers(self):
        """Test VectorStore with mock providers."""
        # Create mock providers
        embedding_provider = MockProviderHelper.create_mock_embedding_provider()
        vector_store_provider = MockProviderHelper.create_mock_vector_store_provider()
        
        # Create VectorStore with injected providers
        vector_store = VectorStore(
            embedding_provider=embedding_provider,
            vector_store_provider=vector_store_provider
        )
        
        # Test that providers are correctly injected
        assert vector_store.embedding_provider == embedding_provider
        assert vector_store.vector_store_provider == vector_store_provider

    def test_provider_factory_creates_correct_providers(self):
        """Test that ProviderFactory creates the correct provider types."""
        # Test OpenAI providers
        embedding_config = {
            "type": "openai",
            "api_url": "https://api.openai.com/v1/embeddings",
            "api_key": "test_key",
            "model": "text-embedding-ada-002"
        }
        
        llm_config = {
            "type": "openai",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_key": "test_key",
            "default_model": "gpt-3.5-turbo"
        }
        
        vector_store_config = {
            "type": "qdrant",
            "base_url": "https://test.qdrant.com",
            "api_key": "test_key"
        }
        
        # Create providers
        embedding_provider = ProviderFactory.create_embedding_provider(embedding_config)
        llm_provider = ProviderFactory.create_llm_provider(llm_config)
        vector_store_provider = ProviderFactory.create_vector_store_provider(vector_store_config)
        
        # Test that correct types are created
        from app.infrastructure.providers.openai_provider import OpenAIEmbeddingProvider, OpenAILLMProvider
        from app.infrastructure.providers.qdrant_provider import QdrantVectorStoreProvider
        
        assert isinstance(embedding_provider, OpenAIEmbeddingProvider)
        assert isinstance(llm_provider, OpenAILLMProvider)
        assert isinstance(vector_store_provider, QdrantVectorStoreProvider)

    def test_service_locator_manages_providers(self):
        """Test that ServiceLocator correctly manages providers."""
        service_locator = ServiceLocator()
        
        # Should not be initialized initially
        assert not service_locator._initialized
        
        # Initialize providers
        service_locator.initialize_providers()
        
        # Should be initialized now
        assert service_locator._initialized
        
        # Should have all provider types
        assert "embedding" in service_locator._providers
        assert "llm" in service_locator._providers
        assert "vector_store" in service_locator._providers
        
        # Should return providers
        embedding_provider = service_locator.get_embedding_provider()
        llm_provider = service_locator.get_llm_provider()
        vector_store_provider = service_locator.get_vector_store_provider()
        
        assert embedding_provider is not None
        assert llm_provider is not None
        assert vector_store_provider is not None

    @pytest.mark.asyncio
    async def test_end_to_end_workflow_with_mock_providers(self):
        """Test end-to-end workflow with mock providers."""
        # Create mock providers with specific responses
        embedding_provider = MockProviderHelper.create_mock_embedding_provider()
        llm_provider = MockProviderHelper.create_mock_llm_provider()
        vector_store_provider = MockProviderHelper.create_mock_vector_store_provider()
        
        # Configure mock responses
        embedding_provider.get_embeddings.return_value = [[0.1, 0.2, 0.3] * 512]
        llm_provider.call_llm.return_value = "This is a test response from the LLM."
        vector_store_provider.search_vectors.return_value = [
            {
                "payload": {
                    "content": "Test document content",
                    "metadata": {"source": "test.txt"}
                },
                "score": 0.95
            }
        ]
        
        # Mock the service locator calls to return our mock providers
        with patch('app.domain.services.rag_service.get_embedding_provider', return_value=embedding_provider), \
             patch('app.domain.services.rag_service.get_llm_provider', return_value=llm_provider), \
             patch('app.domain.services.rag_service.get_vector_store_provider', return_value=vector_store_provider), \
             patch('app.infrastructure.vector_store.vector_store.get_embedding_provider', return_value=embedding_provider), \
             patch('app.infrastructure.vector_store.vector_store.get_vector_store_provider', return_value=vector_store_provider):
            
            # Create RAG service
            rag_service = RAGService(
                embedding_provider=embedding_provider,
                llm_provider=llm_provider,
                vector_store_provider=vector_store_provider
            )
            
            # Test question asking
            result = await rag_service.ask_question("What is this test about?")
            
            # Verify the result
            assert result["success"] == True
            assert "test response" in result["answer"].lower()
            assert len(result["sources"]) == 1
            assert result["sources"][0]["score"] == 0.95
            
            # Verify that providers were called
            embedding_provider.get_embeddings.assert_called()
            vector_store_provider.search_vectors.assert_called()
            llm_provider.call_llm.assert_called()

    def test_configuration_integration(self):
        """Test that configuration works with the plugin architecture."""
        # Test that configuration methods return the expected structure
        embedding_config = Config.get_embedding_provider_config()
        llm_config = Config.get_llm_provider_config()
        vector_store_config = Config.get_vector_store_provider_config()
        
        # Verify configuration structure
        assert "type" in embedding_config
        assert "type" in llm_config
        assert "type" in vector_store_config
        
        # Verify provider types
        assert embedding_config["type"] in ["openai", "inhouse"]
        assert llm_config["type"] in ["openai", "inhouse"]
        assert vector_store_config["type"] in ["qdrant", "inhouse"]
        
        # Test that providers can be created from config
        embedding_provider = ProviderFactory.create_embedding_provider(embedding_config)
        llm_provider = ProviderFactory.create_llm_provider(llm_config)
        vector_store_provider = ProviderFactory.create_vector_store_provider(vector_store_config)
        
        assert embedding_provider is not None
        assert llm_provider is not None
        assert vector_store_provider is not None

    @pytest.mark.asyncio
    async def test_provider_switching_simulation(self):
        """Test that providers can be switched by changing configuration."""
        # Test with OpenAI providers
        openai_embedding_config = {
            "type": "openai",
            "api_url": "https://api.openai.com/v1/embeddings",
            "api_key": "test_key",
            "model": "text-embedding-ada-002"
        }
        
        openai_llm_config = {
            "type": "openai",
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_key": "test_key",
            "default_model": "gpt-3.5-turbo"
        }
        
        # Test with in-house providers
        inhouse_embedding_config = {
            "type": "inhouse",
            "api_url": "https://inhouse-api.com/embeddings",
            "api_key": "test_key",
            "model": "inhouse-model"
        }
        
        inhouse_llm_config = {
            "type": "inhouse",
            "api_url": "https://inhouse-api.com/llm",
            "api_key": "test_key",
            "default_model": "inhouse-model"
        }
        
        # Create providers with different configurations
        openai_embedding = ProviderFactory.create_embedding_provider(openai_embedding_config)
        openai_llm = ProviderFactory.create_llm_provider(openai_llm_config)
        
        inhouse_embedding = ProviderFactory.create_embedding_provider(inhouse_embedding_config)
        inhouse_llm = ProviderFactory.create_llm_provider(inhouse_llm_config)
        
        # Verify different provider types
        from app.infrastructure.providers.openai_provider import OpenAIEmbeddingProvider, OpenAILLMProvider
        from app.infrastructure.providers.inhouse_provider import InhouseEmbeddingProvider, InhouseLLMProvider
        
        assert isinstance(openai_embedding, OpenAIEmbeddingProvider)
        assert isinstance(openai_llm, OpenAILLMProvider)
        assert isinstance(inhouse_embedding, InhouseEmbeddingProvider)
        assert isinstance(inhouse_llm, InhouseLLMProvider)
        
        # Test that they have different configurations
        assert openai_embedding.api_url != inhouse_embedding.api_url
        assert openai_llm.api_url != inhouse_llm.api_url 