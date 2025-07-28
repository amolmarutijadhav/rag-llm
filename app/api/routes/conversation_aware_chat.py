from fastapi import APIRouter, HTTPException
from app.domain.models import ChatCompletionRequest, ChatCompletionResponse
from app.domain.services.conversation_aware_rag_service import ConversationAwareRAGService
from app.infrastructure.providers import get_embedding_provider, get_llm_provider, get_vector_store_provider
from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)
router = APIRouter()

@router.post("/conversation-aware-completions", response_model=ChatCompletionResponse)
async def conversation_aware_chat_completions(request: ChatCompletionRequest):
    """
    Conversation-aware RAG-enhanced chat completions.
    
    Features:
    - Analyzes entire conversation context
    - Extracts topics, entities, and context clues
    - Generates multiple enhanced queries
    - Performs multi-query retrieval
    - Provides conversation context information
    """
    correlation_id = get_correlation_id()
    
    logger.info("Conversation-aware chat completion request received", extra={
        'extra_fields': {
            'event_type': 'conversation_aware_chat_completion_request_start',
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
            logger.warning("Conversation-aware chat completion validation failed - no messages", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_chat_completion_validation_failure',
                    'error': 'Messages cannot be empty',
                    'correlation_id': correlation_id
                }
            })
            raise HTTPException(status_code=400, detail="Messages cannot be empty")
        
        # Extract the last user message for RAG processing
        last_user_message = None
        for message in reversed(request.messages):
            if message.role == "user":
                last_user_message = message.content
                break
        
        if not last_user_message:
            logger.warning("Conversation-aware chat completion validation failed - no user message", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_chat_completion_validation_failure',
                    'error': 'No user message found',
                    'correlation_id': correlation_id
                }
            })
            raise HTTPException(status_code=400, detail="No user message found")
        
        logger.info("Conversation-aware chat completion validation passed", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_chat_completion_validation_success',
                'model': request.model,
                'messages_count': len(request.messages),
                'last_user_message_length': len(last_user_message),
                'correlation_id': correlation_id
            }
        })
        
        # Create conversation-aware RAG service (reusing the service from /ask endpoint)
        conversation_aware_rag_service = ConversationAwareRAGService(
            embedding_provider=get_embedding_provider(),
            llm_provider=get_llm_provider(),
            vector_store_provider=get_vector_store_provider()
        )
        
        # Process the question using conversation-aware RAG (reusing the same logic as /ask)
        logger.info("Starting conversation-aware RAG processing for chat completion", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_chat_completion_rag_processing_start',
                'model': request.model,
                'messages_count': len(request.messages),
                'last_user_message_length': len(last_user_message),
                'correlation_id': correlation_id
            }
        })
        
        # Reuse the same conversation-aware RAG logic from /ask endpoint
        rag_result = await conversation_aware_rag_service.ask_question_with_conversation(
            messages=request.messages,
            current_question=last_user_message,
            top_k=3
        )
        
        logger.info("Conversation-aware RAG processing completed for chat completion", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_chat_completion_rag_processing_complete',
                'model': request.model,
                'rag_success': rag_result.get('success', False),
                'rag_answer_length': len(rag_result.get('answer', '')),
                'rag_sources_count': len(rag_result.get('sources', [])),
                'conversation_context_used': rag_result.get('conversation_context_used', False),
                'correlation_id': correlation_id
            }
        })
        
        # Prepare the response
        if rag_result.get('success', False):
            # Use conversation-aware RAG-enhanced answer
            content = rag_result['answer']
            sources = rag_result.get('sources', [])
            
            logger.info("Using conversation-aware RAG-enhanced answer for chat completion", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_chat_completion_rag_answer_used',
                    'model': request.model,
                    'answer_length': len(content),
                    'sources_count': len(sources),
                    'conversation_context_used': rag_result.get('conversation_context_used', False),
                    'correlation_id': correlation_id
                }
            })
        else:
            # Fallback to default response
            content = "I'm sorry, I couldn't find relevant information to answer your question."
            sources = []
            
            logger.warning("Using fallback answer for conversation-aware chat completion", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_chat_completion_fallback_used',
                    'model': request.model,
                    'rag_error': rag_result.get('answer', 'Unknown error'),
                    'fallback_reason': rag_result.get('fallback_reason', 'Unknown'),
                    'correlation_id': correlation_id
                }
            })
        
        # Create chat completion response with conversation context information
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
        
        # Add conversation context information to response if available
        if rag_result.get('conversation_context_used', False):
            # Add conversation context as metadata
            response.conversation_context = {
                "used": True,
                "analysis": rag_result.get('conversation_analysis', {}),
                "enhanced_queries": rag_result.get('enhanced_queries', {}),
                "context_summary": rag_result.get('conversation_context', {})
            }
        else:
            response.conversation_context = {
                "used": False,
                "fallback_reason": rag_result.get('fallback_reason', 'Unknown')
            }
        
        logger.info("Conversation-aware chat completion response generated successfully", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_chat_completion_response_generated',
                'model': request.model,
                'response_id': response.id,
                'completion_tokens': response.usage['completion_tokens'],
                'total_tokens': response.usage['total_tokens'],
                'sources_count': len(sources),
                'conversation_context_used': rag_result.get('conversation_context_used', False),
                'correlation_id': correlation_id
            }
        })
        
        return response
        
    except HTTPException:
        logger.error("Conversation-aware chat completion failed with HTTP exception", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_chat_completion_http_error',
                'model': request.model if hasattr(request, 'model') else 'unknown',
                'correlation_id': correlation_id
            }
        })
        raise
    except Exception as e:
        logger.error("Conversation-aware chat completion failed with unexpected error", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_chat_completion_error',
                'model': request.model if hasattr(request, 'model') else 'unknown',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/completions-enhanced", response_model=ChatCompletionResponse)
async def enhanced_chat_completions(request: ChatCompletionRequest):
    """
    Enhanced chat completions with conversation awareness.
    This is an enhanced version of the original /completions endpoint.
    """
    return await conversation_aware_chat_completions(request) 