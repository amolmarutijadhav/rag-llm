"""
Sample in-house provider implementations.
These are example implementations showing how to create custom providers for internal services.
"""

from typing import List, Dict, Any, Union
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider, VectorStoreProvider
from .base_provider import BaseProvider


class InhouseEmbeddingProvider(BaseProvider, EmbeddingProvider):
    """Sample in-house embedding service provider."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize in-house embedding provider.
        
        Args:
            config: Configuration dictionary containing:
                - api_url: In-house embeddings API URL
                - api_key: In-house API key
                - model: Embedding model name
                - auth_scheme: Authentication scheme
        """
        super().__init__(config)
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
        self.model = config.get("model", "inhouse-embedding-model")
        
        if not self.api_url:
            raise ValueError("In-house embedding API URL is required")
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for text chunks using in-house API.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            Exception: If embedding generation fails
        """
        try:
            # Example payload structure for in-house API
            payload = {
                "texts": texts,
                "model": self.model,
                "format": "vector"
            }
            
            headers = self._get_headers(self.api_key)
            response = await self._make_request("POST", self.api_url, headers, json_data=payload)
            
            data = response.json()
            # Assuming in-house API returns embeddings in a different format
            return data.get("embeddings", [])
            
        except Exception as e:
            raise Exception(f"In-house embedding API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the in-house embedding model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "provider": "inhouse",
            "model": self.model,
            "api_url": self.api_url,
            "vector_size": 768  # Example size for in-house model
        }


class InhouseLLMProvider(BaseProvider, LLMProvider):
    """Sample in-house LLM service provider."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize in-house LLM provider.
        
        Args:
            config: Configuration dictionary containing:
                - api_url: In-house LLM API URL
                - api_key: In-house API key
                - default_model: Default model name
                - default_temperature: Default temperature
                - default_max_tokens: Default max tokens
        """
        super().__init__(config)
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
        self.default_model = config.get("default_model", "inhouse-llm-model")
        self.default_temperature = config.get("default_temperature", 0.1)
        self.default_max_tokens = config.get("default_max_tokens", 1000)
        
        if not self.api_url:
            raise ValueError("In-house LLM API URL is required")
    
    async def call_llm(self, messages: List[Dict[str, str]], model: str = None, 
                      temperature: float = None, max_tokens: int = None) -> str:
        """
        Make a simple LLM call and return the content string.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use (uses default if not provided)
            temperature: Sampling temperature (uses default if not provided)
            max_tokens: Maximum tokens to generate (uses default if not provided)
            
        Returns:
            Generated text content as string
        """
        # Use defaults if not provided
        model = model or self.default_model
        temperature = temperature if temperature is not None else self.default_temperature
        max_tokens = max_tokens if max_tokens is not None else self.default_max_tokens
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        return await self.call_llm_api(payload, return_full_response=False)
    
    async def call_llm_api(self, request: Dict[str, Any], return_full_response: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Make a flexible LLM API call.
        
        Args:
            request: Complete request dictionary
            return_full_response: If True, return full response dict; if False, return content string
            
        Returns:
            Either content string or full response dictionary
        """
        try:
            headers = self._get_headers(self.api_key)
            response = await self._make_request("POST", self.api_url, headers, json_data=request)
            
            data = response.json()
            
            if return_full_response:
                return data
            else:
                # Assuming in-house API returns content in a different field
                return data.get("response", data.get("content", ""))
                
        except Exception as e:
            raise Exception(f"In-house LLM API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the in-house LLM model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            "provider": "inhouse",
            "default_model": self.default_model,
            "api_url": self.api_url,
            "default_temperature": self.default_temperature,
            "default_max_tokens": self.default_max_tokens
        }


class InhouseVectorStoreProvider(BaseProvider, VectorStoreProvider):
    """Sample in-house vector store service provider."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize in-house vector store provider.
        
        Args:
            config: Configuration dictionary containing:
                - base_url: In-house vector store base URL
                - api_key: In-house API key
        """
        super().__init__(config)
        self.base_url = config.get("base_url")
        self.api_key = config.get("api_key")
        
        if not self.base_url:
            raise ValueError("In-house vector store base URL is required")
    
    def _get_collection_url(self, collection_name: str) -> str:
        """Get the collection URL for a given collection name."""
        return f"{self.base_url}/collections/{collection_name}"
    
    def _get_points_url(self, collection_name: str) -> str:
        """Get the points URL for a given collection name."""
        return f"{self.base_url}/collections/{collection_name}/points"
    
    def _get_search_url(self, collection_name: str) -> str:
        """Get the search URL for a given collection name."""
        return f"{self.base_url}/collections/{collection_name}/search"
    
    async def create_collection_if_not_exists(self, collection_name: str, vector_size: int, distance_metric: str) -> bool:
        """
        Create a collection if it doesn't exist.
        
        Args:
            collection_name: Name of the collection
            vector_size: Dimension of the vectors
            distance_metric: Distance metric to use
            
        Returns:
            True if collection exists or was created successfully
        """
        try:
            collection_url = self._get_collection_url(collection_name)
            headers = self._get_headers(self.api_key)
            
            # Example payload for in-house API
            create_payload = {
                "name": collection_name,
                "vector_dimension": vector_size,
                "distance_metric": distance_metric
            }
            
            await self._make_request("POST", collection_url, headers, json_data=create_payload)
            print(f"Created in-house collection: {collection_name}")
            return True
            
        except Exception as e:
            print(f"Error creating in-house collection: {e}")
            return False
    
    async def insert_vectors(self, points: List[Dict[str, Any]], collection_name: str) -> bool:
        """
        Insert vectors into the vector store.
        
        Args:
            points: List of points to insert
            collection_name: Name of the collection to insert into
            
        Returns:
            True if insertion was successful
        """
        try:
            # Transform points to in-house format if needed
            transformed_points = []
            for point in points:
                transformed_point = {
                    "id": point["id"],
                    "vector": point["vector"],
                    "metadata": point["payload"]
                }
                transformed_points.append(transformed_point)
            
            payload = {"vectors": transformed_points}
            headers = self._get_headers(self.api_key)
            points_url = self._get_points_url(collection_name)
            
            await self._make_request("POST", points_url, headers, json_data=payload)
            return True
            
        except Exception as e:
            raise Exception(f"In-house vector insert API error: {str(e)}")
    
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
                "query_vector": query_vector,
                "limit": top_k,
                "include_metadata": True
            }
            
            headers = self._get_headers(self.api_key)
            search_url = self._get_search_url(collection_name)
            
            response = await self._make_request("POST", search_url, headers, json_data=payload)
            data = response.json()
            
            # Transform results to standard format
            results = []
            for item in data.get("results", []):
                result = {
                    "payload": {
                        "content": item.get("metadata", {}).get("content"),
                        "metadata": item.get("metadata", {})
                    },
                    "score": item.get("similarity", 0.0)
                }
                results.append(result)
            
            return results
            
        except Exception as e:
            raise Exception(f"In-house vector search API error: {str(e)}")
    
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
                "total_documents": data.get("document_count", 0),
                "collection_name": collection_name,
                "vector_size": data.get("vector_dimension", 1536)
            }
            
        except Exception as e:
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
            delete_url = f"{self._get_points_url(collection_name)}/clear"
            headers = self._get_headers(self.api_key)
            
            self._make_sync_request("POST", delete_url, headers)
            return True
            
        except Exception as e:
            return True 