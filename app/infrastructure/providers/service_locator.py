"""
Service locator for managing external service providers with enhanced logging.
Provides dependency injection and singleton management for providers.
"""

from typing import Dict, Any, Optional
from app.domain.interfaces.providers import EmbeddingProvider, VectorStoreProvider, LLMProvider
from .factory import ProviderFactory
from app.core.config import Config
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class ServiceLocator:
    """Service locator for managing external service providers with enhanced logging."""
    
    def __init__(self):
        """Initialize the service locator."""
        self._providers: Dict[str, Any] = {}
        self._initialized = False
        
        logger.debug("Service locator initialized", extra={
            'extra_fields': {
                'event_type': 'service_locator_initialized',
                'providers_count': 0,
                'initialized': False
            }
        })
    
    def initialize_providers(self):
        """Initialize all providers using configuration with enhanced logging."""
        if self._initialized:
            logger.debug("Service locator already initialized, skipping", extra={
                'extra_fields': {
                    'event_type': 'service_locator_already_initialized',
                    'providers_count': len(self._providers)
                }
            })
            return
        
        logger.info("Initializing all providers", extra={
            'extra_fields': {
                'event_type': 'service_locator_initialize_start',
                'providers_count': 0
            }
        })
        
        try:
            # Get configurations
            embedding_config = Config.get_embedding_provider_config()
            llm_config = Config.get_llm_provider_config()
            vector_store_config = Config.get_vector_store_provider_config()
            
            logger.debug("Retrieved provider configurations", extra={
                'extra_fields': {
                    'event_type': 'service_locator_config_retrieved',
                    'embedding_type': embedding_config.get('type', 'not_specified'),
                    'llm_type': llm_config.get('type', 'not_specified'),
                    'vector_store_type': vector_store_config.get('type', 'not_specified')
                }
            })
            
            # Create providers
            embedding_provider = ProviderFactory.create_embedding_provider(embedding_config)
            llm_provider = ProviderFactory.create_llm_provider(llm_config)
            vector_store_provider = ProviderFactory.create_vector_store_provider(vector_store_config)
            
            # Store providers
            self._providers["embedding"] = embedding_provider
            self._providers["llm"] = llm_provider
            self._providers["vector_store"] = vector_store_provider
            
            self._initialized = True
            
            logger.info("Successfully initialized all providers", extra={
                'extra_fields': {
                    'event_type': 'service_locator_initialize_success',
                    'providers_count': len(self._providers),
                    'embedding_type': embedding_config.get('type', 'not_specified'),
                    'llm_type': llm_config.get('type', 'not_specified'),
                    'vector_store_type': vector_store_config.get('type', 'not_specified')
                }
            })
            
        except Exception as e:
            logger.error("Failed to initialize providers", extra={
                'extra_fields': {
                    'event_type': 'service_locator_initialize_failure',
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            })
            raise
    
    def get_embedding_provider(self) -> EmbeddingProvider:
        """
        Get the embedding provider with enhanced logging.
        
        Returns:
            EmbeddingProvider instance
            
        Raises:
            RuntimeError: If providers are not initialized
        """
        if not self._initialized:
            logger.debug("Providers not initialized, initializing now", extra={
                'extra_fields': {
                    'event_type': 'service_locator_provider_retrieval_auto_init',
                    'provider_type': 'embedding'
                }
            })
            self.initialize_providers()
        
        provider = self._providers["embedding"]
        logger.debug("Retrieved embedding provider", extra={
            'extra_fields': {
                'event_type': 'service_locator_provider_retrieved',
                'provider_type': 'embedding',
                'provider_class': type(provider).__name__
            }
        })
        return provider
    
    def get_llm_provider(self) -> LLMProvider:
        """
        Get the LLM provider with enhanced logging.
        
        Returns:
            LLMProvider instance
            
        Raises:
            RuntimeError: If providers are not initialized
        """
        if not self._initialized:
            logger.debug("Providers not initialized, initializing now", extra={
                'extra_fields': {
                    'event_type': 'service_locator_provider_retrieval_auto_init',
                    'provider_type': 'llm'
                }
            })
            self.initialize_providers()
        
        provider = self._providers["llm"]
        logger.debug("Retrieved LLM provider", extra={
            'extra_fields': {
                'event_type': 'service_locator_provider_retrieved',
                'provider_type': 'llm',
                'provider_class': type(provider).__name__
            }
        })
        return provider
    
    def get_vector_store_provider(self) -> VectorStoreProvider:
        """
        Get the vector store provider with enhanced logging.
        
        Returns:
            VectorStoreProvider instance
            
        Raises:
            RuntimeError: If providers are not initialized
        """
        if not self._initialized:
            logger.debug("Providers not initialized, initializing now", extra={
                'extra_fields': {
                    'event_type': 'service_locator_provider_retrieval_auto_init',
                    'provider_type': 'vector_store'
                }
            })
            self.initialize_providers()
        
        provider = self._providers["vector_store"]
        logger.debug("Retrieved vector store provider", extra={
            'extra_fields': {
                'event_type': 'service_locator_provider_retrieved',
                'provider_type': 'vector_store',
                'provider_class': type(provider).__name__
            }
        })
        return provider
    
    def register_provider(self, provider_type: str, provider: Any):
        """
        Register a custom provider instance with enhanced logging.
        
        Args:
            provider_type: Type of provider ("embedding", "llm", "vector_store")
            provider: Provider instance
        """
        logger.info("Registering custom provider", extra={
            'extra_fields': {
                'event_type': 'service_locator_provider_registered',
                'provider_type': provider_type,
                'provider_class': type(provider).__name__,
                'previous_provider_class': type(self._providers.get(provider_type)).__name__ if provider_type in self._providers else 'none'
            }
        })
        
        self._providers[provider_type] = provider
        self._initialized = True
    
    def reset(self):
        """Reset the service locator (useful for testing) with enhanced logging."""
        logger.info("Resetting service locator", extra={
            'extra_fields': {
                'event_type': 'service_locator_reset',
                'providers_count': len(self._providers),
                'was_initialized': self._initialized
            }
        })
        
        self._providers.clear()
        self._initialized = False
        
        logger.debug("Service locator reset completed", extra={
            'extra_fields': {
                'event_type': 'service_locator_reset_complete',
                'providers_count': 0,
                'initialized': False
            }
        })


# Global service locator instance
_service_locator = ServiceLocator()

def get_embedding_provider() -> EmbeddingProvider:
    """
    Get the global embedding provider instance with enhanced logging.
    
    Returns:
        EmbeddingProvider instance
    """
    logger.debug("Getting global embedding provider", extra={
        'extra_fields': {
            'event_type': 'global_provider_retrieval',
            'provider_type': 'embedding'
        }
    })
    return _service_locator.get_embedding_provider()

def get_llm_provider() -> LLMProvider:
    """
    Get the global LLM provider instance with enhanced logging.
    
    Returns:
        LLMProvider instance
    """
    logger.debug("Getting global LLM provider", extra={
        'extra_fields': {
            'event_type': 'global_provider_retrieval',
            'provider_type': 'llm'
        }
    })
    return _service_locator.get_llm_provider()

def get_vector_store_provider() -> VectorStoreProvider:
    """
    Get the global vector store provider instance with enhanced logging.
    
    Returns:
        VectorStoreProvider instance
    """
    logger.debug("Getting global vector store provider", extra={
        'extra_fields': {
            'event_type': 'global_provider_retrieval',
            'provider_type': 'vector_store'
        }
    })
    return _service_locator.get_vector_store_provider() 