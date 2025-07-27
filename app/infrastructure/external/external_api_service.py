import httpx
import json
import os
from typing import List, Dict, Any, Optional, Union
from app.core.config import Config

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
                        "size": Config.VECTOR_SIZE,
                        "distance": Config.VECTOR_DISTANCE_METRIC
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
                "model": Config.EMBEDDING_MODEL
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
    
    async def call_llm_api(self, request: Dict[str, Any], return_full_response: bool = False) -> Union[str, Dict[str, Any]]:
        """Make LLM call using external API with flexible return format"""
        try:
            async with httpx.AsyncClient(**self._get_client_kwargs()) as client:
                response = await client.post(
                    Config.LLM_API_URL,
                    headers=self.openai_headers,
                    json=request
                )
                response.raise_for_status()
                
                data = response.json()
                
                if return_full_response:
                    return data
                else:
                    return data["choices"][0]["message"]["content"]
                    
        except Exception as e:
            raise Exception(f"LLM API error: {str(e)}")
    
    async def call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Make LLM call using external API - returns content string only"""
        payload = {
            "model": Config.LLM_MODEL,
            "messages": messages,
            "temperature": Config.LLM_TEMPERATURE,
            "max_tokens": Config.LLM_MAX_TOKENS
        }
        return await self.call_llm_api(payload, return_full_response=False)
    
    async def call_openai_completions(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Make OpenAI chat completions call with full request - returns full response"""
        return await self.call_llm_api(request, return_full_response=True)
    
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
                    "vector_size": Config.VECTOR_SIZE
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
    
    def delete_all_points(self) -> bool:
        """Delete all points in the collection without deleting the collection itself"""
        try:
            # Use the points deletion URL with a filter that matches all points
            points_url = f"{Config.VECTOR_COLLECTION_URL}/points/delete"
            
            # Filter that matches all points (empty filter matches everything)
            payload = {
                "filter": {}
            }
            
            with httpx.Client(**self._get_client_kwargs()) as client:
                response = client.post(
                    points_url,
                    headers=self.qdrant_headers,
                    json=payload
                )
                response.raise_for_status()
                return True
                
        except Exception as e:
            # Return True if collection doesn't exist or is empty
            return True 