from abc import ABC, abstractmethod
from typing import List, Dict, Any
import re
import time
from app.domain.models.conversation import ConversationContext, ConversationAnalysisResult
from app.domain.models.requests import ChatMessage
from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)

class ConversationAnalysisStrategy(ABC):
    """Abstract base class for conversation analysis strategies"""
    
    @abstractmethod
    async def analyze_conversation(self, messages: List[ChatMessage]) -> ConversationAnalysisResult:
        """Analyze conversation and extract context"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy"""
        pass

class TopicExtractionStrategy(ConversationAnalysisStrategy):
    """Strategy for extracting topics from conversation"""
    
    def __init__(self):
        self.topic_keywords = {
            'technology': ['python', 'programming', 'code', 'software', 'development', 'api', 'database'],
            'business': ['company', 'business', 'strategy', 'market', 'product', 'service', 'customer'],
            'education': ['learning', 'study', 'course', 'training', 'education', 'knowledge', 'skill'],
            'health': ['health', 'medical', 'treatment', 'patient', 'doctor', 'hospital', 'medicine'],
            'finance': ['money', 'finance', 'investment', 'banking', 'economy', 'financial', 'budget']
        }
    
    def get_strategy_name(self) -> str:
        return "topic_extraction"
    
    async def analyze_conversation(self, messages: List[ChatMessage]) -> ConversationAnalysisResult:
        """Extract topics from conversation using keyword matching"""
        correlation_id = get_correlation_id()
        start_time = time.time()
        
        logger.debug("Starting topic extraction analysis", extra={
            'extra_fields': {
                'event_type': 'conversation_topic_extraction_start',
                'messages_count': len(messages),
                'strategy': self.get_strategy_name(),
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Extract all text from conversation
            conversation_text = " ".join([msg.content.lower() for msg in messages if msg.role == "user"])
            
            # Find topics based on keyword matching
            found_topics = []
            topic_scores = {}
            
            for topic, keywords in self.topic_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in conversation_text:
                        score += 1
                
                if score > 0:
                    found_topics.append(topic)
                    topic_scores[topic] = score
            
            # Sort topics by relevance score
            found_topics.sort(key=lambda x: topic_scores[x], reverse=True)
            
            # Create conversation context
            context = ConversationContext(
                topics=found_topics[:5],  # Top 5 topics
                conversation_length=len(messages),
                last_user_message=messages[-1].content if messages else None
            )
            
            processing_time = (time.time() - start_time) * 1000
            confidence_score = min(sum(topic_scores.values()) / len(conversation_text.split()), 1.0)
            
            logger.info("Topic extraction analysis completed", extra={
                'extra_fields': {
                    'event_type': 'conversation_topic_extraction_complete',
                    'topics_found': len(found_topics),
                    'topics': found_topics,
                    'confidence_score': confidence_score,
                    'processing_time_ms': processing_time,
                    'correlation_id': correlation_id
                }
            })
            
            return ConversationAnalysisResult(
                context=context,
                confidence_score=confidence_score,
                analysis_method=self.get_strategy_name(),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error("Error in topic extraction analysis", extra={
                'extra_fields': {
                    'event_type': 'conversation_topic_extraction_error',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            # Return empty context on error
            return ConversationAnalysisResult(
                context=ConversationContext(),
                confidence_score=0.0,
                analysis_method=self.get_strategy_name(),
                processing_time_ms=(time.time() - start_time) * 1000
            )

class EntityExtractionStrategy(ConversationAnalysisStrategy):
    """Strategy for extracting entities from conversation"""
    
    def __init__(self):
        # Simple entity patterns - can be enhanced with NER models
        self.entity_patterns = {
            'person': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Simple name pattern
            'organization': r'\b[A-Z][a-zA-Z\s&]+(?:Inc|Corp|LLC|Ltd|Company|Organization)\b',
            'technology': r'\b(?:Python|Java|JavaScript|React|Angular|Node\.js|Docker|Kubernetes|AWS|Azure|GCP)\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
            'number': r'\b\d+(?:\.\d+)?\b'
        }
    
    def get_strategy_name(self) -> str:
        return "entity_extraction"
    
    async def analyze_conversation(self, messages: List[ChatMessage]) -> ConversationAnalysisResult:
        """Extract entities from conversation using pattern matching"""
        correlation_id = get_correlation_id()
        start_time = time.time()
        
        logger.debug("Starting entity extraction analysis", extra={
            'extra_fields': {
                'event_type': 'conversation_entity_extraction_start',
                'messages_count': len(messages),
                'strategy': self.get_strategy_name(),
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Extract all text from conversation
            conversation_text = " ".join([msg.content for msg in messages if msg.role == "user"])
            
            # Find entities using patterns
            found_entities = []
            entity_counts = {}
            
            for entity_type, pattern in self.entity_patterns.items():
                matches = re.findall(pattern, conversation_text, re.IGNORECASE)
                for match in matches:
                    entity = match.strip()
                    if entity not in found_entities:
                        found_entities.append(entity)
                        entity_counts[entity] = entity_counts.get(entity, 0) + 1
            
            # Sort entities by frequency
            found_entities.sort(key=lambda x: entity_counts[x], reverse=True)
            
            # Create conversation context
            context = ConversationContext(
                entities=found_entities[:10],  # Top 10 entities
                conversation_length=len(messages),
                last_user_message=messages[-1].content if messages else None
            )
            
            processing_time = (time.time() - start_time) * 1000
            confidence_score = min(len(found_entities) / max(len(conversation_text.split()), 1), 1.0)
            
            logger.info("Entity extraction analysis completed", extra={
                'extra_fields': {
                    'event_type': 'conversation_entity_extraction_complete',
                    'entities_found': len(found_entities),
                    'entities': found_entities[:5],  # Log top 5 entities
                    'confidence_score': confidence_score,
                    'processing_time_ms': processing_time,
                    'correlation_id': correlation_id
                }
            })
            
            return ConversationAnalysisResult(
                context=context,
                confidence_score=confidence_score,
                analysis_method=self.get_strategy_name(),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error("Error in entity extraction analysis", extra={
                'extra_fields': {
                    'event_type': 'conversation_entity_extraction_error',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            # Return empty context on error
            return ConversationAnalysisResult(
                context=ConversationContext(),
                confidence_score=0.0,
                analysis_method=self.get_strategy_name(),
                processing_time_ms=(time.time() - start_time) * 1000
            )

class ContextClueStrategy(ConversationAnalysisStrategy):
    """Strategy for extracting context clues from conversation"""
    
    def __init__(self):
        self.context_indicators = {
            'clarification': ['what do you mean', 'can you explain', 'i don\'t understand', 'clarify'],
            'follow_up': ['and then', 'what about', 'also', 'additionally', 'furthermore'],
            'comparison': ['compared to', 'versus', 'instead of', 'rather than', 'on the other hand'],
            'time_reference': ['yesterday', 'today', 'tomorrow', 'last week', 'next month', 'recently'],
            'importance': ['important', 'critical', 'essential', 'key', 'main', 'primary']
        }
    
    def get_strategy_name(self) -> str:
        return "context_clue_extraction"
    
    async def analyze_conversation(self, messages: List[ChatMessage]) -> ConversationAnalysisResult:
        """Extract context clues from conversation"""
        correlation_id = get_correlation_id()
        start_time = time.time()
        
        logger.debug("Starting context clue extraction analysis", extra={
            'extra_fields': {
                'event_type': 'conversation_context_clue_extraction_start',
                'messages_count': len(messages),
                'strategy': self.get_strategy_name(),
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Extract all text from conversation
            conversation_text = " ".join([msg.content.lower() for msg in messages if msg.role == "user"])
            
            # Find context clues
            found_clues = []
            clue_categories = {}
            
            for category, indicators in self.context_indicators.items():
                category_clues = []
                for indicator in indicators:
                    if indicator in conversation_text:
                        category_clues.append(indicator)
                
                if category_clues:
                    found_clues.extend(category_clues)
                    clue_categories[category] = category_clues
            
            # Create conversation context
            context = ConversationContext(
                context_clues=found_clues,
                conversation_length=len(messages),
                last_user_message=messages[-1].content if messages else None
            )
            
            processing_time = (time.time() - start_time) * 1000
            confidence_score = min(len(found_clues) / max(len(conversation_text.split()), 1), 1.0)
            
            logger.info("Context clue extraction analysis completed", extra={
                'extra_fields': {
                    'event_type': 'conversation_context_clue_extraction_complete',
                    'clues_found': len(found_clues),
                    'clue_categories': list(clue_categories.keys()),
                    'confidence_score': confidence_score,
                    'processing_time_ms': processing_time,
                    'correlation_id': correlation_id
                }
            })
            
            return ConversationAnalysisResult(
                context=context,
                confidence_score=confidence_score,
                analysis_method=self.get_strategy_name(),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error("Error in context clue extraction analysis", extra={
                'extra_fields': {
                    'event_type': 'conversation_context_clue_extraction_error',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            # Return empty context on error
            return ConversationAnalysisResult(
                context=ConversationContext(),
                confidence_score=0.0,
                analysis_method=self.get_strategy_name(),
                processing_time_ms=(time.time() - start_time) * 1000
            )

class HybridAnalysisStrategy(ConversationAnalysisStrategy):
    """Combines multiple analysis strategies for comprehensive context extraction"""
    
    def __init__(self):
        self.strategies = [
            TopicExtractionStrategy(),
            EntityExtractionStrategy(),
            ContextClueStrategy()
        ]
    
    def get_strategy_name(self) -> str:
        return "hybrid_analysis"
    
    async def analyze_conversation(self, messages: List[ChatMessage]) -> ConversationAnalysisResult:
        """Combine results from multiple analysis strategies"""
        correlation_id = get_correlation_id()
        start_time = time.time()
        
        logger.debug("Starting hybrid analysis", extra={
            'extra_fields': {
                'event_type': 'conversation_hybrid_analysis_start',
                'messages_count': len(messages),
                'strategies_count': len(self.strategies),
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Run all strategies
            results = []
            for strategy in self.strategies:
                result = await strategy.analyze_conversation(messages)
                results.append(result)
            
            # Combine results
            combined_context = ConversationContext(
                conversation_length=len(messages),
                last_user_message=messages[-1].content if messages else None
            )
            
            # Merge topics, entities, and context clues
            all_topics = []
            all_entities = []
            all_clues = []
            
            for result in results:
                all_topics.extend(result.context.topics)
                all_entities.extend(result.context.entities)
                all_clues.extend(result.context.context_clues)
            
            # Remove duplicates and limit
            combined_context.topics = list(dict.fromkeys(all_topics))[:5]
            combined_context.entities = list(dict.fromkeys(all_entities))[:10]
            combined_context.context_clues = list(dict.fromkeys(all_clues))[:5]
            
            # Calculate average confidence
            avg_confidence = sum(r.confidence_score for r in results) / len(results)
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.info("Hybrid analysis completed", extra={
                'extra_fields': {
                    'event_type': 'conversation_hybrid_analysis_complete',
                    'topics_found': len(combined_context.topics),
                    'entities_found': len(combined_context.entities),
                    'clues_found': len(combined_context.context_clues),
                    'avg_confidence_score': avg_confidence,
                    'processing_time_ms': processing_time,
                    'correlation_id': correlation_id
                }
            })
            
            return ConversationAnalysisResult(
                context=combined_context,
                confidence_score=avg_confidence,
                analysis_method=self.get_strategy_name(),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error("Error in hybrid analysis", extra={
                'extra_fields': {
                    'event_type': 'conversation_hybrid_analysis_error',
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'correlation_id': correlation_id
                }
            })
            
            # Return empty context on error
            return ConversationAnalysisResult(
                context=ConversationContext(),
                confidence_score=0.0,
                analysis_method=self.get_strategy_name(),
                processing_time_ms=(time.time() - start_time) * 1000
            ) 