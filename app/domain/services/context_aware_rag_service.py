"""
Context-Aware RAG Service
Implements advanced response modes, hierarchical document filtering, and progressive validation.
"""

from typing import List, Dict, Any, Optional
from app.domain.services.rag_service import RAGService
from app.domain.services.system_message_parser import SystemMessageParser
from app.domain.models.requests import (
    DocumentContext, DocumentUploadRequest, TextUploadRequest, 
    ContextAwareQuestionRequest, SystemMessageDirective, ResponseMode
)
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider, VectorStoreProvider
from app.core.config import Config
from app.core.logging_config import get_logger, get_correlation_id
from app.core.logging_helpers import log_extra

logger = get_logger(__name__)

class ContextFilter:
    """Handles hierarchical document context filtering"""
    
    @staticmethod
    def filter_documents_by_context(
        documents: List[Dict[str, Any]], 
        directive: SystemMessageDirective
    ) -> List[Dict[str, Any]]:
        """
        Filter documents using hierarchical matching strategy.
        Primary filters must match, secondary filters affect ranking.
        """
        correlation_id = get_correlation_id()
        
        logger.debug(
            "Starting document context filtering",
            extra=log_extra(
                'context_filtering_start',
                total_documents=len(documents),
                directive_context=directive.document_context,
                directive_domains=directive.content_domains,
                directive_categories=directive.document_categories,
            )
        )
        
        if not documents:
            return []
        
        # If no context filters specified, return all documents
        if not any([directive.document_context, directive.content_domains, directive.document_categories]):
            logger.debug(
                "No context filters specified, returning all documents",
                extra=log_extra('context_filtering_no_filters', documents_returned=len(documents))
            )
            return documents
        
        filtered_documents = []
        
        for doc in documents:
            metadata = doc.get("metadata", {})
            doc_context = metadata.get("document_context", {})
            
            # Calculate primary match score (context_type and content_domain)
            primary_score = ContextFilter._calculate_primary_score(doc_context, directive)
            
            # Calculate secondary match score (document_category and relevance_tags)
            secondary_score = ContextFilter._calculate_secondary_score(doc_context, directive)
            
            # Document must have at least one primary match
            if primary_score > 0:
                # Add combined score to document for ranking
                doc["context_match_score"] = primary_score + (secondary_score * 0.5)
                filtered_documents.append(doc)
        
        # Sort by context match score (highest first)
        filtered_documents.sort(key=lambda x: x.get("context_match_score", 0), reverse=True)
        
        logger.info(
            "Document context filtering completed",
            extra=log_extra('context_filtering_complete', original_documents=len(documents), filtered_documents=len(filtered_documents))
        )
        
        return filtered_documents
    
    @staticmethod
    def _calculate_primary_score(doc_context: Dict[str, Any], directive: SystemMessageDirective) -> float:
        """Calculate primary match score (context_type and content_domain)"""
        score = 0.0
        
        # Check context_type match
        if directive.document_context and doc_context.get("context_type"):
            doc_context_types = set(doc_context["context_type"])
            directive_context_types = set(directive.document_context)
            if doc_context_types.intersection(directive_context_types):
                score += 1.0
        
        # Check content_domain match
        if directive.content_domains and doc_context.get("content_domain"):
            doc_domains = set(doc_context["content_domain"])
            directive_domains = set(directive.content_domains)
            if doc_domains.intersection(directive_domains):
                score += 1.0
        
        return score
    
    @staticmethod
    def _calculate_secondary_score(doc_context: Dict[str, Any], directive: SystemMessageDirective) -> float:
        """Calculate secondary match score (document_category and relevance_tags)"""
        score = 0.0
        
        # Check document_category match
        if directive.document_categories and doc_context.get("document_category"):
            doc_categories = set(doc_context["document_category"])
            directive_categories = set(directive.document_categories)
            if doc_categories.intersection(directive_categories):
                score += 1.0
        
        # Relevance tags boost only if they overlap document categories/domains when provided
        if doc_context.get("relevance_tags"):
            doc_tags = set(doc_context["relevance_tags"])
            boost = 0.0
            if directive.document_categories:
                if doc_tags.intersection(set(directive.document_categories)):
                    boost += 0.25
            if directive.content_domains:
                if doc_tags.intersection(set(directive.content_domains)):
                    boost += 0.25
            score += boost
        
        return score

