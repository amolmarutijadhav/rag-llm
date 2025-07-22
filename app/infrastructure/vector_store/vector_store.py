import uuid
import json
from typing import List, Dict, Any, Optional
from app.core.config import Config
from app.infrastructure.external.external_api_service import ExternalAPIService

class VectorStore:
    """Handles vector storage and retrieval using external APIs"""
    
    def __init__(self):
        self.api_service = ExternalAPIService()
        self.collection_name = Config.QDRANT_COLLECTION_NAME
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector store using external APIs"""
        try:
            # Extract text content for embedding
            texts = [doc["content"] for doc in documents]
            
            # Get embeddings using external API
            embeddings = await self.api_service.get_embeddings(texts)
            
            # Prepare points for vector database
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
            
            # Insert vectors using external API
            success = await self.api_service.insert_vectors(points)
            return success
            
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    async def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for similar documents using external APIs"""
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        try:
            # Get query embedding
            query_embeddings = await self.api_service.get_embeddings([query])
            query_vector = query_embeddings[0]
            
            # Search vectors using external API
            results = await self.api_service.search_vectors(query_vector, top_k)
            
            # Format results with better error handling
            formatted_results = []
            for i, result in enumerate(results):
                try:
                    # Check if payload exists
                    if "payload" not in result:
                        continue
                    
                    payload = result["payload"]
                    
                    # Check if content exists in payload (handle both "content" and "page_content" fields)
                    content = None
                    if "content" in payload:
                        content = payload["content"]
                    elif "page_content" in payload:
                        content = payload["page_content"]
                    else:
                        continue
                    
                    formatted_result = {
                        "content": content,
                        "metadata": payload.get("metadata", {}),
                        "score": result.get("score", 0.0)
                    }
                    formatted_results.append(formatted_result)
                    
                except Exception as e:
                    print(f"Error processing search result {i}: {e}")
                    continue
            return formatted_results
            
        except Exception as e:
            print(f"Error searching documents: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            return self.api_service.get_collection_stats()
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {"total_documents": 0, "collection_name": self.collection_name}
    
    def delete_collection(self) -> bool:
        """Delete the entire collection"""
        try:
            return self.api_service.delete_collection()
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False 