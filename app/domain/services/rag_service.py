from typing import List, Dict, Any, Optional
from app.infrastructure.document_processing.loader import DocumentLoader
from app.infrastructure.vector_store.vector_store import VectorStore
from app.infrastructure.providers import get_embedding_provider, get_llm_provider, get_vector_store_provider
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider, VectorStoreProvider
from app.core.config import Config
from app.core.logging_config import get_logger, get_correlation_id
import os

logger = get_logger(__name__)

class RAGService:
    """Main RAG service that orchestrates document processing and Q&A using plugin architecture with enhanced logging"""
    
    def __init__(self, 
                 embedding_provider: Optional[EmbeddingProvider] = None,
                 llm_provider: Optional[LLMProvider] = None,
                 vector_store_provider: Optional[VectorStoreProvider] = None):
        """
        Initialize RAG service with optional provider injection for testing.
        If providers are not provided, they will be obtained from the service locator.
        """
        logger.info("Initializing RAG service", extra={
            'extra_fields': {
                'event_type': 'rag_service_initialization_start',
                'embedding_provider_injected': embedding_provider is not None,
                'llm_provider_injected': llm_provider is not None,
                'vector_store_provider_injected': vector_store_provider is not None
            }
        })
        
        self.document_loader = DocumentLoader()
        
        # Use injected providers or get from service locator
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.llm_provider = llm_provider or get_llm_provider()
        self.vector_store_provider = vector_store_provider or get_vector_store_provider()
        
        # Initialize vector store with the provider
        self.vector_store = VectorStore(vector_store_provider=self.vector_store_provider)
        
        logger.info("RAG service initialized successfully", extra={
            'extra_fields': {
                'event_type': 'rag_service_initialization_complete',
                'embedding_provider_class': type(self.embedding_provider).__name__,
                'llm_provider_class': type(self.llm_provider).__name__,
                'vector_store_provider_class': type(self.vector_store_provider).__name__
            }
        })
    
    async def add_document(self, file_path: str) -> Dict[str, Any]:
        """Add a document to the knowledge base with enhanced logging"""
        correlation_id = get_correlation_id()
        
        logger.info("Starting document processing", extra={
            'extra_fields': {
                'event_type': 'rag_document_processing_start',
                'file_path': file_path,
                'file_size_bytes': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Load and process document
            logger.debug("Loading and processing document", extra={
                'extra_fields': {
                    'event_type': 'rag_document_loader_start',
                    'file_path': file_path,
                    'correlation_id': correlation_id
                }
            })
            
            documents, ocr_text = self.document_loader.load_document(file_path)
            
            logger.info("Document loaded successfully", extra={
                'extra_fields': {
                    'event_type': 'rag_document_loader_complete',
                    'file_path': file_path,
                    'document_chunks': len(documents),
                    'ocr_text_extracted': bool(ocr_text),
                    'ocr_text_length': len(ocr_text) if ocr_text else 0,
                    'correlation_id': correlation_id
                }
            })
            
            # Add to vector store using plugin architecture
            logger.debug("Adding documents to vector store", extra={
                'extra_fields': {
                    'event_type': 'rag_vector_store_add_start',
                    'document_chunks': len(documents),
                    'correlation_id': correlation_id
                }
            })
            
            success = await self.vector_store.add_documents(documents)
            
            if success:
                logger.info("Document added to knowledge base successfully", extra={
                    'extra_fields': {
                        'event_type': 'rag_document_processing_success',
                        'file_path': file_path,
                        'document_chunks': len(documents),
                        'ocr_text_extracted': bool(ocr_text),
                        'correlation_id': correlation_id
                    }
                })
                
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
                logger.error("Failed to add document to vector store", extra={
                    'extra_fields': {
                        'event_type': 'rag_document_processing_failure',
                        'file_path': file_path,
                        'document_chunks': len(documents),
                        'error': 'Vector store insertion failed',
                        'correlation_id': correlation_id
                    }
                })
                
                return {
                    "success": False,
                    "message": "Failed to add document to vector store"
                }
                
        except Exception as e:
            logger.error("Error processing document", extra={
                'extra_fields': {
                    'event_type': 'rag_document_processing_error',
                    'file_path': file_path,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            return {
                "success": False,
                "message": f"Error processing document: {str(e)}"
            }
    
    async def add_text(self, text: str, source_name: str = "text_input") -> Dict[str, Any]:
        """Add raw text to the knowledge base with enhanced logging"""
        correlation_id = get_correlation_id()
        
        logger.info("Starting text processing", extra={
            'extra_fields': {
                'event_type': 'rag_text_processing_start',
                'source_name': source_name,
                'text_length': len(text),
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Validate text is not empty
            if not text or not text.strip():
                logger.warning("Empty text provided for processing", extra={
                    'extra_fields': {
                        'event_type': 'rag_text_processing_validation_failure',
                        'source_name': source_name,
                        'error': 'Text cannot be empty',
                        'correlation_id': correlation_id
                    }
                })
                
                return {
                    "success": False,
                    "message": "Error processing text: Text cannot be empty"
                }
            
            # Load and process text
            logger.debug("Loading and processing text", extra={
                'extra_fields': {
                    'event_type': 'rag_text_loader_start',
                    'source_name': source_name,
                    'text_length': len(text),
                    'correlation_id': correlation_id
                }
            })
            
            documents = self.document_loader.load_text(text, source_name)
            
            logger.info("Text loaded successfully", extra={
                'extra_fields': {
                    'event_type': 'rag_text_loader_complete',
                    'source_name': source_name,
                    'document_chunks': len(documents),
                    'correlation_id': correlation_id
                }
            })
            
            # Add to vector store using plugin architecture
            logger.debug("Adding text documents to vector store", extra={
                'extra_fields': {
                    'event_type': 'rag_vector_store_add_start',
                    'source_name': source_name,
                    'document_chunks': len(documents),
                    'correlation_id': correlation_id
                }
            })
            
            success = await self.vector_store.add_documents(documents)
            
            if success:
                logger.info("Text added to knowledge base successfully", extra={
                    'extra_fields': {
                        'event_type': 'rag_text_processing_success',
                        'source_name': source_name,
                        'document_chunks': len(documents),
                        'correlation_id': correlation_id
                    }
                })
                
                return {
                    "success": True,
                    "message": f"Text from '{source_name}' added successfully",
                    "chunks_processed": len(documents)
                }
            else:
                logger.error("Failed to add text to vector store", extra={
                    'extra_fields': {
                        'event_type': 'rag_text_processing_failure',
                        'source_name': source_name,
                        'document_chunks': len(documents),
                        'error': 'Vector store insertion failed',
                        'correlation_id': correlation_id
                    }
                })
                
                return {
                    "success": False,
                    "message": "Failed to add text to vector store"
                }
                
        except Exception as e:
            logger.error("Error processing text", extra={
                'extra_fields': {
                    'event_type': 'rag_text_processing_error',
                    'source_name': source_name,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            return {
                "success": False,
                "message": f"Error processing text: {str(e)}"
            }
    
    async def ask_question(self, question: str, top_k: int = None) -> Dict[str, Any]:
        """Ask a question and get an answer using RAG with plugin architecture and enhanced logging"""
        correlation_id = get_correlation_id()
        
        # Use default top_k from config if not provided
        if top_k is None:
            top_k = Config.DEFAULT_TOP_K
        
        # Ensure top_k is valid
        if top_k <= 0:
            logger.warning("Invalid top_k value received, using default", extra={
                'extra_fields': {
                    'event_type': 'rag_invalid_top_k_fallback',
                    'received_top_k': top_k,
                    'fallback_top_k': Config.DEFAULT_TOP_K,
                    'correlation_id': correlation_id
                }
            })
            top_k = Config.DEFAULT_TOP_K
        
        logger.info("Starting question processing", extra={
            'extra_fields': {
                'event_type': 'rag_question_processing_start',
                'question_length': len(question),
                'top_k': top_k,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Get embeddings for the question
            logger.debug("Generating question embeddings", extra={
                'extra_fields': {
                    'event_type': 'rag_question_embedding_start',
                    'question_length': len(question),
                    'correlation_id': correlation_id
                }
            })
            
            question_embeddings = await self.embedding_provider.get_embeddings([question])
            question_vector = question_embeddings[0]
            
            logger.info("Question embeddings generated successfully", extra={
                'extra_fields': {
                    'event_type': 'rag_question_embedding_complete',
                    'question_length': len(question),
                    'embedding_dimensions': len(question_vector),
                    'correlation_id': correlation_id
                }
            })
            
            # Search for similar documents
            logger.debug("Searching for similar documents", extra={
                'extra_fields': {
                    'event_type': 'rag_vector_search_start',
                    'top_k': top_k,
                    'correlation_id': correlation_id
                }
            })
            
            search_results = await self.vector_store_provider.search_vectors(
                question_vector, top_k, Config.QDRANT_COLLECTION_NAME
            )
            
            logger.info("Vector search completed successfully", extra={
                'extra_fields': {
                    'event_type': 'rag_vector_search_complete',
                    'top_k': top_k,
                    'results_found': len(search_results),
                    'correlation_id': correlation_id
                }
            })
            
            if not search_results:
                logger.warning("No relevant documents found for question", extra={
                    'extra_fields': {
                        'event_type': 'rag_question_no_results',
                        'question_length': len(question),
                        'top_k': top_k,
                        'correlation_id': correlation_id
                    }
                })
                
                return {
                    "success": False,
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "question": question
                }
            
            # Extract context from search results
            context_parts = []
            sources = []
            
            for result in search_results:
                content = result["payload"].get("content", "")
                metadata = result["payload"].get("metadata", {})
                source = metadata.get("source", "Unknown")
                
                context_parts.append(content)
                sources.append({
                    "content": content[:200] + "..." if len(content) > 200 else content,
                    "source": source,
                    "score": result["score"]
                })
            
            context = "\n\n".join(context_parts)
            
            logger.debug("Context extracted from search results", extra={
                'extra_fields': {
                    'event_type': 'rag_context_extraction_complete',
                    'context_length': len(context),
                    'sources_count': len(sources),
                    'correlation_id': correlation_id
                }
            })
            
            # Generate answer using LLM
            logger.debug("Generating answer using LLM", extra={
                'extra_fields': {
                    'event_type': 'rag_llm_generation_start',
                    'question_length': len(question),
                    'context_length': len(context),
                    'correlation_id': correlation_id
                }
            })
            
            messages = [
                {
                    "role": "system",
                    "content": f"You are a helpful assistant. Use the following context to answer the user's question. If the context doesn't contain relevant information, say so.\n\nContext:\n{context}"
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
            
            answer = await self.llm_provider.call_llm(messages)
            
            logger.info("Answer generated successfully", extra={
                'extra_fields': {
                    'event_type': 'rag_question_processing_success',
                    'question_length': len(question),
                    'answer_length': len(answer),
                    'sources_count': len(sources),
                    'correlation_id': correlation_id
                }
            })
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "question": question
            }
            
        except Exception as e:
            logger.error("Error processing question", extra={
                'extra_fields': {
                    'event_type': 'rag_question_processing_error',
                    'question_length': len(question),
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            return {
                "success": False,
                "answer": f"Error processing question: {str(e)}",
                "sources": [],
                "question": question
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics with enhanced logging"""
        correlation_id = get_correlation_id()
        
        logger.debug("Getting collection statistics", extra={
            'extra_fields': {
                'event_type': 'rag_stats_request_start',
                'correlation_id': correlation_id
            }
        })
        
        try:
            stats = self.vector_store_provider.get_collection_stats(Config.QDRANT_COLLECTION_NAME)
            
            logger.info("Collection statistics retrieved successfully", extra={
                'extra_fields': {
                    'event_type': 'rag_stats_request_success',
                    'total_documents': stats.get('total_documents', 0),
                    'collection_name': stats.get('collection_name', ''),
                    'vector_size': stats.get('vector_size', 0),
                    'correlation_id': correlation_id
                }
            })
            
            return {
                "success": True,
                "vector_store": {
                    "total_documents": stats.get('total_documents', 0),
                    "collection_name": stats.get('collection_name', ''),
                    "vector_size": stats.get('vector_size', 0)
                },
                "supported_formats": ["pdf", "docx", "txt", "png", "jpg", "jpeg"],
                "chunk_size": Config.CHUNK_SIZE,
                "chunk_overlap": Config.CHUNK_OVERLAP
            }
            
        except Exception as e:
            logger.error("Error getting collection statistics", extra={
                'extra_fields': {
                    'event_type': 'rag_stats_request_error',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            return {
                "success": False,
                "message": f"Error getting statistics: {str(e)}"
            }
    
    def clear_knowledge_base(self) -> Dict[str, Any]:
        """Clear all documents from the knowledge base with enhanced logging"""
        correlation_id = get_correlation_id()
        
        logger.warning("Clearing knowledge base", extra={
            'extra_fields': {
                'event_type': 'rag_knowledge_base_clear_start',
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Get stats before clearing
            stats = self.vector_store_provider.get_collection_stats(Config.QDRANT_COLLECTION_NAME)
            total_documents = stats.get('total_documents', 0)
            
            # Clear all points from the collection
            success = self.vector_store_provider.delete_all_points(Config.QDRANT_COLLECTION_NAME)
            
            if success:
                logger.warning("Knowledge base cleared successfully", extra={
                    'extra_fields': {
                        'event_type': 'rag_knowledge_base_clear_success',
                        'documents_cleared': total_documents,
                        'correlation_id': correlation_id
                    }
                })
                
                return {
                    "success": True,
                    "message": f"Knowledge base cleared successfully. {total_documents} documents removed.",
                    "documents_cleared": total_documents
                }
            else:
                logger.error("Failed to clear knowledge base", extra={
                    'extra_fields': {
                        'event_type': 'rag_knowledge_base_clear_failure',
                        'error': 'Vector store clear operation failed',
                        'correlation_id': correlation_id
                    }
                })
                
                return {
                    "success": False,
                    "message": "Failed to clear knowledge base"
                }
                
        except Exception as e:
            logger.error("Error clearing knowledge base", extra={
                'extra_fields': {
                    'event_type': 'rag_knowledge_base_clear_error',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            return {
                "success": False,
                "message": f"Error clearing knowledge base: {str(e)}"
            } 