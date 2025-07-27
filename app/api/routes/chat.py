from fastapi import APIRouter, HTTPException
from app.domain.models import ChatCompletionRequest, ChatCompletionResponse
from app.domain.services.rag_service import RAGService
from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)
router = APIRouter()
rag_service = RAGService()

@router.post("/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """RAG-enhanced chat completions with enhanced logging"""
    correlation_id = get_correlation_id()
    
    logger.info("Chat completion request received", extra={
        'extra_fields': {
            'event_type': 'api_chat_completion_request_start',
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
            logger.warning("Chat completion validation failed - no messages", extra={
                'extra_fields': {
                    'event_type': 'api_chat_completion_validation_failure',
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
            logger.warning("Chat completion validation failed - no user message", extra={
                'extra_fields': {
                    'event_type': 'api_chat_completion_validation_failure',
                    'error': 'No user message found',
                    'correlation_id': correlation_id
                }
            })
            raise HTTPException(status_code=400, detail="No user message found")
        
        logger.info("Chat completion validation passed", extra={
            'extra_fields': {
                'event_type': 'api_chat_completion_validation_success',
                'model': request.model,
                'messages_count': len(request.messages),
                'last_user_message_length': len(last_user_message),
                'correlation_id': correlation_id
            }
        })
        
        # Process the question using RAG
        logger.info("Starting RAG processing for chat completion", extra={
            'extra_fields': {
                'event_type': 'api_chat_completion_rag_processing_start',
                'model': request.model,
                'last_user_message_length': len(last_user_message),
                'correlation_id': correlation_id
            }
        })
        
        rag_result = await rag_service.ask_question(last_user_message, top_k=3)
        
        logger.info("RAG processing completed for chat completion", extra={
            'extra_fields': {
                'event_type': 'api_chat_completion_rag_processing_complete',
                'model': request.model,
                'rag_success': rag_result.get('success', False),
                'rag_answer_length': len(rag_result.get('answer', '')),
                'rag_sources_count': len(rag_result.get('sources', [])),
                'correlation_id': correlation_id
            }
        })
        
        # Prepare the response
        if rag_result.get('success', False):
            # Use RAG-enhanced answer
            content = rag_result['answer']
            sources = rag_result.get('sources', [])
            
            logger.info("Using RAG-enhanced answer for chat completion", extra={
                'extra_fields': {
                    'event_type': 'api_chat_completion_rag_answer_used',
                    'model': request.model,
                    'answer_length': len(content),
                    'sources_count': len(sources),
                    'correlation_id': correlation_id
                }
            })
        else:
            # Fallback to default response
            content = "I'm sorry, I couldn't find relevant information to answer your question."
            sources = []
            
            logger.warning("Using fallback answer for chat completion", extra={
                'extra_fields': {
                    'event_type': 'api_chat_completion_fallback_used',
                    'model': request.model,
                    'rag_error': rag_result.get('answer', 'Unknown error'),
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
        
        logger.info("Chat completion response generated successfully", extra={
            'extra_fields': {
                'event_type': 'api_chat_completion_response_generated',
                'model': request.model,
                'response_id': response.id,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens,
                'sources_count': len(sources),
                'correlation_id': correlation_id
            }
        })
        
        return response
        
    except HTTPException:
        logger.error("Chat completion failed with HTTP exception", extra={
            'extra_fields': {
                'event_type': 'api_chat_completion_http_error',
                'model': request.model if hasattr(request, 'model') else 'unknown',
                'correlation_id': correlation_id
            }
        })
        raise
    except Exception as e:
        logger.error("Chat completion failed with unexpected error", extra={
            'extra_fields': {
                'event_type': 'api_chat_completion_error',
                'model': request.model if hasattr(request, 'model') else 'unknown',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e)) 