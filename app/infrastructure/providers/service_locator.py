"""
Service locator for managing external service providers.
Provides dependency injection and singleton management for providers.
"""

from typing import Dict, Any, Optional
from app.domain.interfaces.providers import EmbeddingProvider, VectorStoreProvider, LLMProvider
from .factory import ProviderFactory
from app.core.config import Config


class ServiceLocator:
    """Service locator for managing external service providers."""
    
    def __init__(self):
        """Initialize the service locator."""
        self._providers: Dict[str, Any] = {}
        self._initialized = False
    
    def initialize_providers(self):
        """Initialize all providers using configuration."""
        if self._initialized:
            return
        
        # Get configurations
        embedding_config = Config.get_embedding_provider_config()
        llm_config = Config.get_llm_provider_config()
        vector_store_config = Config.get_vector_store_provider_config()
        
        # Create providers
        embedding_provider = ProviderFactory.create_embedding_provider(embedding_config)
        llm_provider = ProviderFactory.create_llm_provider(llm_config)
        vector_store_provider = ProviderFactory.create_vector_store_provider(vector_store_config)
        
        # Store providers
        self._providers["embedding"] = embedding_provider
        self._providers["llm"] = llm_provider
        self._providers["vector_store"] = vector_store_provider
        
        self._initialized = True
    
    def get_embedding_provider(self) -> EmbeddingProvider:
        """
        Get the embedding provider.
        
        Returns:
            EmbeddingProvider instance
            
        Raises:
            RuntimeError: If providers are not initialized
        """
        if not self._initialized:
            self.initialize_providers()
        return self._providers["embedding"]
    
    def get_llm_provider(self) -> LLMProvider:
        """
        Get the LLM provider.
        
        Returns:
            LLMProvider instance
            
        Raises:
            RuntimeError: If providers are not initialized
        """
        if not self._initialized:
            self.initialize_providers()
        return self._providers["llm"]
    
    def get_vector_store_provider(self) -> VectorStoreProvider:
        """
        Get the vector store provider.
        
        Returns:
            VectorStoreProvider instance
            
        Raises:
            RuntimeError: If providers are not initialized
        """
        if not self._initialized:
            self.initialize_providers()
        return self._providers["vector_store"]
    
    def register_provider(self, provider_type: str, provider: Any):
        """
        Register a custom provider instance.
        
        Args:
            provider_type: Type of provider ("embedding", "llm", "vector_store")
            provider: Provider instance
        """
        self._providers[provider_type] = provider
        self._initialized = True
    
    def reset(self):
        """Reset the service locator (useful for testing)."""
        self._providers.clear()
        self._initialized = False


# Global service locator instance
service_locator = ServiceLocator()


def get_embedding_provider() -> EmbeddingProvider:
    """Get the embedding provider from the global service locator."""
    return service_locator.get_embedding_provider()


def get_llm_provider() -> LLMProvider:
    """Get the LLM provider from the global service locator."""
    return service_locator.get_llm_provider()


def get_vector_store_provider() -> VectorStoreProvider:
    """Get the vector store provider from the global service locator."""
    return service_locator.get_vector_store_provider() 