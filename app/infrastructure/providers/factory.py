"""
Factory for creating external service providers based on configuration with enhanced logging.
"""

from typing import Dict, Any
from app.domain.interfaces.providers import EmbeddingProvider, VectorStoreProvider, LLMProvider
from .openai_provider import OpenAIEmbeddingProvider, OpenAILLMProvider
from .qdrant_provider import QdrantVectorStoreProvider
from .inhouse_provider import InhouseEmbeddingProvider, InhouseLLMProvider, InhouseVectorStoreProvider
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class ProviderFactory:
    """Factory for creating external service providers with enhanced logging."""
    
    @staticmethod
    def create_embedding_provider(config: Dict[str, Any]) -> EmbeddingProvider:
        """
        Create an embedding provider based on configuration with enhanced logging.
        
        Args:
            config: Configuration dictionary containing provider type and settings
            
        Returns:
            EmbeddingProvider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        provider_type = config.get("type", "openai").lower()
        
        logger.info(f"Creating embedding provider", extra={
            'extra_fields': {
                'event_type': 'provider_factory_embedding_create_start',
                'provider_type': provider_type,
                'api_url': config.get('api_url', 'not_specified'),
                'model': config.get('model', 'not_specified')
            }
        })
        
        try:
            if provider_type == "openai":
                provider = OpenAIEmbeddingProvider(config)
                logger.info(f"Successfully created OpenAI embedding provider", extra={
                    'extra_fields': {
                        'event_type': 'provider_factory_embedding_create_success',
                        'provider_type': provider_type,
                        'provider_class': 'OpenAIEmbeddingProvider'
                    }
                })
                return provider
            elif provider_type == "inhouse":
                provider = InhouseEmbeddingProvider(config)
                logger.info(f"Successfully created Inhouse embedding provider", extra={
                    'extra_fields': {
                        'event_type': 'provider_factory_embedding_create_success',
                        'provider_type': provider_type,
                        'provider_class': 'InhouseEmbeddingProvider'
                    }
                })
                return provider
            elif provider_type == "cohere":
                # TODO: Implement Cohere embedding provider
                logger.error(f"Cohere embedding provider not yet implemented", extra={
                    'extra_fields': {
                        'event_type': 'provider_factory_embedding_create_failure',
                        'provider_type': provider_type,
                        'error': 'NotImplementedError'
                    }
                })
                raise NotImplementedError("Cohere embedding provider not yet implemented")
            else:
                logger.error(f"Unsupported embedding provider type", extra={
                    'extra_fields': {
                        'event_type': 'provider_factory_embedding_create_failure',
                        'provider_type': provider_type,
                        'error': 'ValueError'
                    }
                })
                raise ValueError(f"Unsupported embedding provider type: {provider_type}")
                
        except Exception as e:
            logger.error(f"Failed to create embedding provider", extra={
                'extra_fields': {
                    'event_type': 'provider_factory_embedding_create_failure',
                    'provider_type': provider_type,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            })
            raise
    
    @staticmethod
    def create_llm_provider(config: Dict[str, Any]) -> LLMProvider:
        """
        Create an LLM provider based on configuration with enhanced logging.
        
        Args:
            config: Configuration dictionary containing provider type and settings
            
        Returns:
            LLMProvider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        provider_type = config.get("type", "openai").lower()
        
        logger.info(f"Creating LLM provider", extra={
            'extra_fields': {
                'event_type': 'provider_factory_llm_create_start',
                'provider_type': provider_type,
                'api_url': config.get('api_url', 'not_specified'),
                'default_model': config.get('default_model', 'not_specified')
            }
        })
        
        try:
            if provider_type == "openai":
                provider = OpenAILLMProvider(config)
                logger.info(f"Successfully created OpenAI LLM provider", extra={
                    'extra_fields': {
                        'event_type': 'provider_factory_llm_create_success',
                        'provider_type': provider_type,
                        'provider_class': 'OpenAILLMProvider'
                    }
                })
                return provider
            elif provider_type == "inhouse":
                provider = InhouseLLMProvider(config)
                logger.info(f"Successfully created Inhouse LLM provider", extra={
                    'extra_fields': {
                        'event_type': 'provider_factory_llm_create_success',
                        'provider_type': provider_type,
                        'provider_class': 'InhouseLLMProvider'
                    }
                })
                return provider
            elif provider_type == "anthropic":
                # TODO: Implement Anthropic LLM provider
                logger.error(f"Anthropic LLM provider not yet implemented", extra={
                    'extra_fields': {
                        'event_type': 'provider_factory_llm_create_failure',
                        'provider_type': provider_type,
                        'error': 'NotImplementedError'
                    }
                })
                raise NotImplementedError("Anthropic LLM provider not yet implemented")
            else:
                logger.error(f"Unsupported LLM provider type", extra={
                    'extra_fields': {
                        'event_type': 'provider_factory_llm_create_failure',
                        'provider_type': provider_type,
                        'error': 'ValueError'
                    }
                })
                raise ValueError(f"Unsupported LLM provider type: {provider_type}")
                
        except Exception as e:
            logger.error(f"Failed to create LLM provider", extra={
                'extra_fields': {
                    'event_type': 'provider_factory_llm_create_failure',
                    'provider_type': provider_type,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            })
            raise
    
    @staticmethod
    def create_vector_store_provider(config: Dict[str, Any]) -> VectorStoreProvider:
        """
        Create a vector store provider based on configuration with enhanced logging.
        
        Args:
            config: Configuration dictionary containing provider type and settings
            
        Returns:
            VectorStoreProvider instance
            
        Raises:
            ValueError: If provider type is not supported
        """
        provider_type = config.get("type", "qdrant").lower()
        
        logger.info(f"Creating vector store provider", extra={
            'extra_fields': {
                'event_type': 'provider_factory_vector_store_create_start',
                'provider_type': provider_type,
                'base_url': config.get('base_url', 'not_specified'),
                'collection_name': config.get('collection_name', 'not_specified')
            }
        })
        
        try:
            if provider_type == "qdrant":
                provider = QdrantVectorStoreProvider(config)
                logger.info(f"Successfully created Qdrant vector store provider", extra={
                    'extra_fields': {
                        'event_type': 'provider_factory_vector_store_create_success',
                        'provider_type': provider_type,
                        'provider_class': 'QdrantVectorStoreProvider'
                    }
                })
                return provider
            elif provider_type == "inhouse":
                provider = InhouseVectorStoreProvider(config)
                logger.info(f"Successfully created Inhouse vector store provider", extra={
                    'extra_fields': {
                        'event_type': 'provider_factory_vector_store_create_success',
                        'provider_type': provider_type,
                        'provider_class': 'InhouseVectorStoreProvider'
                    }
                })
                return provider
            elif provider_type == "pinecone":
                # TODO: Implement Pinecone vector store provider
                logger.error(f"Pinecone vector store provider not yet implemented", extra={
                    'extra_fields': {
                        'event_type': 'provider_factory_vector_store_create_failure',
                        'provider_type': provider_type,
                        'error': 'NotImplementedError'
                    }
                })
                raise NotImplementedError("Pinecone vector store provider not yet implemented")
            else:
                logger.error(f"Unsupported vector store provider type", extra={
                    'extra_fields': {
                        'event_type': 'provider_factory_vector_store_create_failure',
                        'provider_type': provider_type,
                        'error': 'ValueError'
                    }
                })
                raise ValueError(f"Unsupported vector store provider type: {provider_type}")
                
        except Exception as e:
            logger.error(f"Failed to create vector store provider", extra={
                'extra_fields': {
                    'event_type': 'provider_factory_vector_store_create_failure',
                    'provider_type': provider_type,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            })
            raise
    
    @staticmethod
    def create_all_providers(embedding_config: Dict[str, Any], 
                           llm_config: Dict[str, Any], 
                           vector_store_config: Dict[str, Any]) -> tuple[EmbeddingProvider, LLMProvider, VectorStoreProvider]:
        """
        Create all three providers at once with enhanced logging.
        
        Args:
            embedding_config: Configuration for embedding provider
            llm_config: Configuration for LLM provider
            vector_store_config: Configuration for vector store provider
            
        Returns:
            Tuple of (EmbeddingProvider, LLMProvider, VectorStoreProvider)
        """
        logger.info(f"Creating all providers", extra={
            'extra_fields': {
                'event_type': 'provider_factory_create_all_start',
                'embedding_type': embedding_config.get('type', 'not_specified'),
                'llm_type': llm_config.get('type', 'not_specified'),
                'vector_store_type': vector_store_config.get('type', 'not_specified')
            }
        })
        
        try:
            embedding_provider = ProviderFactory.create_embedding_provider(embedding_config)
            llm_provider = ProviderFactory.create_llm_provider(llm_config)
            vector_store_provider = ProviderFactory.create_vector_store_provider(vector_store_config)
            
            logger.info(f"Successfully created all providers", extra={
                'extra_fields': {
                    'event_type': 'provider_factory_create_all_success',
                    'embedding_type': embedding_config.get('type', 'not_specified'),
                    'llm_type': llm_config.get('type', 'not_specified'),
                    'vector_store_type': vector_store_config.get('type', 'not_specified')
                }
            })
            
            return embedding_provider, llm_provider, vector_store_provider
            
        except Exception as e:
            logger.error(f"Failed to create all providers", extra={
                'extra_fields': {
                    'event_type': 'provider_factory_create_all_failure',
                    'embedding_type': embedding_config.get('type', 'not_specified'),
                    'llm_type': llm_config.get('type', 'not_specified'),
                    'vector_store_type': vector_store_config.get('type', 'not_specified'),
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            })
            raise 