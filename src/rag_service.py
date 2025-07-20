from typing import List, Dict, Any, Optional
from src.document_loader import DocumentLoader
from src.vector_store import VectorStore
from src.external_api_service import ExternalAPIService
from src.config import Config

class RAGService:
    """Main RAG service that orchestrates document processing and Q&A using external APIs"""
    
    def __init__(self):
        self.document_loader = DocumentLoader()
        self.vector_store = VectorStore()
        self.api_service = ExternalAPIService()
        
        # Define the RAG prompt template
        self.rag_prompt = """You are a helpful AI assistant that answers questions based on the provided context. 
        Use only the information from the context to answer the question. If the context doesn't contain 
        enough information to answer the question, say "I don't have enough information to answer this question."
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:"""
    
    async def add_document(self, file_path: str) -> Dict[str, Any]:
        """Add a document to the knowledge base"""
        try:
            # Load and process document
            documents = self.document_loader.load_document(file_path)
            
            # Add to vector store using external APIs
            success = await self.vector_store.add_documents(documents)
            
            if success:
                return {
                    "success": True,
                    "message": f"Document '{file_path}' added successfully",
                    "chunks_processed": len(documents)
                }
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
            
            # Add to vector store using external APIs
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
        """Ask a question and get an answer using RAG with external APIs"""
        try:
            # Search for relevant documents using external APIs
            relevant_docs = await self.vector_store.search(question, top_k)
            
            if not relevant_docs:
                return {
                    "success": False,
                    "answer": "No relevant documents found to answer your question.",
                    "sources": []
                }
            
            # Prepare context from relevant documents
            context = "\n\n".join([doc["content"] for doc in relevant_docs])
            
            # Generate answer using external LLM API
            messages = [
                {"role": "system", "content": self.rag_prompt.format(context=context, question=question)},
                {"role": "user", "content": question}
            ]
            
            answer = await self.api_service.call_llm(messages)
            
            # Prepare sources information
            sources = []
            for doc in relevant_docs:
                sources.append({
                    "content": doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
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
            
            return {
                "success": True,
                "vector_store": vector_stats,
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
            success = self.vector_store.delete_collection()
            
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