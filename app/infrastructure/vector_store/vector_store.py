import uuid
import json
from typing import List, Dict, Any, Optional
from app.core.config import Config
from app.domain.interfaces.providers import EmbeddingProvider, VectorStoreProvider
from app.infrastructure.providers import get_embedding_provider, get_vector_store_provider

class VectorStore:
    """Handles vector storage and retrieval using plugin architecture"""
    
    def __init__(self, 
                 embedding_provider: Optional[EmbeddingProvider] = None,
                 vector_store_provider: Optional[VectorStoreProvider] = None):
        """
        Initialize VectorStore with optional provider injection for testing.
        If providers are not provided, they will be obtained from the service locator.
        """
        # Use injected providers or get from service locator
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.vector_store_provider = vector_store_provider or get_vector_store_provider()
        self.collection_name = Config.QDRANT_COLLECTION_NAME
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector store using plugin architecture"""
        try:
            # Extract text content for embedding
            texts = [doc["content"] for doc in documents]
            
            # Get embeddings using plugin architecture
            embeddings = await self.embedding_provider.get_embeddings(texts)
            
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
            
            # Insert vectors using plugin architecture
            success = await self.vector_store_provider.insert_vectors(points, self.collection_name)
            return success
            
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    async def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for similar documents using plugin architecture"""
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        try:
            # Get query embedding using plugin architecture
            query_embeddings = await self.embedding_provider.get_embeddings([query])
            query_vector = query_embeddings[0]
            
            # Search vectors using plugin architecture
            results = await self.vector_store_provider.search_vectors(query_vector, top_k, self.collection_name)
            
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
            return self.vector_store_provider.get_collection_stats(self.collection_name)
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {"total_documents": 0, "collection_name": self.collection_name}
    
    def delete_collection(self) -> bool:
        """Delete the entire collection"""
        try:
            return self.vector_store_provider.delete_collection(self.collection_name)
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False
    
    def clear_all_points(self) -> bool:
        """Clear all points in the collection without deleting the collection itself"""
        try:
            return self.vector_store_provider.delete_all_points(self.collection_name)
        except Exception as e:
            print(f"Error clearing all points: {e}")
            return False 