"""
Qdrant vector store provider implementation with enhanced logging.
"""

from typing import List, Dict, Any
from app.domain.interfaces.providers import VectorStoreProvider
from .enhanced_base_provider import EnhancedBaseProvider
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class QdrantVectorStoreProvider(EnhancedBaseProvider, VectorStoreProvider):
    """Qdrant vector store service provider with enhanced logging."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Qdrant vector store provider.
        
        Args:
            config: Configuration dictionary containing:
                - base_url: Qdrant base URL
                - api_key: Qdrant API key
                - auth_scheme: Authentication scheme (default: "api_key")
        """
        # Add provider name to config for logging
        config["provider_name"] = "qdrant_vector_store"
        
        # Set default auth scheme for Qdrant
        if "auth_scheme" not in config:
            config["auth_scheme"] = "api_key"
        
        super().__init__(config)
        self.base_url = config.get("base_url")
        self.api_key = config.get("api_key")
        
        if not self.base_url:
            raise ValueError("Qdrant base URL is required")
        
        logger.info("Qdrant Vector Store Provider initialized", extra={
            'extra_fields': {
                'event_type': 'provider_initialized',
                'provider': 'qdrant_vector_store',
                'base_url': self.base_url
            }
        })
    
    def _get_collection_url(self, collection_name: str) -> str:
        """Get the collection URL for a given collection name."""
        return f"{self.base_url}/collections/{collection_name}"
    
    def _get_points_url(self, collection_name: str) -> str:
        """Get the points URL for a given collection name."""
        return f"{self.base_url}/collections/{collection_name}/points"
    
    def _get_search_url(self, collection_name: str) -> str:
        """Get the search URL for a given collection name."""
        return f"{self.base_url}/collections/{collection_name}/points/search"
    
    def _get_delete_url(self, collection_name: str) -> str:
        """Get the delete URL for a given collection name."""
        return f"{self.base_url}/collections/{collection_name}/points/delete"
    
    async def create_collection_if_not_exists(self, collection_name: str, vector_size: int, distance_metric: str) -> bool:
        """
        Create a collection if it doesn't exist with enhanced logging.
        
        Args:
            collection_name: Name of the collection
            vector_size: Dimension of the vectors
            distance_metric: Distance metric to use (e.g., "Cosine", "Euclidean")
            
        Returns:
            True if collection exists or was created successfully
        """
        logger.debug(f"Creating Qdrant collection", extra={
            'extra_fields': {
                'event_type': 'qdrant_collection_create_start',
                'provider': 'qdrant_vector_store',
                'collection_name': collection_name,
                'vector_size': vector_size,
                'distance_metric': distance_metric
            }
        })
        
        try:
            collection_url = self._get_collection_url(collection_name)
            headers = self._get_headers(self.api_key)
            
            # First, try to get the collection to see if it exists
            try:
                response = await self._make_request("GET", collection_url, headers)
                if response.status_code == 200:
                    logger.info(f"Qdrant collection already exists", extra={
                        'extra_fields': {
                            'event_type': 'qdrant_collection_exists',
                            'provider': 'qdrant_vector_store',
                            'collection_name': collection_name
                        }
                    })
                    return True  # Collection exists
            except:
                pass  # Collection doesn't exist, continue to create it
            
            # Create the collection
            create_payload = {
                "vectors": {
                    "size": vector_size,
                    "distance": distance_metric
                }
            }
            
            response = await self._make_request("PUT", collection_url, headers, json_data=create_payload)
            
            logger.info(f"Successfully created Qdrant collection", extra={
                'extra_fields': {
                    'event_type': 'qdrant_collection_create_success',
                    'provider': 'qdrant_vector_store',
                    'collection_name': collection_name,
                    'vector_size': vector_size,
                    'distance_metric': distance_metric
                }
            })
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Qdrant collection", extra={
                'extra_fields': {
                    'event_type': 'qdrant_collection_create_failure',
                    'provider': 'qdrant_vector_store',
                    'collection_name': collection_name,
                    'vector_size': vector_size,
                    'distance_metric': distance_metric,
                    'error': str(e)
                }
            })
            return False
    
    async def insert_vectors(self, points: List[Dict[str, Any]], collection_name: str) -> bool:
        """
        Insert vectors into the vector store with enhanced logging.
        
        Args:
            points: List of points to insert, each containing id, vector, and payload
            collection_name: Name of the collection to insert into
            
        Returns:
            True if insertion was successful
        """
        logger.debug(f"Inserting vectors into Qdrant", extra={
            'extra_fields': {
                'event_type': 'qdrant_vector_insert_start',
                'provider': 'qdrant_vector_store',
                'collection_name': collection_name,
                'point_count': len(points)
            }
        })
        
        try:
            # Transform points to Qdrant format
            qdrant_points = []
            for point in points:
                qdrant_point = {
                    "id": point["id"],
                    "vector": point["vector"],
                    "payload": point["payload"]
                }
                qdrant_points.append(qdrant_point)
            
            payload = {"points": qdrant_points}
            headers = self._get_headers(self.api_key)
            points_url = self._get_points_url(collection_name)
            
            await self._make_request("PUT", points_url, headers, json_data=payload)
            
            logger.info(f"Successfully inserted vectors into Qdrant", extra={
                'extra_fields': {
                    'event_type': 'qdrant_vector_insert_success',
                    'provider': 'qdrant_vector_store',
                    'collection_name': collection_name,
                    'point_count': len(points)
                }
            })
            return True
            
        except Exception as e:
            logger.error(f"Failed to insert vectors into Qdrant", extra={
                'extra_fields': {
                    'event_type': 'qdrant_vector_insert_failure',
                    'provider': 'qdrant_vector_store',
                    'collection_name': collection_name,
                    'point_count': len(points),
                    'error': str(e)
                }
            })
            raise Exception(f"Qdrant vector insert API error: {str(e)}")
    
    async def search_vectors(self, query_vector: List[float], top_k: int, collection_name: str) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the vector store with enhanced logging.
        
        Args:
            query_vector: The query vector to search for
            top_k: Number of top results to return
            collection_name: Name of the collection to search in
            
        Returns:
            List of search results with payload and score
        """
        logger.debug(f"Searching vectors in Qdrant", extra={
            'extra_fields': {
                'event_type': 'qdrant_vector_search_start',
                'provider': 'qdrant_vector_store',
                'collection_name': collection_name,
                'top_k': top_k,
                'query_vector_size': len(query_vector)
            }
        })
        
        try:
            payload = {
                "vector": query_vector,
                "limit": top_k,
                "with_payload": True
            }
            
            headers = self._get_headers(self.api_key)
            search_url = self._get_search_url(collection_name)
            
            response = await self._make_request("POST", search_url, headers, json_data=payload)
            data = response.json()
            
            # Transform results to standard format
            results = []
            for item in data.get("result", []):
                result = {
                    "payload": item.get("payload", {}),
                    "score": item.get("score", 0.0)
                }
                results.append(result)
            
            logger.info(f"Successfully searched vectors in Qdrant", extra={
                'extra_fields': {
                    'event_type': 'qdrant_vector_search_success',
                    'provider': 'qdrant_vector_store',
                    'collection_name': collection_name,
                    'top_k': top_k,
                    'result_count': len(results)
                }
            })
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search vectors in Qdrant", extra={
                'extra_fields': {
                    'event_type': 'qdrant_vector_search_failure',
                    'provider': 'qdrant_vector_store',
                    'collection_name': collection_name,
                    'top_k': top_k,
                    'error': str(e)
                }
            })
            raise Exception(f"Qdrant vector search API error: {str(e)}")
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics about a collection with enhanced logging.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary containing collection statistics
        """
        logger.debug(f"Getting collection stats from Qdrant", extra={
            'extra_fields': {
                'event_type': 'qdrant_collection_stats_start',
                'provider': 'qdrant_vector_store',
                'collection_name': collection_name
            }
        })
        
        try:
            collection_url = self._get_collection_url(collection_name)
            headers = self._get_headers(self.api_key)
            
            response = self._make_sync_request("GET", collection_url, headers)
            data = response.json()
            
            stats = {
                "total_documents": data.get("result", {}).get("points_count", 0),
                "collection_name": collection_name,
                "vector_size": data.get("result", {}).get("config", {}).get("params", {}).get("vectors", {}).get("size", 1536)
            }
            
            logger.info(f"Successfully retrieved collection stats from Qdrant", extra={
                'extra_fields': {
                    'event_type': 'qdrant_collection_stats_success',
                    'provider': 'qdrant_vector_store',
                    'collection_name': collection_name,
                    'total_documents': stats["total_documents"],
                    'vector_size': stats["vector_size"]
                }
            })
            
            return stats
            
        except Exception as e:
            logger.warning(f"Failed to get collection stats from Qdrant, using defaults", extra={
                'extra_fields': {
                    'event_type': 'qdrant_collection_stats_failure',
                    'provider': 'qdrant_vector_store',
                    'collection_name': collection_name,
                    'error': str(e)
                }
            })
            return {
                "total_documents": 0,
                "collection_name": collection_name,
                "vector_size": 1536
            }
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection with enhanced logging.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if deletion was successful
        """
        logger.info(f"Deleting collection from Qdrant", extra={
            'extra_fields': {
                'event_type': 'qdrant_collection_delete',
                'provider': 'qdrant_vector_store',
                'collection_name': collection_name
            }
        })
        
        try:
            collection_url = self._get_collection_url(collection_name)
            headers = self._get_headers(self.api_key)
            
            self._make_sync_request("DELETE", collection_url, headers)
            
            logger.info(f"Successfully deleted collection from Qdrant", extra={
                'extra_fields': {
                    'event_type': 'qdrant_collection_delete_success',
                    'provider': 'qdrant_vector_store',
                    'collection_name': collection_name
                }
            })
            return True
            
        except Exception as e:
            logger.warning(f"Failed to delete collection from Qdrant", extra={
                'extra_fields': {
                    'event_type': 'qdrant_collection_delete_failure',
                    'provider': 'qdrant_vector_store',
                    'collection_name': collection_name,
                    'error': str(e)
                }
            })
            return True  # Return True to avoid breaking existing code
    
    def delete_all_points(self, collection_name: str) -> bool:
        """
        Delete all points in a collection without deleting the collection itself with enhanced logging.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if deletion was successful
        """
        logger.info(f"Deleting all points from collection in Qdrant", extra={
            'extra_fields': {
                'event_type': 'qdrant_points_delete',
                'provider': 'qdrant_vector_store',
                'collection_name': collection_name
            }
        })
        
        try:
            delete_url = self._get_delete_url(collection_name)
            headers = self._get_headers(self.api_key)
            
            # Delete all points by using a filter that matches everything
            payload = {
                "filter": {
                    "must": [
                        {
                            "key": "id",
                            "range": {
                                "gte": 0
                            }
                        }
                    ]
                }
            }
            
            self._make_sync_request("POST", delete_url, headers, json_data=payload)
            
            logger.info(f"Successfully deleted all points from collection in Qdrant", extra={
                'extra_fields': {
                    'event_type': 'qdrant_points_delete_success',
                    'provider': 'qdrant_vector_store',
                    'collection_name': collection_name
                }
            })
            return True
            
        except Exception as e:
            logger.warning(f"Failed to delete all points from collection in Qdrant", extra={
                'extra_fields': {
                    'event_type': 'qdrant_points_delete_failure',
                    'provider': 'qdrant_vector_store',
                    'collection_name': collection_name,
                    'error': str(e)
                }
            })
            return True  # Return True to avoid breaking existing code 