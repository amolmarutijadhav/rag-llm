"""
Abstract base classes for external service providers.
Defines contracts for embedding, vector store, and LLM providers.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union, Optional


class EmbeddingProvider(ABC):
    """Abstract base class for embedding service providers."""
    
    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of text strings.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
            
        Raises:
            Exception: If embedding generation fails
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model being used.
        
        Returns:
            Dictionary containing model information (name, dimensions, etc.)
        """
        pass


class VectorStoreProvider(ABC):
    """Abstract base class for vector store service providers."""
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def insert_vectors(self, points: List[Dict[str, Any]], collection_name: str) -> bool:
        """
        Insert vectors into the vector store.
        
        Args:
            points: List of points to insert, each containing id, vector, and payload
            collection_name: Name of the collection to insert into
            
        Returns:
            True if insertion was successful
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics about a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary containing collection statistics
        """
        pass
    
    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if deletion was successful
        """
        pass
    
    @abstractmethod
    def delete_all_points(self, collection_name: str) -> bool:
        """
        Delete all points in a collection without deleting the collection itself.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if deletion was successful
        """
        pass


class LLMProvider(ABC):
    """Abstract base class for LLM service providers."""
    
    @abstractmethod
    async def call_llm(self, messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int) -> str:
        """
        Make a simple LLM call and return the content string.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text content as string
        """
        pass
    
    @abstractmethod
    async def call_llm_api(self, request: Dict[str, Any], return_full_response: bool = False) -> Union[str, Dict[str, Any]]:
        """
        Make a flexible LLM API call.
        
        Args:
            request: Complete request dictionary
            return_full_response: If True, return full response dict; if False, return content string
            
        Returns:
            Either content string or full response dictionary
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the LLM model being used.
        
        Returns:
            Dictionary containing model information
        """
        pass 