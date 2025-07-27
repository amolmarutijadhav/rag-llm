"""
Factory for creating external service providers based on configuration.
"""

from typing import Dict, Any
from app.domain.interfaces.providers import EmbeddingProvider, VectorStoreProvider, LLMProvider
from .openai_provider import OpenAIEmbeddingProvider, OpenAILLMProvider
from .qdrant_provider import QdrantVectorStoreProvider
from .inhouse_provider import InhouseEmbeddingProvider, InhouseLLMProvider, InhouseVectorStoreProvider


class ProviderFactory:
    """Factory for creating external service providers."""
    
    @staticmethod
    def create_embedding_provider(config: Dict[str, Any]) -> EmbeddingProvider:
        """
        Create an embedding provider based on configuration.
        
        Args:
            config: Configuration dictionary containing provider type and settings
            
        Returns:
            EmbeddingProvider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        provider_type = config.get("type", "openai").lower()
        
        if provider_type == "openai":
            return OpenAIEmbeddingProvider(config)
        elif provider_type == "inhouse":
            return InhouseEmbeddingProvider(config)
        elif provider_type == "cohere":
            # TODO: Implement Cohere embedding provider
            raise NotImplementedError("Cohere embedding provider not yet implemented")
        else:
            raise ValueError(f"Unsupported embedding provider type: {provider_type}")
    
    @staticmethod
    def create_llm_provider(config: Dict[str, Any]) -> LLMProvider:
        """
        Create an LLM provider based on configuration.
        
        Args:
            config: Configuration dictionary containing provider type and settings
            
        Returns:
            LLMProvider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        provider_type = config.get("type", "openai").lower()
        
        if provider_type == "openai":
            return OpenAILLMProvider(config)
        elif provider_type == "inhouse":
            return InhouseLLMProvider(config)
        elif provider_type == "anthropic":
            # TODO: Implement Anthropic LLM provider
            raise NotImplementedError("Anthropic LLM provider not yet implemented")
        else:
            raise ValueError(f"Unsupported LLM provider type: {provider_type}")
    
    @staticmethod
    def create_vector_store_provider(config: Dict[str, Any]) -> VectorStoreProvider:
        """
        Create a vector store provider based on configuration.
        
        Args:
            config: Configuration dictionary containing provider type and settings
            
        Returns:
            VectorStoreProvider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        provider_type = config.get("type", "qdrant").lower()
        
        if provider_type == "qdrant":
            return QdrantVectorStoreProvider(config)
        elif provider_type == "inhouse":
            return InhouseVectorStoreProvider(config)
        elif provider_type == "pinecone":
            # TODO: Implement Pinecone vector store provider
            raise NotImplementedError("Pinecone vector store provider not yet implemented")
        else:
            raise ValueError(f"Unsupported vector store provider type: {provider_type}")
    
    @staticmethod
    def create_all_providers(embedding_config: Dict[str, Any], 
                           llm_config: Dict[str, Any], 
                           vector_store_config: Dict[str, Any]) -> tuple[EmbeddingProvider, LLMProvider, VectorStoreProvider]:
        """
        Create all three providers at once.
        
        Args:
            embedding_config: Configuration for embedding provider
            llm_config: Configuration for LLM provider
            vector_store_config: Configuration for vector store provider
            
        Returns:
            Tuple of (EmbeddingProvider, LLMProvider, VectorStoreProvider)
        """
        embedding_provider = ProviderFactory.create_embedding_provider(embedding_config)
        llm_provider = ProviderFactory.create_llm_provider(llm_config)
        vector_store_provider = ProviderFactory.create_vector_store_provider(vector_store_config)
        
        return embedding_provider, llm_provider, vector_store_provider 