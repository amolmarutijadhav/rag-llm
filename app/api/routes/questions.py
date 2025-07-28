from fastapi import APIRouter, HTTPException
from app.domain.models import QuestionRequest, QuestionResponse, StatsResponse
from app.domain.services.rag_service import RAGService
from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)
router = APIRouter()
rag_service = RAGService()

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question and get an answer using RAG with enhanced logging"""
    correlation_id = get_correlation_id()
    
    logger.info("Question request received", extra={
        'extra_fields': {
            'event_type': 'api_question_request_start',
            'question_length': len(request.question),
            'top_k': request.top_k,
            'top_k_type': type(request.top_k).__name__,
            'correlation_id': correlation_id
        }
    })
    
    try:
        # Validate question input
        if not request.question or not request.question.strip():
            logger.warning("Question validation failed - empty question", extra={
                'extra_fields': {
                    'event_type': 'api_question_validation_failure',
                    'error': 'Question cannot be empty',
                    'correlation_id': correlation_id
                }
            })
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        logger.info("Question validation passed", extra={
            'extra_fields': {
                'event_type': 'api_question_validation_success',
                'question_length': len(request.question),
                'top_k': request.top_k,
                'correlation_id': correlation_id
            }
        })
        
        # Process the question using RAG
        logger.info("Starting question processing with RAG", extra={
            'extra_fields': {
                'event_type': 'api_question_rag_processing_start',
                'question_length': len(request.question),
                'top_k': request.top_k,
                'correlation_id': correlation_id
            }
        })
        
        result = await rag_service.ask_question(request.question, request.top_k)
        
        logger.info("Question processing completed", extra={
            'extra_fields': {
                'event_type': 'api_question_rag_processing_complete',
                'question_length': len(request.question),
                'processing_success': result.get('success', False),
                'answer_length': len(result.get('answer', '')),
                'sources_count': len(result.get('sources', [])),
                'correlation_id': correlation_id
            }
        })
        
        return QuestionResponse(**result)
        
    except HTTPException:
        logger.error("Question processing failed with HTTP exception", extra={
            'extra_fields': {
                'event_type': 'api_question_http_error',
                'question_length': len(request.question),
                'correlation_id': correlation_id
            }
        })
        raise
    except Exception as e:
        logger.error("Question processing failed with unexpected error", extra={
            'extra_fields': {
                'event_type': 'api_question_error',
                'question_length': len(request.question),
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics"""
    try:
        result = rag_service.get_stats()
        return StatsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 