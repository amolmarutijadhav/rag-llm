from typing import List, Dict, Any, Optional
from app.domain.models.conversation import ConversationContext, ConversationAnalysisResult, EnhancedQuery
from app.domain.models.requests import ChatMessage
from app.domain.services.conversation.strategies import (
    ConversationAnalysisStrategy, 
    TopicExtractionStrategy, 
    EntityExtractionStrategy, 
    ContextClueStrategy, 
    HybridAnalysisStrategy
)
from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)

class ConversationAnalyzer:
    """Main conversation analyzer that coordinates different analysis strategies"""
    
    def __init__(self, default_strategy: Optional[ConversationAnalysisStrategy] = None):
        """
        Initialize conversation analyzer with optional default strategy.
        If no strategy is provided, uses HybridAnalysisStrategy by default.
        """
        self.default_strategy = default_strategy or HybridAnalysisStrategy()
        self.available_strategies = {
            'topic': TopicExtractionStrategy(),
            'entity': EntityExtractionStrategy(),
            'context_clue': ContextClueStrategy(),
            'hybrid': HybridAnalysisStrategy()
        }
        
        logger.info("Conversation analyzer initialized", extra={
            'extra_fields': {
                'event_type': 'conversation_analyzer_initialization',
                'default_strategy': self.default_strategy.get_strategy_name(),
                'available_strategies': list(self.available_strategies.keys())
            }
        })
    
    async def analyze_conversation(self, 
                                 messages: List[ChatMessage], 
                                 strategy_name: Optional[str] = None) -> ConversationAnalysisResult:
        """
        Analyze conversation using specified strategy or default strategy.
        
        Args:
            messages: List of chat messages to analyze
            strategy_name: Name of strategy to use (optional)
            
        Returns:
            ConversationAnalysisResult with extracted context
        """
        correlation_id = get_correlation_id()
        
        logger.info("Starting conversation analysis", extra={
            'extra_fields': {
                'event_type': 'conversation_analyzer_start',
                'messages_count': len(messages),
                'strategy_name': strategy_name or 'default',
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Select strategy
            if strategy_name and strategy_name in self.available_strategies:
                strategy = self.available_strategies[strategy_name]
            else:
                strategy = self.default_strategy
                if strategy_name:
                    logger.warning(f"Unknown strategy '{strategy_name}', using default", extra={
                        'extra_fields': {
                            'event_type': 'conversation_analyzer_unknown_strategy',
                            'requested_strategy': strategy_name,
                            'using_strategy': strategy.get_strategy_name(),
                            'correlation_id': correlation_id
                        }
                    })
            
            # Analyze conversation
            result = await strategy.analyze_conversation(messages)
            
            logger.info("Conversation analysis completed", extra={
                'extra_fields': {
                    'event_type': 'conversation_analyzer_complete',
                    'strategy_used': result.analysis_method,
                    'confidence_score': result.confidence_score,
                    'processing_time_ms': result.processing_time_ms,
                    'topics_found': len(result.context.topics),
                    'entities_found': len(result.context.entities),
                    'clues_found': len(result.context.context_clues),
                    'correlation_id': correlation_id
                }
            })
            
            return result
            
        except Exception as e:
            logger.error("Error in conversation analysis", extra={
                'extra_fields': {
                    'event_type': 'conversation_analyzer_error',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            # Return empty result on error
            return ConversationAnalysisResult(
                context=ConversationContext(),
                confidence_score=0.0,
                analysis_method=strategy_name or 'error',
                processing_time_ms=0.0
            )
    
    async def generate_enhanced_queries(self, 
                                      current_question: str, 
                                      conversation_context: ConversationContext) -> EnhancedQuery:
        """
        Generate enhanced queries using conversation context.
        
        Args:
            current_question: The current user question
            conversation_context: Extracted conversation context
            
        Returns:
            EnhancedQuery with multiple query variations
        """
        correlation_id = get_correlation_id()
        
        logger.debug("Generating enhanced queries", extra={
            'extra_fields': {
                'event_type': 'conversation_analyzer_query_generation_start',
                'current_question_length': len(current_question),
                'topics_count': len(conversation_context.topics),
                'entities_count': len(conversation_context.entities),
                'correlation_id': correlation_id
            }
        })
        
        try:
            enhanced_queries = [current_question]  # Always include original question
            
            # Generate topic-enhanced queries
            if conversation_context.topics:
                topic_query = f"{current_question} {' '.join(conversation_context.topics[:2])}"
                enhanced_queries.append(topic_query)
            
            # Generate entity-enhanced queries
            if conversation_context.entities:
                entity_query = f"{current_question} {' '.join(conversation_context.entities[:3])}"
                enhanced_queries.append(entity_query)
            
            # Generate context clue-enhanced queries
            if conversation_context.context_clues:
                context_query = f"{current_question} {' '.join(conversation_context.context_clues[:2])}"
                enhanced_queries.append(context_query)
            
            # Generate combined query
            if conversation_context.topics and conversation_context.entities:
                combined_query = f"{current_question} {' '.join(conversation_context.topics[:1] + conversation_context.entities[:2])}"
                enhanced_queries.append(combined_query)
            
            # Remove duplicates while preserving order
            unique_queries = list(dict.fromkeys(enhanced_queries))
            
            enhanced_query = EnhancedQuery(
                original_query=current_question,
                enhanced_queries=unique_queries,
                context_used=conversation_context,
                query_generation_method="conversation_context_enhancement"
            )
            
            logger.info("Enhanced queries generated successfully", extra={
                'extra_fields': {
                    'event_type': 'conversation_analyzer_query_generation_complete',
                    'original_query_length': len(current_question),
                    'enhanced_queries_count': len(unique_queries),
                    'queries': unique_queries,
                    'correlation_id': correlation_id
                }
            })
            
            return enhanced_query
            
        except Exception as e:
            logger.error("Error generating enhanced queries", extra={
                'extra_fields': {
                    'event_type': 'conversation_analyzer_query_generation_error',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            # Return original query on error
            return EnhancedQuery(
                original_query=current_question,
                enhanced_queries=[current_question],
                context_used=conversation_context,
                query_generation_method="error_fallback"
            )
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available analysis strategies"""
        return list(self.available_strategies.keys())
    
    def get_strategy_info(self, strategy_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific strategy"""
        if strategy_name in self.available_strategies:
            strategy = self.available_strategies[strategy_name]
            return {
                'name': strategy.get_strategy_name(),
                'description': strategy.__class__.__doc__ or 'No description available'
            }
        return None 