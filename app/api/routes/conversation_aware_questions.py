from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.domain.services.conversation_aware_rag_service import ConversationAwareRAGService
from app.domain.models.requests import ChatMessage
from app.infrastructure.providers import get_embedding_provider, get_llm_provider, get_vector_store_provider
from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)

router = APIRouter(prefix="/conversation-aware-questions", tags=["Conversation-Aware Questions"])

class ConversationAwareQuestionRequest(BaseModel):
    """Request model for conversation-aware questions"""
    messages: List[ChatMessage]
    current_question: str
    top_k: Optional[int] = None
    analysis_strategy: Optional[str] = None

class ConversationAwareQuestionResponse(BaseModel):
    """Response model for conversation-aware questions"""
    success: bool
    answer: str
    sources: List[Dict[str, Any]]
    question: str
    conversation_context_used: bool
    conversation_analysis: Optional[Dict[str, Any]] = None
    enhanced_queries: Optional[Dict[str, Any]] = None
    conversation_context: Optional[Dict[str, Any]] = None
    fallback_reason: Optional[str] = None

@router.post("/ask", response_model=ConversationAwareQuestionResponse)
async def ask_conversation_aware_question(request: ConversationAwareQuestionRequest):
    """
    Ask a question using conversation-aware RAG capabilities.
    
    Features:
    - Analyzes entire conversation context
    - Extracts topics, entities, and context clues
    - Generates multiple enhanced queries
    - Performs multi-query retrieval
    - Merges and deduplicates results
    - Provides conversation context information
    """
    correlation_id = get_correlation_id()
    
    logger.info("Conversation-aware question endpoint called", extra={
        'extra_fields': {
            'event_type': 'conversation_aware_question_endpoint_called',
            'messages_count': len(request.messages),
            'current_question_length': len(request.current_question),
            'top_k': request.top_k,
            'analysis_strategy': request.analysis_strategy,
            'correlation_id': correlation_id
        }
    })
    
    try:
        # Validate request
        if not request.messages:
            logger.warning("Conversation-aware question validation failed - no messages", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_question_validation_failure',
                    'error': 'Messages cannot be empty',
                    'correlation_id': correlation_id
                }
            })
            raise HTTPException(status_code=400, detail="Messages cannot be empty")
        
        if not request.current_question or not request.current_question.strip():
            logger.warning("Conversation-aware question validation failed - no current question", extra={
                'extra_fields': {
                    'event_type': 'conversation_aware_question_validation_failure',
                    'error': 'Current question cannot be empty',
                    'correlation_id': correlation_id
                }
            })
            raise HTTPException(status_code=400, detail="Current question cannot be empty")
        
        # Create conversation-aware RAG service
        conversation_aware_rag_service = ConversationAwareRAGService(
            embedding_provider=get_embedding_provider(),
            llm_provider=get_llm_provider(),
            vector_store_provider=get_vector_store_provider()
        )
        
        # Ask the conversation-aware question
        result = await conversation_aware_rag_service.ask_question_with_conversation(
            messages=request.messages,
            current_question=request.current_question,
            top_k=request.top_k,
            analysis_strategy=request.analysis_strategy
        )
        
        logger.info("Conversation-aware question processed successfully", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_question_processing_success',
                'success': result.get('success', False),
                'answer_length': len(result.get('answer', '')),
                'sources_count': len(result.get('sources', [])),
                'conversation_context_used': result.get('conversation_context_used', False),
                'correlation_id': correlation_id
            }
        })
        
        return ConversationAwareQuestionResponse(**result)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error("Error in conversation-aware question endpoint", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_question_endpoint_error',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing conversation-aware question: {str(e)}"
        )

@router.get("/strategies")
async def get_available_strategies():
    """
    Get available conversation analysis strategies.
    
    Returns:
        List of available strategies with descriptions
    """
    correlation_id = get_correlation_id()
    
    logger.debug("Getting available conversation analysis strategies", extra={
        'extra_fields': {
            'event_type': 'conversation_aware_strategies_request',
            'correlation_id': correlation_id
        }
    })
    
    try:
        from app.domain.services.conversation.analyzer import ConversationAnalyzer
        
        analyzer = ConversationAnalyzer()
        strategies = analyzer.get_available_strategies()
        
        strategy_info = {}
        for strategy_name in strategies:
            info = analyzer.get_strategy_info(strategy_name)
            if info:
                strategy_info[strategy_name] = info
        
        logger.info("Available strategies retrieved successfully", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_strategies_success',
                'strategies_count': len(strategies),
                'strategies': strategies,
                'correlation_id': correlation_id
            }
        })
        
        return {
            "available_strategies": strategies,
            "strategy_details": strategy_info
        }
        
    except Exception as e:
        logger.error("Error getting available strategies", extra={
            'extra_fields': {
                'event_type': 'conversation_aware_strategies_error',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Error getting available strategies: {str(e)}"
        ) 