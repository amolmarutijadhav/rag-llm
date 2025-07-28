from typing import List, Dict, Any, Optional
from app.domain.services.rag_service import RAGService
from app.domain.services.conversation.analyzer import ConversationAnalyzer
from app.domain.models.conversation import ConversationContext, ConversationAnalysisResult, EnhancedQuery
from app.domain.models.requests import ChatMessage
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider, VectorStoreProvider
from app.core.config import Config
from app.core.logging_config import get_logger, get_correlation_id
import asyncio

logger = get_logger(__name__)

class ConversationAwareRAGService:
    """
    Conversation-aware RAG service using decorator pattern.
    Enhances the existing RAG service with conversation analysis capabilities.
    """
    
    def __init__(self, 
                 rag_service: Optional[RAGService] = None,
                 conversation_analyzer: Optional[ConversationAnalyzer] = None,
                 embedding_provider: Optional[EmbeddingProvider] = None,
                 llm_provider: Optional[LLMProvider] = None,
                 vector_store_provider: Optional[VectorStoreProvider] = None):
        """
        Initialize conversation-aware RAG service.
        
        Args:
            rag_service: Existing RAG service to enhance (optional)
            conversation_analyzer: Conversation analyzer instance (optional)
            embedding_provider: Embedding provider for fallback (optional)
            llm_provider: LLM provider for fallback (optional)
            vector_store_provider: Vector store provider for fallback (optional)
        """
        logger.info("Initializing conversation-aware RAG service", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_rag_initialization_start',
                'rag_service_provided': rag_service is not None,
                'conversation_analyzer_provided': conversation_analyzer is not None
            }
        })
        
        # Use provided RAG service or create new one
        self.rag_service = rag_service or RAGService(
            embedding_provider=embedding_provider,
            llm_provider=llm_provider,
            vector_store_provider=vector_store_provider
        )
        
        # Use provided conversation analyzer or create new one
        self.conversation_analyzer = conversation_analyzer or ConversationAnalyzer()
        
        logger.info("Conversation-aware RAG service initialized successfully", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_rag_initialization_complete',
                'rag_service_class': type(self.rag_service).__name__,
                'conversation_analyzer_class': type(self.conversation_analyzer).__name__
            }
        })
    
    async def ask_question_with_conversation(self, 
                                           messages: List[ChatMessage], 
                                           current_question: str, 
                                           top_k: int = None,
                                           analysis_strategy: Optional[str] = None) -> Dict[str, Any]:
        """
        Ask a question with conversation context awareness.
        
        Args:
            messages: List of chat messages for context
            current_question: The current user question
            top_k: Number of top results to return
            analysis_strategy: Strategy to use for conversation analysis (optional)
            
        Returns:
            Enhanced RAG response with conversation context information
        """
        correlation_id = get_correlation_id()
        
        logger.info("Starting conversation-aware question processing", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_rag_question_start',
                'messages_count': len(messages),
                'current_question_length': len(current_question),
                'top_k': top_k,
                'analysis_strategy': analysis_strategy,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Step 1: Analyze conversation context
            logger.debug("Analyzing conversation context", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_analysis_start',
                    'correlation_id': correlation_id
                }
            })
            
            analysis_result = await self.conversation_analyzer.analyze_conversation(
                messages, strategy_name=analysis_strategy
            )
            
            # Step 2: Generate enhanced queries
            logger.debug("Generating enhanced queries", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_query_generation_start',
                    'correlation_id': correlation_id
                }
            })
            
            enhanced_query = await self.conversation_analyzer.generate_enhanced_queries(
                current_question, analysis_result.context
            )
            
            # Step 3: Perform multi-query retrieval
            logger.debug("Performing multi-query retrieval", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_retrieval_start',
                    'queries_count': len(enhanced_query.enhanced_queries),
                    'correlation_id': correlation_id
                }
            })
            
            all_results = await self._perform_multi_query_retrieval(
                enhanced_query.enhanced_queries, top_k or Config.DEFAULT_TOP_K
            )
            
            # Step 4: Merge and deduplicate results
            logger.debug("Merging and deduplicating results", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_merge_start',
                    'total_results': len(all_results),
                    'correlation_id': correlation_id
                }
            })
            
            merged_results = self._merge_and_deduplicate_results(all_results)
            
            # Step 5: Generate answer using original RAG service logic
            logger.debug("Generating answer", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_answer_generation_start',
                    'merged_results_count': len(merged_results),
                    'correlation_id': correlation_id
                }
            })
            
            answer_result = await self._generate_answer_with_context(
                current_question, merged_results, analysis_result.context
            )
            
            # Step 6: Enhance response with conversation context
            enhanced_response = self._enhance_response_with_context(
                answer_result, analysis_result, enhanced_query
            )
            
            logger.info("Conversation-aware question processing completed", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_question_complete',
                    'success': enhanced_response.get('success', False),
                    'answer_length': len(enhanced_response.get('answer', '')),
                    'sources_count': len(enhanced_response.get('sources', [])),
                    'conversation_context_used': True,
                    'correlation_id': correlation_id
                }
            })
            
            return enhanced_response
            
        except Exception as e:
            logger.error("Error in conversation-aware question processing", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_question_error',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            # Fallback to original RAG service
            logger.warning("Falling back to original RAG service", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_fallback',
                    'correlation_id': correlation_id
                }
            })
            
            fallback_result = await self.rag_service.ask_question(current_question, top_k)
            fallback_result['conversation_context_used'] = False
            fallback_result['fallback_reason'] = str(e)
            
            return fallback_result
    
    async def _perform_multi_query_retrieval(self, queries: List[str], top_k: int) -> List[List[Dict[str, Any]]]:
        """Perform retrieval for multiple queries"""
        correlation_id = get_correlation_id()
        
        logger.debug("Starting multi-query retrieval", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_rag_multi_query_start',
                'queries_count': len(queries),
                'top_k': top_k,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Calculate top_k per query to maintain total results limit
            top_k_per_query = max(1, top_k // len(queries))
            
            # Perform retrieval for each query
            tasks = []
            for query in queries:
                task = self._retrieve_for_single_query(query, top_k_per_query)
                tasks.append(task)
            
            # Execute all retrievals concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and flatten results
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.warning(f"Query {i} failed: {result}", extra={
                        'extra_fields': {
                            'event_type': 'conversation_aware_rag_query_failed',
                            'query_index': i,
                            'query': queries[i],
                            'error': str(result),
                            'correlation_id': correlation_id
                        }
                    })
                else:
                    valid_results.append(result)
            
            logger.info("Multi-query retrieval completed", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_multi_query_complete',
                    'queries_processed': len(queries),
                    'successful_queries': len(valid_results),
                    'total_results': sum(len(r) for r in valid_results),
                    'correlation_id': correlation_id
                }
            })
            
            return valid_results
            
        except Exception as e:
            logger.error("Error in multi-query retrieval", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_multi_query_error',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            return []
    
    async def _retrieve_for_single_query(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Retrieve results for a single query"""
        try:
            # Get embeddings for the query
            query_embeddings = await self.rag_service.embedding_provider.get_embeddings([query])
            query_vector = query_embeddings[0]
            
            # Search for similar documents
            search_results = await self.rag_service.vector_store_provider.search_vectors(
                query_vector, top_k, Config.QDRANT_COLLECTION_NAME
            )
            
            return search_results
            
        except Exception as e:
            logger.warning(f"Single query retrieval failed for query: {query[:50]}...", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_single_query_failed',
                    'query_length': len(query),
                    'error': str(e)
                }
            })
            return []
    
    def _merge_and_deduplicate_results(self, all_results: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Merge and deduplicate results from multiple queries"""
        correlation_id = get_correlation_id()
        
        logger.debug("Merging and deduplicating results", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_rag_merge_start',
                'result_sets_count': len(all_results),
                'total_results': sum(len(r) for r in all_results),
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Flatten all results
            all_flat_results = []
            for result_set in all_results:
                all_flat_results.extend(result_set)
            
            # Deduplicate based on content hash
            seen_contents = set()
            unique_results = []
            
            for result in all_flat_results:
                content = result.get("payload", {}).get("content", "")
                content_hash = hash(content)
                
                if content_hash not in seen_contents:
                    seen_contents.add(content_hash)
                    unique_results.append(result)
            
            # Sort by score and limit
            unique_results.sort(key=lambda x: x.get("score", 0), reverse=True)
            final_results = unique_results[:Config.DEFAULT_TOP_K]
            
            logger.info("Results merged and deduplicated successfully", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_merge_complete',
                    'original_results': len(all_flat_results),
                    'unique_results': len(unique_results),
                    'final_results': len(final_results),
                    'correlation_id': correlation_id
                }
            })
            
            return final_results
            
        except Exception as e:
            logger.error("Error merging and deduplicating results", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_merge_error',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            return []
    
    async def _generate_answer_with_context(self, 
                                          question: str, 
                                          results: List[Dict[str, Any]], 
                                          context: ConversationContext) -> Dict[str, Any]:
        """Generate answer using LLM with context"""
        correlation_id = get_correlation_id()
        
        try:
            if not results:
                return {
                    "success": False,
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "question": question
                }
            
            # Extract context from search results
            context_parts = []
            sources = []
            
            for result in results:
                content = result["payload"].get("content", "")
                metadata = result["payload"].get("metadata", {})
                source = metadata.get("source", "Unknown")
                
                context_parts.append(content)
                sources.append({
                    "content": content[:200] + "..." if len(content) > 200 else content,
                    "source": source,
                    "score": result["score"]
                })
            
            context_text = "\n\n".join(context_parts)
            
            # Generate answer using LLM
            messages = [
                {
                    "role": "system",
                    "content": f"You are a helpful assistant. Use the following context to answer the user's question. Consider the conversation context provided.\n\nContext:\n{context_text}"
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
            
            answer = await self.rag_service.llm_provider.call_llm(messages)
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "question": question
            }
            
        except Exception as e:
            logger.error("Error generating answer with context", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_rag_answer_generation_error',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            return {
                "success": False,
                "answer": f"Error generating answer: {str(e)}",
                "sources": [],
                "question": question
            }
    
    def _enhance_response_with_context(self, 
                                     base_response: Dict[str, Any], 
                                     analysis_result: ConversationAnalysisResult,
                                     enhanced_query: EnhancedQuery) -> Dict[str, Any]:
        """Enhance response with conversation context information"""
        enhanced_response = base_response.copy()
        
        # Add conversation context information
        enhanced_response['conversation_context_used'] = True
        enhanced_response['conversation_analysis'] = {
            'strategy_used': analysis_result.analysis_method,
            'confidence_score': analysis_result.confidence_score,
            'processing_time_ms': analysis_result.processing_time_ms,
            'topics_found': len(analysis_result.context.topics),
            'entities_found': len(analysis_result.context.entities),
            'context_clues_found': len(analysis_result.context.context_clues)
        }
        
        # Add enhanced query information
        enhanced_response['enhanced_queries'] = {
            'original_query': enhanced_query.original_query,
            'enhanced_queries_count': len(enhanced_query.enhanced_queries),
            'query_generation_method': enhanced_query.query_generation_method
        }
        
        # Add conversation context summary
        enhanced_response['conversation_context'] = {
            'topics': analysis_result.context.topics,
            'entities': analysis_result.context.entities,
            'context_clues': analysis_result.context.context_clues,
            'conversation_length': analysis_result.context.conversation_length
        }
        
        return enhanced_response
    
    # Delegate other methods to the original RAG service
    async def add_document(self, file_path: str) -> Dict[str, Any]:
        """Add a document to the knowledge base"""
        return await self.rag_service.add_document(file_path)
    
    async def add_text(self, text: str, source_name: str = "text_input") -> Dict[str, Any]:
        """Add raw text to the knowledge base"""
        return await self.rag_service.add_text(text, source_name)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        stats = self.rag_service.get_stats()
        stats['conversation_aware'] = True
        stats['available_analysis_strategies'] = self.conversation_analyzer.get_available_strategies()
        return stats
    
    def clear_knowledge_base(self) -> Dict[str, Any]:
        """Clear all documents from the knowledge base"""
        return self.rag_service.clear_knowledge_base() 