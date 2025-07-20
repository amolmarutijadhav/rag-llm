import os
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from src.config import Config

class VectorStore:
    """Handles vector storage and retrieval using Qdrant Cloud"""
    
    def __init__(self):
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=Config.OPENAI_API_KEY,
            openai_api_base=Config.OPENAI_API_BASE
        )
        
        # Initialize Qdrant client with cloud configuration
        if Config.QDRANT_API_KEY:
            # Cloud configuration
            self.client = QdrantClient(
                url=Config.QDRANT_HOST,
                api_key=Config.QDRANT_API_KEY
            )
        else:
            # Local configuration (fallback)
            self.client = QdrantClient(
                host=Config.QDRANT_HOST,
                port=Config.QDRANT_PORT
            )
        
        # Initialize LangChain vector store
        self.vector_store = Qdrant(
            client=self.client,
            collection_name=Config.QDRANT_COLLECTION_NAME,
            embeddings=self.embeddings
        )
        
        # Ensure collection exists
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Ensure the collection exists with proper configuration"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if Config.QDRANT_COLLECTION_NAME not in collection_names:
                # Create collection with proper configuration
                self.client.create_collection(
                    collection_name=Config.QDRANT_COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI embedding dimension
                        distance=Distance.COSINE
                    )
                )
                print(f"Created Qdrant collection: {Config.QDRANT_COLLECTION_NAME}")
        except Exception as e:
            print(f"Error ensuring collection exists: {e}")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Add documents to the vector store"""
        try:
            # Prepare documents for LangChain
            from langchain.schema import Document
            
            langchain_docs = []
            for doc in documents:
                langchain_docs.append(Document(
                    page_content=doc["content"],
                    metadata=doc["metadata"]
                ))
            
            # Add to Qdrant using LangChain
            self.vector_store.add_documents(langchain_docs)
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if top_k is None:
            top_k = Config.TOP_K_RESULTS
        
        try:
            # Search using LangChain vector store
            results = self.vector_store.similarity_search_with_score(
                query, k=top_k
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score)
                })
            
            return formatted_results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            collection_info = self.client.get_collection(Config.QDRANT_COLLECTION_NAME)
            return {
                "total_documents": collection_info.points_count,
                "collection_name": Config.QDRANT_COLLECTION_NAME,
                "vector_size": collection_info.config.params.vectors.size
            }
        except Exception as e:
            print(f"Error getting collection stats: {e}")
            return {"total_documents": 0, "collection_name": Config.QDRANT_COLLECTION_NAME}
    
    def delete_collection(self) -> bool:
        """Delete the entire collection"""
        try:
            self.client.delete_collection(Config.QDRANT_COLLECTION_NAME)
            return True
        except Exception as e:
            print(f"Error deleting collection: {e}")
            return False 