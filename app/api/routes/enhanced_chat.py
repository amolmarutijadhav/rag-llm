"""
Enhanced Chat Completion Route using Strategy Pattern and Plugin Architecture.
Maintains external interface compatibility while providing enhanced functionality.
"""

from fastapi import APIRouter, HTTPException
from app.domain.models import ChatCompletionRequest, ChatCompletionResponse
from app.domain.services.enhanced_chat_completion_service import EnhancedChatCompletionService
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

@router.post("/completions", response_model=ChatCompletionResponse)
async def enhanced_chat_completions(request: ChatCompletionRequest):
    """Enhanced RAG-enhanced chat completions with conversation awareness"""
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
        
        # Check for user message
        has_user_message = any(msg.role == "user" for msg in request.messages)
        if not has_user_message:
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
                'correlation_id': correlation_id
            }
        })
        
        # Process request using enhanced service
        response = await enhanced_service.process_request(request)
        
        logger.info("Enhanced chat completion response generated successfully", extra={
            'extra_fields': {
                'event_type': 'enhanced_chat_completion_response_generated',
                'model': request.model,
                'response_id': response.id,
                'completion_tokens': response.usage.get('completion_tokens', 0) if response.usage else 0,
                'total_tokens': response.usage.get('total_tokens', 0) if response.usage else 0,
                'sources_count': len(response.sources) if response.sources else 0,
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