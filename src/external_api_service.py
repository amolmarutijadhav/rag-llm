import httpx
import json
import os
from typing import List, Dict, Any, Optional
from src.config import Config

class ExternalAPIService:
    """Service for making external API calls with complete URLs and certificate support"""
    
    def __init__(self):
        self.timeout = Config.REQUEST_TIMEOUT
        self.max_retries = Config.MAX_RETRIES
        self.ssl_config = Config.get_ssl_config()
        
        # Common headers
        self.openai_headers = {
            "Authorization": f"Bearer {Config.OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        self.qdrant_headers = {
            "api-key": Config.QDRANT_API_KEY,
            "Content-Type": "application/json"
        }
    
    def _get_client_kwargs(self):
        """Get common client configuration"""
        return {
            "timeout": self.timeout,
            **self.ssl_config
        }
    
    async def create_collection_if_not_exists(self):
        """Create the collection if it doesn't exist"""
        try:
            # Use the dedicated collection URL
            collection_url = Config.VECTOR_COLLECTION_URL
            
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                try:
                    response = await client.get(
                        collection_url,
                        headers=self.qdrant_headers
                    )
                    if response.status_code == 200:
                        return True  # Collection exists
                except:
                    pass
                
                # Collection doesn't exist, create it
                create_payload = {
                    "vectors": {
                        "size": 1536,
                        "distance": "Cosine"
                    }
                }
                
                response = await client.put(
                    collection_url,
                    headers=self.qdrant_headers,
                    json=create_payload
                )
                response.raise_for_status()
                print(f"Created Qdrant collection: {Config.QDRANT_COLLECTION_NAME}")
                return True
                
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for text chunks using external embedding API"""
        try:
            payload = {
                "input": texts,
                "model": "text-embedding-ada-002"
            }
            
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                response = await client.post(
                    Config.EMBEDDING_API_URL,
                    headers=self.openai_headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                return [item["embedding"] for item in data["data"]]
                
        except Exception as e:
            raise Exception(f"Embedding API error: {str(e)}")
    
    async def insert_vectors(self, points: List[Dict[str, Any]]) -> bool:
        """Insert vectors into vector database using external API"""
        try:
            # Ensure collection exists
            await self.create_collection_if_not_exists()
            
            payload = {
                "points": points
            }
            
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                response = await client.put(
                    Config.VECTOR_INSERT_API_URL,
                    headers=self.qdrant_headers,
                    json=payload
                )
                response.raise_for_status()
                return True
                
        except Exception as e:
            raise Exception(f"Vector insert API error: {str(e)}")
    
    async def search_vectors(self, query_vector: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Search vectors in database using external API"""
        try:
            payload = {
                "vector": query_vector,
                "limit": top_k,
                "with_payload": True,
                "with_vector": False
            }
            
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                response = await client.post(
                    Config.VECTOR_SEARCH_API_URL,
                    headers=self.qdrant_headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                return data.get("result", [])
                
        except Exception as e:
            raise Exception(f"Vector search API error: {str(e)}")
    
    async def call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Make LLM call using external API"""
        try:
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 0.1,
                "max_tokens": 1000
            }
            
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                response = await client.post(
                    Config.LLM_API_URL,
                    headers=self.openai_headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                return data["choices"][0]["message"]["content"]
                
        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics using external API"""
        try:
            # Use the dedicated collection URL
            collection_url = Config.VECTOR_COLLECTION_URL
            
            with httpx.Client(**self._get_client_kwargs()) as client:
                response = client.get(
                    collection_url,
                    headers=self.qdrant_headers
                )
                response.raise_for_status()
                
                data = response.json()
                return {
                    "total_documents": data["result"]["points_count"],
                    "collection_name": Config.QDRANT_COLLECTION_NAME,
                    "vector_size": data["result"]["config"]["params"]["vectors"]["size"]
                }
                
        except Exception as e:
            # Return default stats if collection doesn't exist
            return {
                "total_documents": 0,
                "collection_name": Config.QDRANT_COLLECTION_NAME,
                "vector_size": 1536
            }
    
    def delete_collection(self) -> bool:
        """Delete collection using external API"""
        try:
            # Use the dedicated collection URL
            collection_url = Config.VECTOR_COLLECTION_URL
            
            with httpx.Client(**self._get_client_kwargs()) as client:
                response = client.delete(
                    collection_url,
                    headers=self.qdrant_headers
                )
                response.raise_for_status()
                return True
                
        except Exception as e:
            # Return True if collection doesn't exist (already deleted)
            return True 