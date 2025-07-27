import uuid
import json
from typing import List, Dict, Any, Optional
from app.core.config import Config
from app.domain.interfaces.providers import EmbeddingProvider, VectorStoreProvider
from app.infrastructure.providers import get_embedding_provider, get_vector_store_provider
from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)

class VectorStore:
    """Handles vector storage and retrieval using plugin architecture with enhanced logging"""
    
    def __init__(self, 
                 embedding_provider: Optional[EmbeddingProvider] = None,
                 vector_store_provider: Optional[VectorStoreProvider] = None):
        """
        Initialize VectorStore with optional provider injection for testing.
        If providers are not provided, they will be obtained from the service locator.
        """
        logger.info("Initializing vector store", extra={
            'extra_fields': {
                'event_type': 'vector_store_initialization_start',
                'embedding_provider_injected': embedding_provider is not None,
                'vector_store_provider_injected': vector_store_provider is not None,
                'collection_name': Config.QDRANT_COLLECTION_NAME
            }
        })
        
        # Use injected providers or get from service locator
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.vector_store_provider = vector_store_provider or get_vector_store_provider()
        self.collection_name = Config.QDRANT_COLLECTION_NAME
        
        logger.info("Vector store initialized successfully", extra={
            'extra_fields': {
                'event_type': 'vector_store_initialization_complete',
                'embedding_provider_class': type(self.embedding_provider).__name__,
                'vector_store_provider_class': type(self.vector_store_provider).__name__,
                'collection_name': self.collection_name
            }
        })
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector store using plugin architecture with enhanced logging"""
        correlation_id = get_correlation_id()
        
        logger.info("Starting document addition to vector store", extra={
            'extra_fields': {
                'event_type': 'vector_store_add_documents_start',
                'documents_count': len(documents),
                'collection_name': self.collection_name,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Extract text content for embedding
            texts = [doc["content"] for doc in documents]
            
            logger.debug("Extracted text content for embedding", extra={
                'extra_fields': {
                    'event_type': 'vector_store_text_extraction_complete',
                    'documents_count': len(documents),
                    'total_text_length': sum(len(text) for text in texts),
                    'correlation_id': correlation_id
                }
            })
            
            # Get embeddings using plugin architecture
            logger.debug("Generating embeddings for documents", extra={
                'extra_fields': {
                    'event_type': 'vector_store_embedding_generation_start',
                    'documents_count': len(documents),
                    'correlation_id': correlation_id
                }
            })
            
            embeddings = await self.embedding_provider.get_embeddings(texts)
            
            logger.info("Embeddings generated successfully", extra={
                'extra_fields': {
                    'event_type': 'vector_store_embedding_generation_complete',
                    'documents_count': len(documents),
                    'embeddings_count': len(embeddings),
                    'embedding_dimensions': len(embeddings[0]) if embeddings else 0,
                    'correlation_id': correlation_id
                }
            })
            
            # Prepare points for vector database
            logger.debug("Preparing points for vector database", extra={
                'extra_fields': {
                    'event_type': 'vector_store_points_preparation_start',
                    'documents_count': len(documents),
                    'correlation_id': correlation_id
                }
            })
            
            points = []
            for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
                point = {
                    "id": str(uuid.uuid4()),
                    "vector": embedding,
                    "payload": {
                        "content": doc["content"],
                        "metadata": doc["metadata"]
                    }
                }
                points.append(point)
            
            logger.debug("Points prepared successfully", extra={
                'extra_fields': {
                    'event_type': 'vector_store_points_preparation_complete',
                    'points_count': len(points),
                    'correlation_id': correlation_id
                }
            })
            
            # Insert vectors using plugin architecture
            logger.debug("Inserting vectors into vector store", extra={
                'extra_fields': {
                    'event_type': 'vector_store_insertion_start',
                    'points_count': len(points),
                    'collection_name': self.collection_name,
                    'correlation_id': correlation_id
                }
            })
            
            success = await self.vector_store_provider.insert_vectors(points, self.collection_name)
            
            if success:
                logger.info("Documents added to vector store successfully", extra={
                    'extra_fields': {
                        'event_type': 'vector_store_add_documents_success',
                        'documents_count': len(documents),
                        'points_inserted': len(points),
                        'collection_name': self.collection_name,
                        'correlation_id': correlation_id
                    }
                })
            else:
                logger.error("Failed to add documents to vector store", extra={
                    'extra_fields': {
                        'event_type': 'vector_store_add_documents_failure',
                        'documents_count': len(documents),
                        'points_count': len(points),
                        'collection_name': self.collection_name,
                        'error': 'Vector store insertion failed',
                        'correlation_id': correlation_id
                    }
                })
            
            return success
            
        except Exception as e:
            logger.error("Error adding documents to vector store", extra={
                'extra_fields': {
                    'event_type': 'vector_store_add_documents_error',
                    'documents_count': len(documents),
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            return False
    
    async def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for similar documents using plugin architecture with enhanced logging"""
        correlation_id = get_correlation_id()
        
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        logger.info("Starting vector search", extra={
            'extra_fields': {
                'event_type': 'vector_store_search_start',
                'query_length': len(query),
                'top_k': top_k,
                'collection_name': self.collection_name,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Get query embedding using plugin architecture
            logger.debug("Generating query embedding", extra={
                'extra_fields': {
                    'event_type': 'vector_store_query_embedding_start',
                    'query_length': len(query),
                    'correlation_id': correlation_id
                }
            })
            
            query_embeddings = await self.embedding_provider.get_embeddings([query])
            query_vector = query_embeddings[0]
            
            logger.info("Query embedding generated successfully", extra={
                'extra_fields': {
                    'event_type': 'vector_store_query_embedding_complete',
                    'query_length': len(query),
                    'embedding_dimensions': len(query_vector),
                    'correlation_id': correlation_id
                }
            })
            
            # Search vectors using plugin architecture
            logger.debug("Searching vectors in vector store", extra={
                'extra_fields': {
                    'event_type': 'vector_store_vector_search_start',
                    'top_k': top_k,
                    'collection_name': self.collection_name,
                    'correlation_id': correlation_id
                }
            })
            
            results = await self.vector_store_provider.search_vectors(query_vector, top_k, self.collection_name)
            
            logger.info("Vector search completed successfully", extra={
                'extra_fields': {
                    'event_type': 'vector_store_vector_search_complete',
                    'top_k': top_k,
                    'results_found': len(results),
                    'collection_name': self.collection_name,
                    'correlation_id': correlation_id
                }
            })
            
            # Format results with better error handling
            logger.debug("Formatting search results", extra={
                'extra_fields': {
                    'event_type': 'vector_store_results_formatting_start',
                    'raw_results_count': len(results),
                    'correlation_id': correlation_id
                }
            })
            
            formatted_results = []
            for i, result in enumerate(results):
                try:
                    # Check if payload exists
                    if "payload" not in result:
                        logger.warning("Search result missing payload", extra={
                            'extra_fields': {
                                'event_type': 'vector_store_result_missing_payload',
                                'result_index': i,
                                'correlation_id': correlation_id
                            }
                        })
                        continue
                    
                    payload = result["payload"]
                    
                    # Check if content exists in payload (handle both "content" and "page_content" fields)
                    content = None
                    if "content" in payload:
                        content = payload["content"]
                    elif "page_content" in payload:
                        content = payload["page_content"]
                    else:
                        logger.warning("Search result missing content", extra={
                            'extra_fields': {
                                'event_type': 'vector_store_result_missing_content',
                                'result_index': i,
                                'correlation_id': correlation_id
                            }
                        })
                        continue
                    
                    formatted_result = {
                        "content": content,
                        "metadata": payload.get("metadata", {}),
                        "score": result.get("score", 0.0)
                    }
                    formatted_results.append(formatted_result)
                    
                except Exception as e:
                    logger.warning("Error processing search result", extra={
                        'extra_fields': {
                            'event_type': 'vector_store_result_processing_error',
                            'result_index': i,
                            'error': str(e),
                            'correlation_id': correlation_id
                        }
                    })
                    continue
            
            logger.info("Search results formatted successfully", extra={
                'extra_fields': {
                    'event_type': 'vector_store_search_complete',
                    'query_length': len(query),
                    'top_k': top_k,
                    'raw_results_count': len(results),
                    'formatted_results_count': len(formatted_results),
                    'correlation_id': correlation_id
                }
            })
            
            return formatted_results
            
        except Exception as e:
            logger.error("Error searching documents", extra={
                'extra_fields': {
                    'event_type': 'vector_store_search_error',
                    'query_length': len(query),
                    'top_k': top_k,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics with enhanced logging"""
        correlation_id = get_correlation_id()
        
        logger.debug("Getting collection statistics", extra={
            'extra_fields': {
                'event_type': 'vector_store_stats_request_start',
                'collection_name': self.collection_name,
                'correlation_id': correlation_id
            }
        })
        
        try:
            stats = self.vector_store_provider.get_collection_stats(self.collection_name)
            
            logger.info("Collection statistics retrieved successfully", extra={
                'extra_fields': {
                    'event_type': 'vector_store_stats_request_success',
                    'collection_name': self.collection_name,
                    'total_documents': stats.get('total_documents', 0),
                    'vector_size': stats.get('vector_size', 0),
                    'correlation_id': correlation_id
                }
            })
            
            return stats
            
        except Exception as e:
            logger.error("Error getting collection statistics", extra={
                'extra_fields': {
                    'event_type': 'vector_store_stats_request_error',
                    'collection_name': self.collection_name,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            return {
                "total_documents": 0,
                "collection_name": self.collection_name,
                "vector_size": 0
            }
    
    def delete_collection(self) -> bool:
        """Delete the collection with enhanced logging"""
        correlation_id = get_correlation_id()
        
        logger.warning("Deleting vector store collection", extra={
            'extra_fields': {
                'event_type': 'vector_store_collection_delete_start',
                'collection_name': self.collection_name,
                'correlation_id': correlation_id
            }
        })
        
        try:
            success = self.vector_store_provider.delete_collection(self.collection_name)
            
            if success:
                logger.warning("Vector store collection deleted successfully", extra={
                    'extra_fields': {
                        'event_type': 'vector_store_collection_delete_success',
                        'collection_name': self.collection_name,
                        'correlation_id': correlation_id
                    }
                })
            else:
                logger.error("Failed to delete vector store collection", extra={
                    'extra_fields': {
                        'event_type': 'vector_store_collection_delete_failure',
                        'collection_name': self.collection_name,
                        'correlation_id': correlation_id
                    }
                })
            
            return success
            
        except Exception as e:
            logger.error("Error deleting vector store collection", extra={
                'extra_fields': {
                    'event_type': 'vector_store_collection_delete_error',
                    'collection_name': self.collection_name,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            return False
    
    def clear_all_points(self) -> bool:
        """Clear all points from the collection with enhanced logging"""
        correlation_id = get_correlation_id()
        
        logger.warning("Clearing all points from vector store collection", extra={
            'extra_fields': {
                'event_type': 'vector_store_clear_points_start',
                'collection_name': self.collection_name,
                'correlation_id': correlation_id
            }
        })
        
        try:
            success = self.vector_store_provider.delete_all_points(self.collection_name)
            
            if success:
                logger.warning("All points cleared from vector store collection successfully", extra={
                    'extra_fields': {
                        'event_type': 'vector_store_clear_points_success',
                        'collection_name': self.collection_name,
                        'correlation_id': correlation_id
                    }
                })
            else:
                logger.error("Failed to clear points from vector store collection", extra={
                    'extra_fields': {
                        'event_type': 'vector_store_clear_points_failure',
                        'collection_name': self.collection_name,
                        'correlation_id': correlation_id
                    }
                })
            
            return success
            
        except Exception as e:
            logger.error("Error clearing points from vector store collection", extra={
                'extra_fields': {
                    'event_type': 'vector_store_clear_points_error',
                    'collection_name': self.collection_name,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            return False 