class ResponseModeHandler:
    """Handles different response modes for context-aware RAG"""
    
    def __init__(self, rag_service: RAGService, llm_provider: LLMProvider):
        self.rag_service = rag_service
        self.llm_provider = llm_provider
    
    async def handle_response_mode(
        self,
        question: str,
        system_message: str,
        directive: SystemMessageDirective,
        top_k: int = None
    ) -> Dict[str, Any]:
        """Handle different response modes"""
        correlation_id = get_correlation_id()
        
        logger.info("Handling response mode", extra={
            'extra_fields': {
                'event_type': 'response_mode_handling_start',
                'response_mode': directive.response_mode,
                'question_length': len(question),
                'correlation_id': correlation_id
            }
        })
        
        if directive.response_mode == ResponseMode.RAG_ONLY:
            return await self._handle_rag_only(question, directive, top_k)
        elif directive.response_mode == ResponseMode.LLM_ONLY:
            return await self._handle_llm_only(question, system_message)
        elif directive.response_mode == ResponseMode.HYBRID:
            return await self._handle_hybrid(question, system_message, directive, top_k)
        elif directive.response_mode == ResponseMode.SMART_FALLBACK:
            return await self._handle_smart_fallback(question, system_message, directive, top_k)
        elif directive.response_mode == ResponseMode.RAG_PRIORITY:
            return await self._handle_rag_priority(question, system_message, directive, top_k)
        elif directive.response_mode == ResponseMode.LLM_PRIORITY:
            return await self._handle_llm_priority(question, system_message, directive, top_k)
        else:
            # Default to hybrid
            return await self._handle_hybrid(question, system_message, directive, top_k)
    
    async def _handle_rag_only(self, question: str, directive: SystemMessageDirective, top_k: int) -> Dict[str, Any]:
        """Handle RAG_ONLY mode - only use uploaded documents"""
        correlation_id = get_correlation_id()
        
        logger.info("Handling RAG_ONLY response mode", extra={
            'extra_fields': {
                'event_type': 'response_mode_rag_only',
                'correlation_id': correlation_id
            }
        })
        
        # Use existing RAG service
        rag_result = await self.rag_service.ask_question(question, top_k)
        
        if not rag_result.get('success', False):
            # No RAG results found
            if directive.fallback_strategy == "refuse":
                logger.info("RAG_ONLY: Refusing to answer - no RAG results and refuse strategy", extra={
                    'extra_fields': {
                        'event_type': 'rag_only_refuse_no_results',
                        'fallback_strategy': directive.fallback_strategy,
                        'correlation_id': correlation_id
                    }
                })
                
                return {
                    "success": False,
                    "answer": "I cannot answer this question as I don't have relevant information in my knowledge base.",
                    "sources": [],
                    "question": question,
                    "response_mode": "RAG_ONLY",
                    "context_used": "rag_refused",
                    "decision_reason": "no_rag_results_and_refuse_strategy",
                    "rag_sources_count": 0,
                    "rag_confidence": 0.0,
                    "llm_fallback_used": False,
                    "fallback_reason": "no_rag_results_and_refuse_strategy",
                    "decision_transparency": {
                        "rag_attempted": True,
                        "rag_successful": False,
                        "rag_documents_found": 0,
                        "llm_fallback_triggered": False,
                        "fallback_strategy": "refuse",
                        "final_decision": "refuse_to_answer"
                    }
                }
            else:
                # Fallback to LLM even in RAG_ONLY mode if configured
                logger.info("RAG_ONLY: Falling back to LLM despite RAG_ONLY mode", extra={
                    'extra_fields': {
                        'event_type': 'rag_only_llm_fallback',
                        'fallback_strategy': directive.fallback_strategy,
                        'correlation_id': correlation_id
                    }
                })
                
                llm_result = await self._generate_llm_response(question, "You are a helpful assistant.")
                
                return {
                    **llm_result,
                    "response_mode": "RAG_ONLY",
                    "context_used": "llm_fallback",
                    "decision_reason": "rag_no_results_but_llm_fallback_allowed",
                    "rag_sources_count": 0,
                    "rag_confidence": 0.0,
                    "llm_fallback_used": True,
                    "fallback_reason": f"no_rag_results_and_{directive.fallback_strategy}_strategy",
                    "decision_transparency": {
                        "rag_attempted": True,
                        "rag_successful": False,
                        "rag_documents_found": 0,
                        "llm_fallback_triggered": True,
                        "fallback_strategy": directive.fallback_strategy,
                        "final_decision": "use_llm_fallback"
                    }
                }
        
        # RAG was successful
        sources = rag_result.get('sources', [])
        avg_confidence = sum(source.get('score', 0) for source in sources) / len(sources) if sources else 0.0
        
        logger.info("RAG_ONLY: Using RAG results successfully", extra={
            'extra_fields': {
                'event_type': 'rag_only_rag_success',
                'sources_count': len(sources),
                'avg_confidence': avg_confidence,
                'correlation_id': correlation_id
            }
        })
        
        return {
            **rag_result,
            "response_mode": "RAG_ONLY",
            "context_used": "rag_successful",
            "decision_reason": "rag_found_relevant_documents",
            "rag_sources_count": len(sources),
            "rag_confidence": avg_confidence,
            "llm_fallback_used": False,
            "decision_transparency": {
                "rag_attempted": True,
                "rag_successful": True,
                "rag_documents_found": len(sources),
                "llm_fallback_triggered": False,
                "fallback_strategy": directive.fallback_strategy,
                "final_decision": "use_rag_results"
            }
        }
    
    async def _handle_llm_only(self, question: str, system_message: str) -> Dict[str, Any]:
        """Handle LLM_ONLY mode - only use LLM knowledge"""
        correlation_id = get_correlation_id()
        
        logger.info("Handling LLM_ONLY response mode", extra={
            'extra_fields': {
                'event_type': 'response_mode_llm_only',
                'correlation_id': correlation_id
            }
        })
        
        llm_result = await self._generate_llm_response(question, system_message)
        
        logger.info("LLM_ONLY: Using LLM knowledge only", extra={
            'extra_fields': {
                'event_type': 'llm_only_success',
                'correlation_id': correlation_id
            }
        })
        
        return {
            **llm_result,
            "response_mode": "LLM_ONLY",
            "context_used": "llm_knowledge_only",
            "decision_reason": "llm_only_mode_requested",
            "rag_sources_count": 0,
            "rag_confidence": 0.0,
            "llm_fallback_used": False,
            "decision_transparency": {
                "rag_attempted": False,
                "rag_successful": False,
                "rag_documents_found": 0,
                "llm_fallback_triggered": False,
                "final_decision": "use_llm_only"
            }
        }
    
    async def _handle_hybrid(self, question: str, system_message: str, directive: SystemMessageDirective, top_k: int) -> Dict[str, Any]:
        """Handle HYBRID mode - try RAG first, fallback to LLM"""
        correlation_id = get_correlation_id()
        
        logger.info("Handling HYBRID response mode", extra={
            'extra_fields': {
                'event_type': 'response_mode_hybrid',
                'correlation_id': correlation_id
            }
        })
        
        # Try RAG first
        rag_result = await self.rag_service.ask_question(question, top_k)
        
        if rag_result.get('success', False):
            # RAG found results, use them
            sources = rag_result.get('sources', [])
            avg_confidence = sum(source.get('score', 0) for source in sources) / len(sources) if sources else 0.0
            
            logger.info("HYBRID: Using RAG results", extra={
                'extra_fields': {
                    'event_type': 'hybrid_rag_success',
                    'sources_count': len(sources),
                    'avg_confidence': avg_confidence,
                    'correlation_id': correlation_id
                }
            })
            
            return {
                **rag_result,
                "response_mode": "HYBRID",
                "context_used": "rag_enhanced_with_llm",
                "decision_reason": "rag_found_relevant_documents",
                "rag_sources_count": len(sources),
                "rag_confidence": avg_confidence,
                "llm_fallback_used": False,
                "decision_transparency": {
                    "rag_attempted": True,
                    "rag_successful": True,
                    "rag_documents_found": len(sources),
                    "llm_fallback_triggered": False,
                    "final_decision": "use_rag_results"
                }
            }
        else:
            # No RAG results, fallback to LLM
            logger.info("HYBRID: Falling back to LLM - no RAG results", extra={
                'extra_fields': {
                    'event_type': 'hybrid_llm_fallback',
                    'rag_success': False,
                    'correlation_id': correlation_id
                }
            })
            
            llm_result = await self._generate_llm_response(question, system_message)
            
            return {
                **llm_result,
                "response_mode": "HYBRID",
                "context_used": "llm_fallback",
                "decision_reason": "rag_no_relevant_documents_found",
                "rag_sources_count": 0,
                "rag_confidence": 0.0,
                "llm_fallback_used": True,
                "fallback_reason": "no_rag_results_available",
                "decision_transparency": {
                    "rag_attempted": True,
                    "rag_successful": False,
                    "rag_documents_found": 0,
                    "llm_fallback_triggered": True,
                    "final_decision": "use_llm_fallback"
                }
            }
    
    async def _handle_smart_fallback(self, question: str, system_message: str, directive: SystemMessageDirective, top_k: int) -> Dict[str, Any]:
        """Handle SMART_FALLBACK mode - use confidence scoring"""
        correlation_id = get_correlation_id()
        
        logger.info("Handling SMART_FALLBACK response mode", extra={
            'extra_fields': {
                'event_type': 'response_mode_smart_fallback',
                'min_confidence': directive.min_confidence,
                'correlation_id': correlation_id
            }
        })
        
        # Try RAG first
        rag_result = await self.rag_service.ask_question(question, top_k)
        
        if rag_result.get('success', False):
            # Calculate confidence based on sources and scores
            sources = rag_result.get('sources', [])
            if sources:
                avg_score = sum(source.get('score', 0) for source in sources) / len(sources)
                confidence = min(avg_score, 1.0)  # Normalize to 0-1
                
                logger.info("SMART_FALLBACK: RAG results found, calculating confidence", extra={
                    'extra_fields': {
                        'event_type': 'smart_fallback_confidence_calculation',
                        'sources_count': len(sources),
                        'avg_score': avg_score,
                        'normalized_confidence': confidence,
                        'min_confidence_threshold': directive.min_confidence,
                        'correlation_id': correlation_id
                    }
                })
                
                if confidence >= directive.min_confidence:
                    # High confidence RAG result
                    logger.info("SMART_FALLBACK: Using high confidence RAG results", extra={
                        'extra_fields': {
                            'event_type': 'smart_fallback_high_confidence_rag',
                            'confidence': confidence,
                            'threshold': directive.min_confidence,
                            'correlation_id': correlation_id
                        }
                    })
                    
                    return {
                        **rag_result,
                        "response_mode": "SMART_FALLBACK",
                        "context_used": "high_confidence_rag",
                        "decision_reason": f"rag_confidence_{confidence:.2f}_above_threshold_{directive.min_confidence}",
                        "rag_sources_count": len(sources),
                        "rag_confidence": confidence,
                        "llm_fallback_used": False,
                        "confidence_score": confidence,
                        "decision_transparency": {
                            "rag_attempted": True,
                            "rag_successful": True,
                            "rag_documents_found": len(sources),
                            "llm_fallback_triggered": False,
                            "confidence_threshold": directive.min_confidence,
                            "actual_confidence": confidence,
                            "confidence_decision": "above_threshold",
                            "final_decision": "use_high_confidence_rag"
                        }
                    }
                else:
                    # Low confidence, combine with LLM
                    logger.info("SMART_FALLBACK: Low confidence RAG, combining with LLM", extra={
                        'extra_fields': {
                            'event_type': 'smart_fallback_low_confidence_hybrid',
                            'confidence': confidence,
                            'threshold': directive.min_confidence,
                            'correlation_id': correlation_id
                        }
                    })
                    
                    return await self._handle_hybrid(question, system_message, directive, top_k)
            else:
                # No sources, fallback to LLM
                logger.info("SMART_FALLBACK: No RAG sources, falling back to LLM", extra={
                    'extra_fields': {
                        'event_type': 'smart_fallback_no_sources_llm',
                        'correlation_id': correlation_id
                    }
                })
                
                llm_result = await self._generate_llm_response(question, system_message)
                
                return {
                    **llm_result,
                    "response_mode": "SMART_FALLBACK",
                    "context_used": "llm_fallback",
                    "decision_reason": "rag_no_sources_available",
                    "rag_sources_count": 0,
                    "rag_confidence": 0.0,
                    "llm_fallback_used": True,
                    "fallback_reason": "no_rag_sources_found",
                    "confidence_score": 0.0,
                    "decision_transparency": {
                        "rag_attempted": True,
                        "rag_successful": False,
                        "rag_documents_found": 0,
                        "llm_fallback_triggered": True,
                        "confidence_threshold": directive.min_confidence,
                        "actual_confidence": 0.0,
                        "confidence_decision": "no_sources",
                        "final_decision": "use_llm_fallback"
                    }
                }
        else:
            # No RAG results, use LLM
            logger.info("SMART_FALLBACK: No RAG results, using LLM", extra={
                'extra_fields': {
                    'event_type': 'smart_fallback_no_rag_llm',
                    'correlation_id': correlation_id
                }
            })
            
            llm_result = await self._generate_llm_response(question, system_message)
            
            return {
                **llm_result,
                "response_mode": "SMART_FALLBACK",
                "context_used": "llm_fallback",
                "decision_reason": "rag_no_results_available",
                "rag_sources_count": 0,
                "rag_confidence": 0.0,
                "llm_fallback_used": True,
                "fallback_reason": "no_rag_results_found",
                "confidence_score": 0.0,
                "decision_transparency": {
                    "rag_attempted": True,
                    "rag_successful": False,
                    "rag_documents_found": 0,
                    "llm_fallback_triggered": True,
                    "confidence_threshold": directive.min_confidence,
                    "actual_confidence": 0.0,
                    "confidence_decision": "no_results",
                    "final_decision": "use_llm_fallback"
                }
            }
    
    async def _handle_rag_priority(self, question: str, system_message: str, directive: SystemMessageDirective, top_k: int) -> Dict[str, Any]:
        """Handle RAG_PRIORITY mode - prefer RAG, use LLM for gaps"""
        correlation_id = get_correlation_id()
        
        logger.info("Handling RAG_PRIORITY response mode", extra={
            'extra_fields': {
                'event_type': 'response_mode_rag_priority',
                'correlation_id': correlation_id
            }
        })
        
        # Try RAG first
        rag_result = await self.rag_service.ask_question(question, top_k)
        
        if rag_result.get('success', False):
            # RAG was successful - use RAG result
            sources = rag_result.get('sources', [])
            avg_confidence = sum(source.get('score', 0) for source in sources) / len(sources) if sources else 0.0
            
            logger.info("RAG_PRIORITY: Using RAG results", extra={
                'extra_fields': {
                    'event_type': 'rag_priority_rag_success',
                    'sources_count': len(sources),
                    'avg_confidence': avg_confidence,
                    'correlation_id': correlation_id
                }
            })
            
            return {
                **rag_result,
                "response_mode": "RAG_PRIORITY",
                "context_used": "rag_priority",
                "decision_reason": "rag_found_relevant_documents",
                "rag_sources_count": len(sources),
                "rag_confidence": avg_confidence,
                "llm_fallback_used": False,
                "decision_transparency": {
                    "rag_attempted": True,
                    "rag_successful": True,
                    "rag_documents_found": len(sources),
                    "llm_fallback_triggered": False,
                    "final_decision": "use_rag_results"
                }
            }
        else:
            # No RAG results, use LLM for gaps
            logger.info("RAG_PRIORITY: Falling back to LLM - no RAG results", extra={
                'extra_fields': {
                    'event_type': 'rag_priority_llm_fallback',
                    'rag_success': False,
                    'correlation_id': correlation_id
                }
            })
            
            llm_result = await self._generate_llm_response(question, system_message)
            
            return {
                **llm_result,
                "response_mode": "RAG_PRIORITY",
                "context_used": "llm_fallback",
                "decision_reason": "rag_no_relevant_documents_found",
                "rag_sources_count": 0,
                "rag_confidence": 0.0,
                "llm_fallback_used": True,
                "fallback_reason": "no_rag_results_available",
                "decision_transparency": {
                    "rag_attempted": True,
                    "rag_successful": False,
                    "rag_documents_found": 0,
                    "llm_fallback_triggered": True,
                    "final_decision": "use_llm_fallback"
                }
            }
    
    async def _handle_llm_priority(self, question: str, system_message: str, directive: SystemMessageDirective, top_k: int) -> Dict[str, Any]:
        """Handle LLM_PRIORITY mode - prefer LLM, use RAG for specific topics"""
        correlation_id = get_correlation_id()
        
        logger.info("Handling LLM_PRIORITY response mode", extra={
            'extra_fields': {
                'event_type': 'response_mode_llm_priority',
                'correlation_id': correlation_id
            }
        })
        
        # Try LLM first
        llm_result = await self._generate_llm_response(question, system_message)
        
        # Check if question might benefit from RAG (simple heuristic)
        rag_keywords = ['document', 'file', 'upload', 'specific', 'context', 'reference']
        rag_keywords_found = [keyword for keyword in rag_keywords if keyword in question.lower()]
        
        if rag_keywords_found:
            logger.info("LLM_PRIORITY: RAG keywords detected, attempting RAG supplementation", extra={
                'extra_fields': {
                    'event_type': 'llm_priority_rag_keywords_detected',
                    'rag_keywords_found': rag_keywords_found,
                    'correlation_id': correlation_id
                }
            })
            
            # Try RAG as well
            rag_result = await self.rag_service.ask_question(question, top_k)
            if rag_result.get('success', False):
                # Combine LLM and RAG results
                sources = rag_result.get('sources', [])
                avg_confidence = sum(source.get('score', 0) for source in sources) / len(sources) if sources else 0.0
                
                logger.info("LLM_PRIORITY: RAG supplementation successful", extra={
                    'extra_fields': {
                        'event_type': 'llm_priority_rag_supplementation_success',
                        'sources_count': len(sources),
                        'avg_confidence': avg_confidence,
                        'correlation_id': correlation_id
                    }
                })
                
                return {
                    **llm_result,
                    "response_mode": "LLM_PRIORITY",
                    "context_used": "llm_priority_with_rag_supplement",
                    "decision_reason": f"llm_primary_with_rag_supplementation_keywords_{rag_keywords_found}",
                    "rag_sources_count": len(sources),
                    "rag_confidence": avg_confidence,
                    "llm_fallback_used": False,
                    "rag_supplement": sources,
                    "decision_transparency": {
                        "rag_attempted": True,
                        "rag_successful": True,
                        "rag_documents_found": len(sources),
                        "llm_fallback_triggered": False,
                        "rag_keywords_detected": rag_keywords_found,
                        "final_decision": "use_llm_with_rag_supplement"
                    }
                }
            else:
                logger.info("LLM_PRIORITY: RAG supplementation failed, using LLM only", extra={
                    'extra_fields': {
                        'event_type': 'llm_priority_rag_supplementation_failed',
                        'rag_keywords_found': rag_keywords_found,
                        'correlation_id': correlation_id
                    }
                })
        else:
            logger.info("LLM_PRIORITY: No RAG keywords detected, using LLM only", extra={
                'extra_fields': {
                    'event_type': 'llm_priority_no_rag_keywords',
                    'correlation_id': correlation_id
                }
            })
        
        return {
            **llm_result,
            "response_mode": "LLM_PRIORITY",
            "context_used": "llm_priority",
            "decision_reason": "llm_primary_no_rag_supplementation_needed",
            "rag_sources_count": 0,
            "rag_confidence": 0.0,
            "llm_fallback_used": False,
            "decision_transparency": {
                "rag_attempted": bool(rag_keywords_found),
                "rag_successful": False,
                "rag_documents_found": 0,
                "llm_fallback_triggered": False,
                "rag_keywords_detected": rag_keywords_found,
                "final_decision": "use_llm_only"
            }
        }
    
    async def _generate_llm_response(self, question: str, system_message: str) -> Dict[str, Any]:
        """Generate response using only LLM"""
        correlation_id = get_correlation_id()
        
        logger.debug("Generating LLM-only response", extra={
            'extra_fields': {
                'event_type': 'llm_response_generation',
                'question_length': len(question),
                'correlation_id': correlation_id
            }
        })
        
        messages = [
            {"role": "system", "content": system_message or "You are a helpful assistant."},
            {"role": "user", "content": question}
        ]
        
        answer = await self.llm_provider.call_llm(messages)
        
        logger.debug("LLM-only response generated successfully", extra={
            'extra_fields': {
                'event_type': 'llm_response_generation_success',
                'answer_length': len(answer),
                'correlation_id': correlation_id
            }
        })
        
        return {
            "success": True,
            "answer": answer,
            "sources": [],
            "question": question,
            "response_mode": "LLM_ONLY",
            "context_used": "llm_knowledge_only",
            "decision_reason": "llm_only_response_generated",
            "rag_sources_count": 0,
            "rag_confidence": 0.0,
            "llm_fallback_used": False,
            "decision_transparency": {
                "rag_attempted": False,
                "rag_successful": False,
                "rag_documents_found": 0,
                "llm_fallback_triggered": False,
                "final_decision": "use_llm_only"
            }
        }

