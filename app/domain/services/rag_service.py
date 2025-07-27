from typing import List, Dict, Any, Optional
from app.infrastructure.document_processing.loader import DocumentLoader
from app.infrastructure.vector_store.vector_store import VectorStore
from app.infrastructure.providers import get_embedding_provider, get_llm_provider, get_vector_store_provider
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider, VectorStoreProvider
from app.core.config import Config
import os

class RAGService:
    """Main RAG service that orchestrates document processing and Q&A using plugin architecture"""
    
    def __init__(self, 
                 embedding_provider: Optional[EmbeddingProvider] = None,
                 llm_provider: Optional[LLMProvider] = None,
                 vector_store_provider: Optional[VectorStoreProvider] = None):
        """
        Initialize RAG service with optional provider injection for testing.
        If providers are not provided, they will be obtained from the service locator.
        """
        self.document_loader = DocumentLoader()
        
        # Use injected providers or get from service locator
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.llm_provider = llm_provider or get_llm_provider()
        self.vector_store_provider = vector_store_provider or get_vector_store_provider()
        
        # Initialize vector store with the provider
        self.vector_store = VectorStore(vector_store_provider=self.vector_store_provider)
    
    async def add_document(self, file_path: str) -> Dict[str, Any]:
        """Add a document to the knowledge base"""
        try:
            # Load and process document
            documents, ocr_text = self.document_loader.load_document(file_path)
            
            # Add to vector store using plugin architecture
            success = await self.vector_store.add_documents(documents)
            
            if success:
                response = {
                    "success": True,
                    "message": f"Document '{file_path}' added successfully",
                    "chunks_processed": len(documents)
                }
                
                # Add OCR text to response if available
                if ocr_text:
                    response["extracted_text"] = ocr_text
                
                return response
            else:
                return {
                    "success": False,
                    "message": "Failed to add document to vector store"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing document: {str(e)}"
            }
    
    async def add_text(self, text: str, source_name: str = "text_input") -> Dict[str, Any]:
        """Add raw text to the knowledge base"""
        try:
            # Validate text is not empty
            if not text or not text.strip():
                return {
                    "success": False,
                    "message": "Error processing text: Text cannot be empty"
                }
            
            # Load and process text
            documents = self.document_loader.load_text(text, source_name)
            
            # Add to vector store using plugin architecture
            success = await self.vector_store.add_documents(documents)
            
            if success:
                return {
                    "success": True,
                    "message": f"Text from '{source_name}' added successfully",
                    "chunks_processed": len(documents)
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to add text to vector store"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing text: {str(e)}"
            }
    
    async def ask_question(self, question: str, top_k: int = None) -> Dict[str, Any]:
        """Ask a question and get an answer using RAG with plugin architecture"""
        try:
            # Use default top_k from config if not provided
            if top_k is None:
                top_k = Config.DEFAULT_TOP_K
                
            # Search for relevant documents using plugin architecture
            relevant_docs = await self.vector_store.search(question, top_k)
            
            if not relevant_docs:
                return {
                    "success": False,
                    "answer": "No relevant documents found to answer your question.",
                    "sources": []
                }
            
            # Prepare context from relevant documents
            context = "\n\n".join([doc["content"] for doc in relevant_docs])
            
            # Generate answer using plugin architecture LLM provider
            messages = [
                {"role": "system", "content": Config.RAG_PROMPT_TEMPLATE.format(context=context, question=question)},
                {"role": "user", "content": question}
            ]
            
            answer = await self.llm_provider.call_llm(
                messages=messages,
                model=Config.LLM_MODEL,
                temperature=Config.LLM_TEMPERATURE,
                max_tokens=Config.LLM_MAX_TOKENS
            )
            
            # Prepare sources information with configurable preview length
            sources = []
            for doc in relevant_docs:
                preview_length = Config.CONTENT_PREVIEW_LENGTH
                content_preview = doc["content"][:preview_length] + "..." if len(doc["content"]) > preview_length else doc["content"]
                sources.append({
                    "content": content_preview,
                    "metadata": doc["metadata"],
                    "score": doc["score"]
                })
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "context_used": context
            }
            
        except Exception as e:
            return {
                "success": False,
                "answer": f"Error generating answer: {str(e)}",
                "sources": []
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            vector_stats = self.vector_store.get_collection_stats()
            
            # Get provider information
            embedding_info = self.embedding_provider.get_model_info()
            llm_info = self.llm_provider.get_model_info()
            
            return {
                "success": True,
                "vector_store": vector_stats,
                "embedding_provider": embedding_info,
                "llm_provider": llm_info,
                "supported_formats": Config.SUPPORTED_FORMATS,
                "chunk_size": Config.CHUNK_SIZE,
                "chunk_overlap": Config.CHUNK_OVERLAP
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting stats: {str(e)}"
            }
    
    def clear_knowledge_base(self) -> Dict[str, Any]:
        """Clear all documents from the knowledge base"""
        try:
            success = self.vector_store.clear_all_points()
            
            if success:
                return {
                    "success": True,
                    "message": "Knowledge base cleared successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to clear knowledge base"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error clearing knowledge base: {str(e)}"
            } 