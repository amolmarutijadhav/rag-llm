"""
Service locator for managing external service providers with enhanced logging.
Provides dependency injection and singleton management for providers.
"""

import asyncio
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
    
    async def cleanup(self):
        """Cleanup all providers and close connection pools."""
        if not self._initialized:
            logger.debug("Service locator not initialized, skipping cleanup", extra={
                'extra_fields': {
                    'event_type': 'service_locator_cleanup_skipped',
                    'reason': 'not_initialized'
                }
            })
            return
        
        logger.info("Starting provider cleanup", extra={
            'extra_fields': {
                'event_type': 'service_locator_cleanup_start',
                'providers_count': len(self._providers)
            }
        })
        
        cleanup_tasks = []
        
        # Close all providers that support cleanup
        for provider_type, provider in self._providers.items():
            if hasattr(provider, 'close') and callable(getattr(provider, 'close')):
                try:
                    if asyncio.iscoroutinefunction(provider.close):
                        cleanup_tasks.append(provider.close())
                    else:
                        # For sync close methods, run in executor
                        loop = asyncio.get_event_loop()
                        cleanup_tasks.append(loop.run_in_executor(None, provider.close))
                    
                    logger.debug(f"Added {provider_type} provider to cleanup queue", extra={
                        'extra_fields': {
                            'event_type': 'provider_cleanup_queued',
                            'provider_type': provider_type
                        }
                    })
                except Exception as e:
                    logger.warning(f"Failed to queue cleanup for {provider_type} provider", extra={
                        'extra_fields': {
                            'event_type': 'provider_cleanup_queue_failed',
                            'provider_type': provider_type,
                            'error': str(e)
                        }
                    })
        
        # Wait for all cleanup tasks to complete
        if cleanup_tasks:
            try:
                await asyncio.gather(*cleanup_tasks, return_exceptions=True)
                logger.info("Provider cleanup completed", extra={
                    'extra_fields': {
                        'event_type': 'service_locator_cleanup_success',
                        'providers_cleaned': len(cleanup_tasks)
                    }
                })
            except Exception as e:
                logger.error("Provider cleanup failed", extra={
                    'extra_fields': {
                        'event_type': 'service_locator_cleanup_failure',
                        'error': str(e),
                        'providers_attempted': len(cleanup_tasks)
                    }
                })
        
        # Clear providers
        self._providers.clear()
        self._initialized = False
        
        logger.info("Service locator reset completed", extra={
            'extra_fields': {
                'event_type': 'service_locator_reset_complete',
                'providers_count': 0
            }
        })
    
    def get_embedding_provider(self) -> EmbeddingProvider:
        """
        Get the embedding provider with enhanced logging.
        
        Returns:
            EmbeddingProvider instance
            
        Raises:
            RuntimeError: If providers are not initialized
        """
        if not self._initialized:
            logger.debug("Providers not initialized, auto-initializing now", extra={
                'extra_fields': {
                    'event_type': 'service_locator_auto_init',
                    'provider_type': 'embedding'
                }
            })
            self.initialize_providers()
        
        provider = self._providers.get("embedding")
        if not provider:
            logger.error("Embedding provider not found", extra={
                'extra_fields': {
                    'event_type': 'service_locator_provider_not_found',
                    'provider_type': 'embedding'
                }
            })
            raise RuntimeError("Embedding provider not found")
        
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
            logger.debug("Providers not initialized, auto-initializing now", extra={
                'extra_fields': {
                    'event_type': 'service_locator_auto_init',
                    'provider_type': 'llm'
                }
            })
            self.initialize_providers()
        
        provider = self._providers.get("llm")
        if not provider:
            logger.error("LLM provider not found", extra={
                'extra_fields': {
                    'event_type': 'service_locator_provider_not_found',
                    'provider_type': 'llm'
                }
            })
            raise RuntimeError("LLM provider not found")
        
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
            logger.debug("Providers not initialized, auto-initializing now", extra={
                'extra_fields': {
                    'event_type': 'service_locator_auto_init',
                    'provider_type': 'vector_store'
                }
            })
            self.initialize_providers()
        
        provider = self._providers.get("vector_store")
        if not provider:
            logger.error("Vector store provider not found", extra={
                'extra_fields': {
                    'event_type': 'service_locator_provider_not_found',
                    'provider_type': 'vector_store'
                }
            })
            raise RuntimeError("Vector store provider not found")
        
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
        Register a custom provider with enhanced logging.
        
        Args:
            provider_type: Type of provider (embedding, llm, vector_store)
            provider: Provider instance
        """
        if provider_type in self._providers:
            logger.warning(f"Overwriting existing {provider_type} provider", extra={
                'extra_fields': {
                    'event_type': 'service_locator_provider_overwrite',
                    'provider_type': provider_type,
                    'old_provider_class': type(self._providers[provider_type]).__name__,
                    'new_provider_class': type(provider).__name__
                }
            })
        
        self._providers[provider_type] = provider
        self._initialized = True
        
        logger.info(f"Registered custom {provider_type} provider", extra={
            'extra_fields': {
                'event_type': 'service_locator_provider_registered',
                'provider_type': provider_type,
                'provider_class': type(provider).__name__
            }
        })
    
    async def reset(self):
        """
        Reset the service locator and cleanup all providers with enhanced logging.
        This will close all connection pools and cleanup resources.
        """
        logger.info("Resetting service locator", extra={
            'extra_fields': {
                'event_type': 'service_locator_reset_start',
                'providers_count': len(self._providers),
                'initialized': self._initialized
            }
        })
        
        await self.cleanup()

# Global service locator instance
_service_locator = ServiceLocator()

def get_service_locator() -> ServiceLocator:
    """Get the global service locator instance."""
    return _service_locator

def get_embedding_provider() -> EmbeddingProvider:
    """
    Get the global embedding provider instance.
    
    Returns:
        EmbeddingProvider instance
    """
    return _service_locator.get_embedding_provider()

def get_llm_provider() -> LLMProvider:
    """
    Get the global LLM provider instance.
    
    Returns:
        LLMProvider instance
    """
    return _service_locator.get_llm_provider()

def get_vector_store_provider() -> VectorStoreProvider:
    """
    Get the global vector store provider instance.
    
    Returns:
        VectorStoreProvider instance
    """
    return _service_locator.get_vector_store_provider()

async def cleanup_service_locator():
    """Cleanup the global service locator and all providers."""
    await _service_locator.cleanup() 