"""
Enhanced Chat Completion Route using Strategy Pattern and Plugin Architecture.
Maintains external interface compatibility while providing enhanced functionality.
"""

from fastapi import APIRouter, HTTPException
from app.domain.models import ChatCompletionRequest, ChatCompletionResponse
from app.domain.services.enhanced_chat_completion_service import EnhancedChatCompletionService
from app.domain.services.context_aware_rag_service import ContextAwareRAGService
from app.domain.services.system_message_parser import SystemMessageParser
from app.domain.services.rag_service import RAGService
from app.infrastructure.providers.service_locator import ServiceLocator
from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)
router = APIRouter()

# Initialize services
rag_service = RAGService()
service_locator = ServiceLocator()
llm_provider = service_locator.get_llm_provider()
enhanced_service = EnhancedChatCompletionService(rag_service, llm_provider)

# Initialize context-aware services
context_aware_rag_service = ContextAwareRAGService(rag_service=rag_service, llm_provider=llm_provider)
system_parser = SystemMessageParser()

@router.post("/completions", response_model=ChatCompletionResponse)
async def enhanced_chat_completions(request: ChatCompletionRequest):
    """Enhanced RAG-enhanced chat completions with conversation awareness and context-aware features"""
    correlation_id = get_correlation_id()
    
    logger.info("Enhanced chat completion request received", extra={
        'extra_fields': {
            'event_type': 'enhanced_chat_completion_request_start',
            'model': request.model,
            'messages_count': len(request.messages),
            'temperature': request.temperature,
            'max_tokens': request.max_tokens,
            'correlation_id': correlation_id
        }
    })
    
    try:
        # Validate request
        if not request.messages or len(request.messages) == 0:
            logger.warning("Enhanced chat completion validation failed - no messages", extra={
                'extra_fields': {
                    'event_type': 'enhanced_chat_completion_validation_failure',
                    'error': 'Messages cannot be empty',
                    'correlation_id': correlation_id
                }
            })
            raise HTTPException(status_code=400, detail="Messages cannot be empty")
        
        # Extract system message and last user message
        system_message = ""
        last_user_message = None
        
        for message in request.messages:
            if message.role == "system":
                system_message = message.content
            elif message.role == "user":
                last_user_message = message.content
        
        if not last_user_message:
            logger.warning("Enhanced chat completion validation failed - no user message", extra={
                'extra_fields': {
                    'event_type': 'enhanced_chat_completion_validation_failure',
                    'error': 'No user message found',
                    'correlation_id': correlation_id
                }
            })
            raise HTTPException(status_code=400, detail="No user message found")
        
        logger.info("Enhanced chat completion validation passed", extra={
            'extra_fields': {
                'event_type': 'enhanced_chat_completion_validation_success',
                'model': request.model,
                'messages_count': len(request.messages),
                'last_user_message_length': len(last_user_message),
                'system_message_length': len(system_message),
                'correlation_id': correlation_id
            }
        })
        
        # Check if system message contains context-aware directives
        has_context_directives = any(keyword in system_message.upper() for keyword in [
            'RESPONSE_MODE:', 'DOCUMENT_CONTEXT:', 'CONTENT_DOMAINS:', 
            'DOCUMENT_CATEGORIES:', 'MIN_CONFIDENCE:', 'FALLBACK_STRATEGY:'
        ]) or '<config>' in system_message
        
        if has_context_directives:
            # Use context-aware RAG service
            logger.info("Using context-aware RAG processing", extra={
                'extra_fields': {
                    'event_type': 'context_aware_rag_processing_start',
                    'model': request.model,
                    'last_user_message_length': len(last_user_message),
                    'system_message_length': len(system_message),
                    'correlation_id': correlation_id
                }
            })
            
            # Process with context-aware RAG
            rag_result = await context_aware_rag_service.ask_question_with_context(
                question=last_user_message,
                system_message=system_message,
                top_k=3
            )
            
            logger.info("Context-aware RAG processing completed", extra={
                'extra_fields': {
                    'event_type': 'context_aware_rag_processing_complete',
                    'model': request.model,
                    'rag_success': rag_result.get('success', False),
                    'response_mode': rag_result.get('response_mode', 'unknown'),
                    'context_used': rag_result.get('context_used', 'unknown'),
                    'correlation_id': correlation_id
                }
            })
            
            # Prepare the response
            if rag_result.get('success', False):
                content = rag_result['answer']
                sources = rag_result.get('sources', [])
                
                logger.info("Using context-aware RAG answer", extra={
                    'extra_fields': {
                        'event_type': 'context_aware_rag_answer_used',
                        'model': request.model,
                        'answer_length': len(content),
                        'sources_count': len(sources),
                        'response_mode': rag_result.get('response_mode', 'unknown'),
                        'context_used': rag_result.get('context_used', 'unknown'),
                        'correlation_id': correlation_id
                    }
                })
            else:
                # Fallback response
                content = rag_result.get('answer', "I'm sorry, I couldn't process your request.")
                sources = []
                
                logger.warning("Using fallback answer for context-aware chat completion", extra={
                    'extra_fields': {
                        'event_type': 'context_aware_chat_completion_fallback_used',
                        'model': request.model,
                        'rag_error': rag_result.get('answer', 'Unknown error'),
                        'response_mode': rag_result.get('response_mode', 'unknown'),
                        'correlation_id': correlation_id
                    }
                })
            
            # Create chat completion response
            response = ChatCompletionResponse(
                id=f"chatcmpl-{correlation_id}",
                object="chat.completion",
                created=int(__import__('time').time()),
                model=request.model,
                choices=[
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content
                        },
                        "finish_reason": "stop"
                    }
                ],
                usage={
                    "prompt_tokens": len(last_user_message.split()),
                    "completion_tokens": len(content.split()),
                    "total_tokens": len(last_user_message.split()) + len(content.split())
                },
                sources=sources
            )
            
            # Add context-aware metadata
            response.metadata = {
                "context_aware": True,
                "response_mode": rag_result.get('response_mode', 'unknown'),
                "context_used": rag_result.get('context_used', 'unknown'),
                "fallback_reason": rag_result.get('fallback_reason'),
                "confidence_score": rag_result.get('confidence_score')
            }
            
        else:
            # Use existing enhanced service (backward compatibility)
            logger.info("Using existing enhanced service (no context directives)", extra={
                'extra_fields': {
                    'event_type': 'existing_enhanced_service_used',
                    'model': request.model,
                    'correlation_id': correlation_id
                }
            })
            
            response = await enhanced_service.process_request(request)
        
        logger.info("Enhanced chat completion response generated successfully", extra={
            'extra_fields': {
                'event_type': 'enhanced_chat_completion_response_generated',
                'model': request.model,
                'response_id': response.id,
                'completion_tokens': response.usage.get('completion_tokens', 0) if response.usage else 0,
                'total_tokens': response.usage.get('total_tokens', 0) if response.usage else 0,
                'sources_count': len(response.sources) if response.sources else 0,
                'context_aware': has_context_directives,
                'correlation_id': correlation_id
            }
        })
        
        return response
        
    except HTTPException:
        logger.error("Enhanced chat completion failed with HTTP exception", extra={
            'extra_fields': {
                'event_type': 'enhanced_chat_completion_http_error',
                'model': request.model if hasattr(request, 'model') else 'unknown',
                'correlation_id': correlation_id
            }
        })
        raise
    except Exception as e:
        logger.error("Enhanced chat completion failed with unexpected error", extra={
            'extra_fields': {
                'event_type': 'enhanced_chat_completion_error',
                'model': request.model if hasattr(request, 'model') else 'unknown',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
async def get_available_strategies():
    """Get available conversation analysis strategies"""
    correlation_id = get_correlation_id()
    
    logger.info("Strategies request received", extra={
        'extra_fields': {
            'event_type': 'strategies_request',
            'correlation_id': correlation_id
        }
    })
    
    try:
        strategies = [
            {
                "name": "topic_tracking",
                "description": "Tracks conversation topics and generates topic-aware queries",
                "features": ["Topic extraction", "Context clue identification", "Multi-topic queries"]
            },
            {
                "name": "entity_extraction", 
                "description": "Extracts entities and generates entity-aware queries",
                "features": ["Entity extraction", "Relationship identification", "Entity-based queries"]
            }
        ]
        
        logger.info("Strategies request completed", extra={
            'extra_fields': {
                'event_type': 'strategies_response',
                'strategies_count': len(strategies),
                'correlation_id': correlation_id
            }
        })
        
        return {
            "strategies": strategies,
            "total": len(strategies)
        }
        
    except Exception as e:
        logger.error("Strategies request failed", extra={
            'extra_fields': {
                'event_type': 'strategies_error',
                'error': str(e),
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plugins")
async def get_available_plugins():
    """Get available processing plugins"""
    correlation_id = get_correlation_id()
    
    logger.info("Plugins request received", extra={
        'extra_fields': {
            'event_type': 'plugins_request',
            'correlation_id': correlation_id
        }
    })
    
    try:
        plugins = [
            {
                "name": "conversation_context",
                "description": "Analyzes conversation context and determines processing strategy",
                "priority": "HIGH",
                "features": ["Context analysis", "Strategy selection", "Conversation tracking"]
            },
            {
                "name": "multi_query_rag",
                "description": "Performs multi-query RAG processing with enhanced retrieval",
                "priority": "NORMAL", 
                "features": ["Multi-query generation", "Enhanced retrieval", "Result deduplication"]
            },
            {
                "name": "response_enhancement",
                "description": "Enhances final response with context and metadata",
                "priority": "LOW",
                "features": ["Response generation", "Metadata addition", "Context integration"]
            }
        ]
        
        logger.info("Plugins request completed", extra={
            'extra_fields': {
                'event_type': 'plugins_response',
                'plugins_count': len(plugins),
                'correlation_id': correlation_id
            }
        })
        
        return {
            "plugins": plugins,
            "total": len(plugins)
        }
        
    except Exception as e:
        logger.error("Plugins request failed", extra={
            'extra_fields': {
                'event_type': 'plugins_error',
                'error': str(e),
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e)) 

# Context-Aware RAG Endpoints

@router.get("/context-options")
async def get_context_options():
    """Get available context options for document upload"""
    correlation_id = get_correlation_id()
    
    logger.info("Context options request received", extra={
        'extra_fields': {
            'event_type': 'context_options_request',
            'correlation_id': correlation_id
        }
    })
    
    try:
        context_options = {
            "context_types": [
                "technical", "creative", "general", "api_docs", "user_guides", 
                "reference", "tutorial", "faq", "policies", "marketing", 
                "support", "legal", "academic"
            ],
            "content_domains": [
                "api_documentation", "user_support", "marketing", "technical_reference",
                "tutorials", "policies", "release_notes", "best_practices", 
                "troubleshooting", "examples", "getting_started", "advanced_topics"
            ],
            "document_categories": [
                "user_guide", "reference", "tutorial", "faq", "api_reference",
                "getting_started", "troubleshooting", "examples", "best_practices",
                "release_notes", "configuration", "deployment", "security"
            ],
            "response_modes": [
                "RAG_ONLY", "LLM_ONLY", "HYBRID", "SMART_FALLBACK", 
                "RAG_PRIORITY", "LLM_PRIORITY"
            ],
            "fallback_strategies": [
                "llm_knowledge", "refuse", "hybrid"
            ]
        }
        
        logger.info("Context options retrieved successfully", extra={
            'extra_fields': {
                'event_type': 'context_options_retrieved',
                'correlation_id': correlation_id
            }
        })
        
        return {
            "success": True,
            "context_options": context_options
        }
        
    except Exception as e:
        logger.error("Error retrieving context options", extra={
            'extra_fields': {
                'event_type': 'context_options_retrieval_error',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context-aware-stats")
async def get_context_aware_stats():
    """Get statistics for context-aware documents"""
    correlation_id = get_correlation_id()
    
    logger.info("Context-aware stats request received", extra={
        'extra_fields': {
            'event_type': 'context_aware_stats_request',
            'correlation_id': correlation_id
        }
    })
    
    try:
        stats = context_aware_rag_service.get_stats()
        
        logger.info("Context-aware stats retrieved successfully", extra={
            'extra_fields': {
                'event_type': 'context_aware_stats_retrieved',
                'correlation_id': correlation_id
            }
        })
        
        return stats
        
    except Exception as e:
        logger.error("Error retrieving context-aware stats", extra={
            'extra_fields': {
                'event_type': 'context_aware_stats_retrieval_error',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/context-aware-clear")
async def clear_context_aware_knowledge_base():
    """Clear all context-aware documents"""
    correlation_id = get_correlation_id()
    
    logger.info("Context-aware clear request received", extra={
        'extra_fields': {
            'event_type': 'context_aware_clear_request',
            'correlation_id': correlation_id
        }
    })
    
    try:
        result = context_aware_rag_service.clear_knowledge_base()
        
        logger.info("Context-aware knowledge base cleared successfully", extra={
            'extra_fields': {
                'event_type': 'context_aware_clear_success',
                'correlation_id': correlation_id
            }
        })
        
        return result
        
    except Exception as e:
        logger.error("Error clearing context-aware knowledge base", extra={
            'extra_fields': {
                'event_type': 'context_aware_clear_error',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e)) 