class ContextAwareRAGService:
    """Enhanced RAG service with context awareness and user-defined document context"""
    
    def __init__(self,
                 rag_service: Optional[RAGService] = None,
                 embedding_provider: Optional[EmbeddingProvider] = None,
                 llm_provider: Optional[LLMProvider] = None,
                 vector_store_provider: Optional[VectorStoreProvider] = None):
        """Initialize context-aware RAG service"""
        self.rag_service = rag_service or RAGService(
            embedding_provider=embedding_provider,
            llm_provider=llm_provider,
            vector_store_provider=vector_store_provider
        )
        self.llm_provider = llm_provider or self.rag_service.llm_provider
        self.system_parser = SystemMessageParser()
        self.response_handler = ResponseModeHandler(self.rag_service, self.llm_provider)
        
        logger.info("Context-aware RAG service initialized", extra={
            'extra_fields': {
                'event_type': 'context_aware_rag_service_initialization',
                'rag_service_class': type(self.rag_service).__name__
            }
        })
    
    async def add_document_with_context(self, request: DocumentUploadRequest) -> Dict[str, Any]:
        """Add document with mandatory context"""
        correlation_id = get_correlation_id()
        
        logger.info("Adding document with context", extra={
            'extra_fields': {
                'event_type': 'context_aware_document_add_start',
                'file_path': request.file_path,
                'context_type': request.context.context_type,
                'content_domain': request.context.content_domain,
                'document_category': request.context.document_category,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Load document using existing RAG service
            documents, ocr_text = self.rag_service.document_loader.load_document(request.file_path)
            
            # Enhance documents with context
            enhanced_documents = []
            for i, doc in enumerate(documents):
                enhanced_doc = {
                    "id": f"{request.file_path}_{i}",
                    "content": doc["content"],  # Use dictionary access instead of attribute access
                    "metadata": {
                        "source": request.file_path,
                        "chunk_index": i,
                        "total_chunks": len(documents),
                        # Add document context
                        "document_context": {
                            "context_type": request.context.context_type,
                            "content_domain": request.context.content_domain,
                            "document_category": request.context.document_category,
                            "relevance_tags": request.context.relevance_tags,
                            "description": request.context.description
                        }
                    }
                }
                enhanced_documents.append(enhanced_doc)
            
            # Add OCR text if available
            if ocr_text:
                ocr_doc = {
                    "id": f"{request.file_path}_ocr",
                    "content": f"Extracted from images: {ocr_text}",
                    "metadata": {
                        "source": request.file_path,
                        "chunk_index": len(documents),
                        "total_chunks": len(documents) + 1,
                        "is_ocr": True,
                        "document_context": {
                            "context_type": request.context.context_type,
                            "content_domain": request.context.content_domain,
                            "document_category": request.context.document_category,
                            "relevance_tags": request.context.relevance_tags + ["ocr", "image_extraction"],
                            "description": request.context.description
                        }
                    }
                }
                enhanced_documents.append(ocr_doc)
            
            # Add to vector store
            success = await self.rag_service.vector_store.add_documents(enhanced_documents)
            
            if success:
                logger.info("Document with context added successfully", extra={
                    'extra_fields': {
                        'event_type': 'context_aware_document_add_success',
                        'file_path': request.file_path,
                        'documents_added': len(enhanced_documents),
                        'context_type': request.context.context_type,
                        'correlation_id': correlation_id
                    }
                })
                
                return {
                    "success": True,
                    "message": f"Document '{request.file_path}' added with context '{request.context.context_type}'",
                    "documents_added": len(enhanced_documents),
                    "context": {
                        "context_type": request.context.context_type,
                        "content_domain": request.context.content_domain,
                        "document_category": request.context.document_category,
                        "relevance_tags": request.context.relevance_tags
                    }
                }
            else:
                raise Exception("Failed to add documents to vector store")
                
        except Exception as e:
            logger.error("Error adding document with context", extra={
                'extra_fields': {
                    'event_type': 'context_aware_document_add_error',
                    'file_path': request.file_path,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'error_details': {
                        'documents_count': len(enhanced_documents) if 'enhanced_documents' in locals() else 'unknown',
                        'rag_service_type': type(self.rag_service).__name__,
                        'vector_store_type': type(self.rag_service.vector_store).__name__ if hasattr(self.rag_service, 'vector_store') else 'unknown',
                        'embedding_provider_type': type(self.rag_service.vector_store.embedding_provider).__name__ if hasattr(self.rag_service, 'vector_store') and hasattr(self.rag_service.vector_store, 'embedding_provider') else 'unknown',
                        'vector_store_provider_type': type(self.rag_service.vector_store.vector_store_provider).__name__ if hasattr(self.rag_service, 'vector_store') and hasattr(self.rag_service.vector_store, 'vector_store_provider') else 'unknown'
                    },
                    'correlation_id': correlation_id
                }
            })
            
            return {
                "success": False,
                "message": f"Error adding document: {str(e)}",
                "context": {
                    "context_type": request.context.context_type,
                    "content_domain": request.context.content_domain,
                    "document_category": request.context.document_category
                }
            }
    
    async def add_text_with_context(self, request: TextUploadRequest) -> Dict[str, Any]:
        """Add text with mandatory context"""
        correlation_id = get_correlation_id()
        
        logger.info("Adding text with context", extra={
            'extra_fields': {
                'event_type': 'context_aware_text_add_start',
                'text_length': len(request.text),
                'context_type': request.context.context_type,
                'content_domain': request.context.content_domain,
                'document_category': request.context.document_category,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Load text using existing RAG service
            documents = self.rag_service.document_loader.load_text(
                request.text, 
                source_name=request.source_name or "text_input"
            )
            
            # Enhance documents with context
            enhanced_documents = []
            for i, doc in enumerate(documents):
                enhanced_doc = {
                    "id": doc["id"],
                    "content": doc["content"],
                    "metadata": {
                        **doc["metadata"],
                        # Add document context
                        "document_context": {
                            "context_type": request.context.context_type,
                            "content_domain": request.context.content_domain,
                            "document_category": request.context.document_category,
                            "relevance_tags": request.context.relevance_tags,
                            "description": request.context.description
                        }
                    }
                }
                enhanced_documents.append(enhanced_doc)
            
            # Add to vector store
            success = await self.rag_service.vector_store.add_documents(enhanced_documents)
            
            if success:
                logger.info("Text with context added successfully", extra={
                    'extra_fields': {
                        'event_type': 'context_aware_text_add_success',
                        'text_length': len(request.text),
                        'documents_added': len(enhanced_documents),
                        'context_type': request.context.context_type,
                        'correlation_id': correlation_id
                    }
                })
                
                return {
                    "success": True,
                    "message": f"Text added with context '{request.context.context_type}'",
                    "documents_added": len(enhanced_documents),
                    "context": {
                        "context_type": request.context.context_type,
                        "content_domain": request.context.content_domain,
                        "document_category": request.context.document_category,
                        "relevance_tags": request.context.relevance_tags
                    }
                }
            else:
                raise Exception("Failed to add text to vector store")
                
        except Exception as e:
            logger.error("Error adding text with context", extra={
                'extra_fields': {
                    'event_type': 'context_aware_text_add_error',
                    'text_length': len(request.text),
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'error_details': {
                        'documents_count': len(enhanced_documents) if 'enhanced_documents' in locals() else 'unknown',
                        'rag_service_type': type(self.rag_service).__name__,
                        'vector_store_type': type(self.rag_service.vector_store).__name__ if hasattr(self.rag_service, 'vector_store') else 'unknown',
                        'embedding_provider_type': type(self.rag_service.vector_store.embedding_provider).__name__ if hasattr(self.rag_service, 'vector_store') and hasattr(self.rag_service.vector_store, 'embedding_provider') else 'unknown',
                        'vector_store_provider_type': type(self.rag_service.vector_store.vector_store_provider).__name__ if hasattr(self.rag_service, 'vector_store') and hasattr(self.rag_service.vector_store, 'vector_store_provider') else 'unknown'
                    },
                    'correlation_id': correlation_id
                }
            })
            
            return {
                "success": False,
                "message": f"Error adding text: {str(e)}",
                "context": {
                    "context_type": request.context.context_type,
                    "content_domain": request.context.content_domain,
                    "document_category": request.context.document_category
                }
            }
    
    async def ask_question_with_context(self, 
                                      question: str, 
                                      system_message: str = "",
                                      top_k: int = None,
                                      context_filter: Optional[DocumentContext] = None) -> Dict[str, Any]:
        """Ask question with context awareness based on system message"""
        correlation_id = get_correlation_id()
        
        logger.info("Starting context-aware question processing", extra={
            'extra_fields': {
                'event_type': 'context_aware_question_start',
                'question_length': len(question),
                'system_message_length': len(system_message),
                'top_k': top_k,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Parse system message for directives
            directive = self.system_parser.parse_system_message(system_message)
            
            # Handle response mode
            result = await self.response_handler.handle_response_mode(
                question, system_message, directive, top_k
            )
            
            logger.info("Context-aware question processing completed", extra={
                'extra_fields': {
                    'event_type': 'context_aware_question_complete',
                    'response_mode': result.get('response_mode', 'unknown'),
                    'context_used': result.get('context_used', 'unknown'),
                    'correlation_id': correlation_id
                }
            })
            
            return result
                
        except Exception as e:
            logger.error("Error in context-aware question processing", extra={
                'extra_fields': {
                    'event_type': 'context_aware_question_error',
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
                "question": question,
                "response_mode": "error"
            }
    
    # Delegate other methods to the wrapped RAG service
    async def get_stats(self) -> Dict[str, Any]:
        return await self.rag_service.get_stats()
    
    def clear_knowledge_base(self) -> Dict[str, Any]:
        return self.rag_service.clear_knowledge_base() 