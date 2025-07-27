"""
Qdrant vector store provider implementation.
"""

from typing import List, Dict, Any
from app.domain.interfaces.providers import VectorStoreProvider
from .base_provider import BaseProvider


class QdrantVectorStoreProvider(BaseProvider, VectorStoreProvider):
    """Qdrant vector store service provider."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Qdrant vector store provider.
        
        Args:
            config: Configuration dictionary containing:
                - base_url: Qdrant base URL
                - api_key: Qdrant API key
                - auth_scheme: Authentication scheme (default: "api_key")
        """
        # Set default auth scheme for Qdrant
        if "auth_scheme" not in config:
            config["auth_scheme"] = "api_key"
        
        super().__init__(config)
        self.base_url = config.get("base_url")
        self.api_key = config.get("api_key")
        
        if not self.base_url:
            raise ValueError("Qdrant base URL is required")
    
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
        Create a collection if it doesn't exist.
        
        Args:
            collection_name: Name of the collection
            vector_size: Dimension of the vectors
            distance_metric: Distance metric to use (e.g., "Cosine", "Euclidean")
            
        Returns:
            True if collection exists or was created successfully
        """
        try:
            collection_url = self._get_collection_url(collection_name)
            headers = self._get_headers(self.api_key)
            
            # First, try to get the collection to see if it exists
            try:
                response = await self._make_request("GET", collection_url, headers)
                if response.status_code == 200:
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
            print(f"Created Qdrant collection: {collection_name}")
            return True
            
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False
    
    async def insert_vectors(self, points: List[Dict[str, Any]], collection_name: str) -> bool:
        """
        Insert vectors into the vector store.
        
        Args:
            points: List of points to insert, each containing id, vector, and payload
            collection_name: Name of the collection to insert into
            
        Returns:
            True if insertion was successful
        """
        try:
            # Ensure collection exists first
            await self.create_collection_if_not_exists(
                collection_name, 
                len(points[0]["vector"]) if points else 1536, 
                "Cosine"
            )
            
            payload = {"points": points}
            headers = self._get_headers(self.api_key)
            points_url = self._get_points_url(collection_name)
            
            await self._make_request("PUT", points_url, headers, json_data=payload)
            return True
            
        except Exception as e:
            raise Exception(f"Qdrant vector insert API error: {str(e)}")
    
    async def search_vectors(self, query_vector: List[float], top_k: int, collection_name: str) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in the vector store.
        
        Args:
            query_vector: The query vector to search for
            top_k: Number of top results to return
            collection_name: Name of the collection to search in
            
        Returns:
            List of search results with payload and score
        """
        try:
            payload = {
                "vector": query_vector,
                "limit": top_k,
                "with_payload": True,
                "with_vector": False
            }
            
            headers = self._get_headers(self.api_key)
            search_url = self._get_search_url(collection_name)
            
            response = await self._make_request("POST", search_url, headers, json_data=payload)
            data = response.json()
            return data.get("result", [])
            
        except Exception as e:
            raise Exception(f"Qdrant vector search API error: {str(e)}")
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary containing collection statistics
        """
        try:
            collection_url = self._get_collection_url(collection_name)
            headers = self._get_headers(self.api_key)
            
            response = self._make_sync_request("GET", collection_url, headers)
            data = response.json()
            
            return {
                "total_documents": data["result"]["points_count"],
                "collection_name": collection_name,
                "vector_size": data["result"]["config"]["params"]["vectors"]["size"]
            }
            
        except Exception as e:
            # Return default stats if collection doesn't exist
            return {
                "total_documents": 0,
                "collection_name": collection_name,
                "vector_size": 1536
            }
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            collection_url = self._get_collection_url(collection_name)
            headers = self._get_headers(self.api_key)
            
            self._make_sync_request("DELETE", collection_url, headers)
            return True
            
        except Exception as e:
            # Return True if collection doesn't exist (already deleted)
            return True
    
    def delete_all_points(self, collection_name: str) -> bool:
        """
        Delete all points in a collection without deleting the collection itself.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if deletion was successful
        """
        try:
            delete_url = self._get_delete_url(collection_name)
            headers = self._get_headers(self.api_key)
            
            # Filter that matches all points (empty filter matches everything)
            payload = {"filter": {}}
            
            self._make_sync_request("POST", delete_url, headers, json_data=payload)
            return True
            
        except Exception as e:
            # Return True if collection doesn't exist or is empty
            return True 