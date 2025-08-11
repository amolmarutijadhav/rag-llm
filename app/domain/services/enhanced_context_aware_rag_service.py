"""
Enhanced Context-Aware RAG Service
Integrates multi-turn conversation support with context-aware RAG functionality.
"""

from typing import List, Dict, Any, Optional
from app.domain.services.context_aware_rag_service import ContextAwareRAGService, ContextFilter
from app.domain.services.enhanced_chat_completion_service import (
    MultiTurnConversationStrategy, TopicTrackingStrategy, EntityExtractionStrategy,
    ConversationState, ConversationAnalysisStrategy
)
from app.domain.services.rag_service import RAGService
from app.domain.models.requests import (
    DocumentContext, DocumentUploadRequest, TextUploadRequest, 
    ContextAwareQuestionRequest, SystemMessageDirective, ResponseMode
)
from app.domain.interfaces.providers import EmbeddingProvider, LLMProvider, VectorStoreProvider
from app.core.config import Config
from app.core.enhanced_chat_config import EnhancedChatConfig
from app.core.logging_config import get_logger, get_correlation_id
from app.core.logging_helpers import log_extra
import asyncio
import re
import time

logger = get_logger(__name__)

class AdaptiveConfidenceManager:
    """Manages adaptive confidence thresholds based on conversation context"""
    
    def __init__(self):
        self.base_threshold = 0.7
        self.min_threshold = 0.3
        self.max_threshold = 0.95
        self.turn_decay_factor = 0.05
        self.context_boost_factor = 0.1
        self.session_thresholds = {}
    
    def get_adaptive_threshold(self, session_id: str, turn_number: int, 
                             context_quality: float, conversation_complexity: float) -> float:
        """Calculate adaptive confidence threshold based on conversation state"""
        correlation_id = get_correlation_id()
        
        # Base threshold adjustment
        threshold = self.base_threshold
        
        # Turn-based decay (lower threshold for later turns)
        turn_decay = min(turn_number * self.turn_decay_factor, 0.3)
        threshold -= turn_decay
        
        # Context quality boost
        if context_quality > 0.8:
            threshold += self.context_boost_factor
        
        # Complexity adjustment
        if conversation_complexity > 0.7:
            threshold -= 0.1  # Lower threshold for complex conversations
        elif conversation_complexity < 0.3:
            threshold += 0.05  # Higher threshold for simple conversations
        
        # Session-specific learning
        if session_id in self.session_thresholds:
            session_adjustment = self.session_thresholds[session_id].get('adjustment', 0.0)
            threshold += session_adjustment
        
        # Clamp to valid range
        threshold = max(self.min_threshold, min(self.max_threshold, threshold))
        
        logger.debug("Calculated adaptive threshold", extra={
            'extra_fields': {
                'event_type': 'threshold_calculation',
                'session_id': session_id,
                'turn_number': turn_number,
                'context_quality': context_quality,
                'conversation_complexity': conversation_complexity,
                'calculated_threshold': threshold,
                'correlation_id': correlation_id
            }
        })
        
        return threshold
    
    def update_session_threshold(self, session_id: str, actual_confidence: float, 
                               expected_confidence: float, success: bool):
        """Update session-specific threshold based on performance feedback"""
        if session_id not in self.session_thresholds:
            self.session_thresholds[session_id] = {'adjustment': 0.0, 'feedback_count': 0}
        
        session_data = self.session_thresholds[session_id]
        session_data['feedback_count'] += 1
        
        # Calculate adjustment based on performance
        if success and actual_confidence >= expected_confidence:
            # Good performance, slight boost
            adjustment = 0.02
        elif not success and actual_confidence < expected_confidence:
            # Poor performance, reduce threshold
            adjustment = -0.03
        else:
            # Mixed performance, small adjustment
            adjustment = 0.0
        
        # Apply exponential decay to adjustment
        decay_factor = 1.0 / (1.0 + session_data['feedback_count'] * 0.1)
        session_data['adjustment'] += adjustment * decay_factor
        
        # Clamp adjustment
        session_data['adjustment'] = max(-0.2, min(0.2, session_data['adjustment']))
        
        logger.debug("Updated session threshold", extra={
            'extra_fields': {
                'event_type': 'threshold_update',
                'session_id': session_id,
                'actual_confidence': actual_confidence,
                'expected_confidence': expected_confidence,
                'success': success,
                'new_adjustment': session_data['adjustment'],
                'feedback_count': session_data['feedback_count']
            }
        })

class ProgressiveContextRelaxation:
    """Implements progressive context relaxation for initial conversations"""
    
    def __init__(self, initial_stage=None, enable_initial_context_boost=None):
        """
        Initialize progressive context relaxation
        
        Args:
            initial_stage: Starting stage ('moderate', 'relaxed', 'broad', 'very_broad')
            enable_initial_context_boost: Whether to boost context retrieval for first few turns
        """
        # Load configuration
        config = EnhancedChatConfig.get_progressive_context_config()
        
        self.relaxation_stages = [
            {'name': 'moderate', 'top_k': 5, 'similarity_threshold': 0.7, 'context_weight': 0.8},
            {'name': 'relaxed', 'top_k': 8, 'similarity_threshold': 0.6, 'context_weight': 0.6},
            {'name': 'broad', 'top_k': 12, 'similarity_threshold': 0.5, 'context_weight': 0.4},
            {'name': 'very_broad', 'top_k': 15, 'similarity_threshold': 0.4, 'context_weight': 0.3}
        ]
        self.session_stages = {}
        self.stage_transition_threshold = config.get('stage_transition_threshold', 0.6)
        
        # Use provided parameters or fall back to configuration
        self.enable_initial_context_boost = enable_initial_context_boost if enable_initial_context_boost is not None else config.get('enable_initial_context_boost', True)
        self.initial_boost_turns = config.get('initial_boost_turns', 3)
        self.boost_top_k_increase = config.get('boost_top_k_increase', 2)
        self.boost_threshold_reduction = config.get('boost_threshold_reduction', 0.05)
        self.boost_context_weight_increase = config.get('boost_context_weight_increase', 0.1)
        self.max_top_k = config.get('max_top_k', 15)
        self.min_similarity_threshold = config.get('min_similarity_threshold', 0.3)
        self.max_context_weight = config.get('max_context_weight', 1.0)
        
        # Set initial stage based on configuration
        stage_names = [stage['name'] for stage in self.relaxation_stages]
        initial_stage = initial_stage or config.get('initial_stage', 'moderate')
        if initial_stage in stage_names:
            self.default_initial_stage = stage_names.index(initial_stage)
        else:
            self.default_initial_stage = 0  # Default to moderate
    
    def get_context_parameters(self, session_id: str, turn_number: int, 
                             previous_confidence: float = None) -> Dict[str, Any]:
        """Get context parameters based on progressive relaxation strategy"""
        correlation_id = get_correlation_id()
        
        # Determine current stage
        current_stage = self._determine_stage(session_id, turn_number, previous_confidence)
        
        # Get parameters for current stage
        stage_params = self.relaxation_stages[current_stage]
        
        # Apply initial context boost for first few turns
        top_k = stage_params['top_k']
        similarity_threshold = stage_params['similarity_threshold']
        context_weight = stage_params['context_weight']
        
        if self.enable_initial_context_boost and turn_number <= self.initial_boost_turns:
            # Boost context retrieval for initial conversations
            top_k = min(top_k + self.boost_top_k_increase, self.max_top_k)
            similarity_threshold = max(similarity_threshold - self.boost_threshold_reduction, self.min_similarity_threshold)
            context_weight = min(context_weight + self.boost_context_weight_increase, self.max_context_weight)
            
            logger.debug("Applied initial context boost", extra={
                'extra_fields': {
                    'event_type': 'initial_context_boost',
                    'session_id': session_id,
                    'turn_number': turn_number,
                    'original_top_k': stage_params['top_k'],
                    'boosted_top_k': top_k,
                    'original_threshold': stage_params['similarity_threshold'],
                    'boosted_threshold': similarity_threshold,
                    'correlation_id': correlation_id
                }
            })
        
        logger.debug("Progressive context relaxation parameters", extra={
            'extra_fields': {
                'event_type': 'context_relaxation_parameters',
                'session_id': session_id,
                'turn_number': turn_number,
                'current_stage': current_stage,
                'stage_name': stage_params['name'],
                'top_k': top_k,
                'similarity_threshold': similarity_threshold,
                'context_weight': context_weight,
                'initial_boost_applied': self.enable_initial_context_boost and turn_number <= 3,
                'correlation_id': correlation_id
            }
        })
        
        return {
            'top_k': top_k,
            'similarity_threshold': similarity_threshold,
            'context_weight': context_weight,
            'stage': current_stage,
            'stage_name': stage_params['name'],
            'initial_boost_applied': self.enable_initial_context_boost and turn_number <= 3
        }
    
    def _determine_stage(self, session_id: str, turn_number: int, 
                        previous_confidence: float) -> int:
        """Determine the appropriate relaxation stage"""
        # Initial stage for new sessions
        if session_id not in self.session_stages:
            self.session_stages[session_id] = {'current_stage': 0, 'turn_count': 0}
        
        session_data = self.session_stages[session_id]
        session_data['turn_count'] = turn_number
        
        # Progressive relaxation based on turn number - starting with moderate for better initial context
        if turn_number <= 3:
            stage = 0  # Moderate (was Strict) - better initial context retrieval
        elif turn_number <= 6:
            stage = 1  # Relaxed (was Moderate)
        elif turn_number <= 12:
            stage = 2  # Broad (was Relaxed)
        else:
            stage = 3  # Very Broad (was Broad)
        
        # Adjust based on previous confidence
        if previous_confidence is not None:
            if previous_confidence < self.stage_transition_threshold and session_data['current_stage'] > 0:
                # Move to more relaxed stage if confidence was low
                stage = min(stage + 1, len(self.relaxation_stages) - 1)
            elif previous_confidence > 0.8 and session_data['current_stage'] < len(self.relaxation_stages) - 1:
                # Move to stricter stage if confidence was high
                stage = max(stage - 1, 0)
        
        session_data['current_stage'] = stage
        return stage
    
    def update_stage_based_on_performance(self, session_id: str, confidence: float, 
                                        success: bool, user_feedback: str = None):
        """Update stage based on performance feedback"""
        if session_id not in self.session_stages:
            return
        
        session_data = self.session_stages[session_id]
        current_stage = session_data['current_stage']
        
        # Adjust stage based on performance
        if success and confidence > 0.8:
            # Good performance, can be more strict
            if current_stage > 0:
                session_data['current_stage'] = current_stage - 1
        elif not success or confidence < 0.5:
            # Poor performance, need more relaxation
            if current_stage < len(self.relaxation_stages) - 1:
                session_data['current_stage'] = current_stage + 1
        
        logger.debug("Updated progressive relaxation stage", extra={
            'extra_fields': {
                'event_type': 'stage_update',
                'session_id': session_id,
                'previous_stage': current_stage,
                'new_stage': session_data['current_stage'],
                'confidence': confidence,
                'success': success
            }
        })

class ConversationTurnTracker:
    """Tracks conversation turns and manages turn-based context"""
    
    def __init__(self):
        self.session_turns = {}
        self.turn_contexts = {}
        self.max_turn_history = 20
    
    def record_turn(self, session_id: str, question: str, response: str, 
                   confidence: float, context_used: List[Dict] = None):
        """Record a conversation turn with metadata"""
        if session_id not in self.session_turns:
            self.session_turns[session_id] = []
            self.turn_contexts[session_id] = []
        
        turn_data = {
            'turn_number': len(self.session_turns[session_id]) + 1,
            'timestamp': time.time(),
            'question': question,
            'response': response,
            'confidence': confidence,
            'context_used': context_used or [],
            'context_count': len(context_used) if context_used else 0
        }
        
        self.session_turns[session_id].append(turn_data)
        
        # Maintain history limit
        if len(self.session_turns[session_id]) > self.max_turn_history:
            self.session_turns[session_id] = self.session_turns[session_id][-self.max_turn_history:]
        
        logger.debug("Recorded conversation turn", extra={
            'extra_fields': {
                'event_type': 'turn_recorded',
                'session_id': session_id,
                'turn_number': turn_data['turn_number'],
                'confidence': confidence,
                'context_count': turn_data['context_count']
            }
        })
    
    def get_turn_context(self, session_id: str, turn_number: int = None) -> Dict[str, Any]:
        """Get context for a specific turn or current turn"""
        if session_id not in self.session_turns:
            return {}
        
        turns = self.session_turns[session_id]
        if not turns:
            return {}
        
        if turn_number is None:
            # Get current turn context
            current_turn = turns[-1]
        else:
            # Get specific turn context
            turn_index = turn_number - 1
            if 0 <= turn_index < len(turns):
                current_turn = turns[turn_index]
            else:
                return {}
        
        return {
            'turn_number': current_turn['turn_number'],
            'total_turns': len(turns),
            'previous_confidence': turns[-2]['confidence'] if len(turns) > 1 else None,
            'confidence_trend': self._calculate_confidence_trend(turns),
            'context_usage_pattern': self._analyze_context_usage(turns),
            'conversation_flow': self._analyze_conversation_flow(turns)
        }
    
    def _calculate_confidence_trend(self, turns: List[Dict]) -> str:
        """Calculate confidence trend over recent turns"""
        if len(turns) < 3:
            return "stable"
        
        recent_confidences = [turn['confidence'] for turn in turns[-3:]]
        if recent_confidences[0] < recent_confidences[1] < recent_confidences[2]:
            return "improving"
        elif recent_confidences[0] > recent_confidences[1] > recent_confidences[2]:
            return "declining"
        else:
            return "stable"
    
    def _analyze_context_usage(self, turns: List[Dict]) -> Dict[str, Any]:
        """Analyze context usage patterns"""
        if not turns:
            return {}
        
        context_counts = [turn['context_count'] for turn in turns]
        avg_context = sum(context_counts) / len(context_counts)
        
        return {
            'average_context_count': avg_context,
            'context_usage_trend': 'increasing' if len(context_counts) > 1 and context_counts[-1] > context_counts[0] else 'stable',
            'recent_context_count': context_counts[-1] if context_counts else 0
        }
    
    def _analyze_conversation_flow(self, turns: List[Dict]) -> Dict[str, Any]:
        """Analyze conversation flow patterns"""
        if len(turns) < 2:
            return {}
        
        question_lengths = [len(turn['question']) for turn in turns]
        response_lengths = [len(turn['response']) for turn in turns]
        
        return {
            'question_complexity_trend': 'increasing' if len(question_lengths) > 1 and question_lengths[-1] > question_lengths[0] else 'stable',
            'response_detail_trend': 'increasing' if len(response_lengths) > 1 and response_lengths[-1] > response_lengths[0] else 'stable',
            'conversation_depth': len(turns)
        }

class AdaptiveStrategySelector:
    """Adaptive strategy selector for conversation analysis"""
    
    def select_strategy(self, messages: List[Dict], conversation_complexity: float = None) -> ConversationAnalysisStrategy:
        """Select the most appropriate strategy based on conversation analysis"""
        correlation_id = get_correlation_id()
        
        if conversation_complexity is None:
            conversation_complexity = self._calculate_complexity(messages)
        
        conversation_type = self._classify_conversation(messages)
        
        logger.debug("Selecting conversation strategy", extra={
            'extra_fields': {
                'event_type': 'strategy_selection',
                'complexity_score': conversation_complexity,
                'conversation_type': conversation_type,
                'messages_count': len(messages),
                'correlation_id': correlation_id
            }
        })
        
        # Select strategy based on analysis
        if conversation_complexity > 0.7:
            strategy = MultiTurnConversationStrategy()
        elif conversation_type == "technical":
            strategy = EntityExtractionStrategy()
        elif conversation_type == "creative":
            strategy = TopicTrackingStrategy()
        else:
            strategy = MultiTurnConversationStrategy()
        
        logger.info("Strategy selected", extra={
            'extra_fields': {
                'event_type': 'strategy_selected',
                'strategy_name': strategy.get_strategy_name(),
                'complexity_score': conversation_complexity,
                'conversation_type': conversation_type,
                'correlation_id': correlation_id
            }
        })
        
        return strategy
    
    def _calculate_complexity(self, messages: List[Dict]) -> float:
        """Calculate conversation complexity score"""
        if len(messages) < 2:
            return 0.0
        
        complexity_factors = {
            'message_count': min(len(messages) / 10.0, 1.0),  # Normalize to 0-1
            'avg_message_length': 0.0,
            'entity_density': 0.0,
            'topic_diversity': 0.0
        }
        
        # Calculate average message length
        total_length = sum(len(msg.get('content', '')) for msg in messages)
        avg_length = total_length / len(messages)
        complexity_factors['avg_message_length'] = min(avg_length / 500.0, 1.0)  # Normalize
        
        # Calculate entity density
        all_content = ' '.join(msg.get('content', '') for msg in messages)
        entities = self._extract_entities(all_content)
        complexity_factors['entity_density'] = min(len(entities) / 20.0, 1.0)
        
        # Calculate topic diversity
        topics = self._extract_topics(all_content)
        complexity_factors['topic_diversity'] = min(len(topics) / 10.0, 1.0)
        
        # Weighted average
        weights = [0.3, 0.2, 0.25, 0.25]
        complexity_score = sum(factor * weight for factor, weight in zip(complexity_factors.values(), weights))
        
        return min(complexity_score, 1.0)
    
    def _classify_conversation(self, messages: List[Dict]) -> str:
        """Classify conversation type"""
        all_content = ' '.join(msg.get('content', '').lower() for msg in messages)
        
        # Technical indicators
        technical_terms = ['api', 'code', 'function', 'error', 'debug', 'technical', 'implementation', 'algorithm']
        technical_score = sum(1 for term in technical_terms if term in all_content)
        
        # Creative indicators
        creative_terms = ['creative', 'design', 'art', 'story', 'narrative', 'imagine', 'brainstorm', 'idea']
        creative_score = sum(1 for term in creative_terms if term in all_content)
        
        if technical_score > creative_score and technical_score > 2:
            return "technical"
        elif creative_score > technical_score and creative_score > 2:
            return "creative"
        else:
            return "general"
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        # Simple entity extraction - can be enhanced with NER
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return list(set(words))
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        # Simple topic extraction based on common words
        common_topics = ['python', 'api', 'database', 'security', 'performance', 'testing', 'deployment']
        found_topics = [topic for topic in common_topics if topic in text.lower()]
        return found_topics

class AdvancedMultiTurnStrategy(MultiTurnConversationStrategy):
    """Enhanced multi-turn strategy with better context understanding"""
    
    async def generate_enhanced_queries(self, question: str, context: Dict[str, Any]) -> List[str]:
        """Generate enhanced queries with better context understanding"""
        correlation_id = get_correlation_id()
        
        logger.debug("Generating advanced enhanced queries", extra={
            'extra_fields': {
                'event_type': 'advanced_query_generation_start',
                'original_question': question,
                'correlation_id': correlation_id
            }
        })
        
        queries = [question]  # Always include original question
        
        # Generate conversation-aware queries
        conversation_summary = self._generate_conversation_summary(context.get('messages', []))
        if conversation_summary:
            queries.append(f"{conversation_summary} {question}")
        
        # Generate intent-aware queries
        intent = self._detect_user_intent(context.get('messages', []))
        if intent:
            queries.append(f"{intent} {question}")
        
        # Generate context-specific queries
        context_entities = self._extract_context_entities(context.get('messages', []))
        for entity in context_entities[:3]:
            queries.append(f"{entity} {question}")
        
        # Generate follow-up queries based on conversation flow
        follow_up_context = self._extract_follow_up_context(context.get('messages', []))
        if follow_up_context:
            queries.append(f"{follow_up_context} {question}")
        
        # Add goal-oriented queries
        conversation_state = context.get("conversation_state", {})
        if isinstance(conversation_state, dict) and conversation_state.get("current_goal"):
            goal_query = f"{conversation_state['current_goal']} {question}"
            queries.append(goal_query)
        
        # Add phase-specific queries
        if isinstance(conversation_state, dict) and conversation_state.get("conversation_phase") != "planning":
            phase_query = f"{conversation_state.get('conversation_phase', 'general')} {question}"
            queries.append(phase_query)
        
        # Deduplicate and limit queries
        unique_queries = list(set(queries))
        final_queries = unique_queries[:10]  # Limit to 10 queries for performance
        
        logger.debug("Advanced enhanced query generation completed", extra={
            'extra_fields': {
                'event_type': 'advanced_query_generation_complete',
                'original_queries_count': len(queries),
                'unique_queries_count': len(unique_queries),
                'final_queries_count': len(final_queries),
                'correlation_id': correlation_id
            }
        })
        
        return final_queries
    
    def _generate_conversation_summary(self, messages: List[Dict]) -> str:
        """Generate a summary of the conversation context"""
        if len(messages) < 2:
            return ""
        
        # Extract key information from recent messages
        recent_messages = messages[-6:]  # Last 6 messages
        
        summary_parts = []
        
        # Extract main topics
        all_content = ' '.join(msg.get('content', '') for msg in recent_messages)
        topics = self._extract_topics(all_content)
        if topics:
            summary_parts.append(f"Topics: {', '.join(topics[:3])}")
        
        # Extract key entities
        entities = self._extract_entities(all_content)
        if entities:
            summary_parts.append(f"Entities: {', '.join(entities[:3])}")
        
        # Extract conversation flow indicators
        flow_indicators = self._extract_flow_indicators(recent_messages)
        if flow_indicators:
            summary_parts.append(f"Context: {', '.join(flow_indicators[:2])}")
        
        return " ".join(summary_parts) if summary_parts else ""
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        # Simple topic extraction based on common words
        common_topics = [
            'python', 'programming', 'code', 'algorithm', 'data', 'machine learning',
            'api', 'database', 'web', 'frontend', 'backend', 'testing', 'deployment',
            'security', 'performance', 'optimization', 'debugging', 'error handling'
        ]
        
        text_lower = text.lower()
        found_topics = [topic for topic in common_topics if topic in text_lower]
        
        # Also extract capitalized words as potential topics
        capitalized_words = re.findall(r'\b[A-Z][a-z]+\b', text)
        found_topics.extend(capitalized_words[:5])  # Limit to 5 additional topics
        
        return list(set(found_topics))[:8]  # Return unique topics, max 8
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        # Extract capitalized words and technical terms
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Add common technical entities
        technical_entities = [
            'Python', 'JavaScript', 'Java', 'C++', 'React', 'Angular', 'Vue',
            'Django', 'Flask', 'FastAPI', 'PostgreSQL', 'MongoDB', 'Redis',
            'Docker', 'Kubernetes', 'AWS', 'Azure', 'Git', 'GitHub'
        ]
        
        text_lower = text.lower()
        found_technical = [entity for entity in technical_entities if entity.lower() in text_lower]
        
        # Combine and deduplicate
        all_entities = entities + found_technical
        return list(set(all_entities))[:10]  # Return unique entities, max 10
    
    def _detect_user_intent(self, messages: List[Dict]) -> str:
        """Detect user intent from conversation"""
        if not messages:
            return ""
        
        # Look for intent indicators in recent user messages
        intent_indicators = {
            'clarification': ['clarify', 'explain', 'what do you mean', 'can you elaborate'],
            'comparison': ['compare', 'difference', 'versus', 'vs', 'better'],
            'implementation': ['how to', 'implement', 'code', 'example', 'tutorial'],
            'troubleshooting': ['error', 'problem', 'issue', 'fix', 'debug', 'not working'],
            'evaluation': ['review', 'assess', 'evaluate', 'opinion', 'thoughts']
        }
        
        recent_user_messages = [msg.get('content', '').lower() for msg in messages if msg.get('role') == 'user'][-3:]
        
        for intent, indicators in intent_indicators.items():
            for message in recent_user_messages:
                if any(indicator in message for indicator in indicators):
                    return intent
        
        return ""
    
    def _extract_context_entities(self, messages: List[Dict]) -> List[str]:
        """Extract context-specific entities from conversation"""
        if not messages:
            return []
        
        all_content = ' '.join(msg.get('content', '') for msg in messages)
        
        # Extract technical entities
        technical_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', all_content)
        
        # Extract domain-specific terms
        domain_terms = re.findall(r'\b\w+(?:\.\w+)*\b', all_content)
        
        # Combine and filter
        entities = technical_entities + domain_terms
        entities = [entity for entity in entities if len(entity) > 2 and entity.lower() not in ['the', 'and', 'for', 'with']]
        
        return list(set(entities))[:5]  # Return top 5 unique entities
    
    def _extract_follow_up_context(self, messages: List[Dict]) -> str:
        """Extract follow-up context from conversation flow"""
        if len(messages) < 4:
            return ""
        
        # Look for follow-up indicators
        follow_up_indicators = ['also', 'additionally', 'furthermore', 'moreover', 'besides', 'in addition']
        
        recent_messages = messages[-4:]
        
        for msg in recent_messages:
            if msg.get('role') == 'user':
                content = msg.get('content', '').lower()
                for indicator in follow_up_indicators:
                    if indicator in content:
                        # Extract the part after the indicator
                        parts = content.split(indicator, 1)
                        if len(parts) > 1:
                            return parts[1].strip()
        
        return ""
    
    def _extract_flow_indicators(self, messages: List[Dict]) -> List[str]:
        """Extract conversation flow indicators"""
        indicators = []
        
        for msg in messages:
            content = msg.get('content', '').lower()
            
            # Look for flow indicators
            if any(word in content for word in ['first', 'then', 'next', 'finally']):
                indicators.append('sequential')
            if any(word in content for word in ['however', 'but', 'although', 'despite']):
                indicators.append('contrast')
            if any(word in content for word in ['because', 'since', 'therefore', 'thus']):
                indicators.append('causal')
            if any(word in content for word in ['for example', 'such as', 'like']):
                indicators.append('exemplification')
        
        return list(set(indicators))  # Return unique indicators

class ConversationMemory:
    """Manages conversation memory and learning"""
    
    def __init__(self):
        self.conversation_memory = {}
        self.learning_patterns = {}
    
    def store_conversation_context(self, session_id: str, context: Dict[str, Any]):
        """Store conversation context for a session"""
        correlation_id = get_correlation_id()
        
        logger.debug("Storing conversation context", extra={
            'extra_fields': {
                'event_type': 'conversation_context_stored',
                'session_id': session_id,
                'context_keys': list(context.keys()),
                'correlation_id': correlation_id
            }
        })
        
        self.conversation_memory[session_id] = {
            'context': context,
            'timestamp': __import__('time').time(),
            'access_count': 0
        }
    
    def retrieve_conversation_context(self, session_id: str) -> Dict[str, Any]:
        """Retrieve conversation context for a session"""
        correlation_id = get_correlation_id()
        
        if session_id in self.conversation_memory:
            memory_entry = self.conversation_memory[session_id]
            memory_entry['access_count'] += 1
            
            logger.debug("Retrieved conversation context", extra={
                'extra_fields': {
                    'event_type': 'conversation_context_retrieved',
                    'session_id': session_id,
                    'access_count': memory_entry['access_count'],
                    'correlation_id': correlation_id
                }
            })
            
            return memory_entry['context']
        
        return {}
    
    def update_conversation_learning(self, session_id: str, feedback: Dict[str, Any]):
        """Update conversation patterns based on feedback"""
        correlation_id = get_correlation_id()
        
        logger.debug("Updating conversation learning", extra={
            'extra_fields': {
                'event_type': 'conversation_learning_updated',
                'session_id': session_id,
                'feedback_keys': list(feedback.keys()),
                'correlation_id': correlation_id
            }
        })
        
        if session_id not in self.learning_patterns:
            self.learning_patterns[session_id] = []
        
        self.learning_patterns[session_id].append({
            'feedback': feedback,
            'timestamp': __import__('time').time()
        })
    
    def get_session_patterns(self, session_id: str) -> List[Dict[str, Any]]:
        """Get learning patterns for a session"""
        return self.learning_patterns.get(session_id, [])
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up old conversation sessions"""
        current_time = __import__('time').time()
        max_age_seconds = max_age_hours * 3600
        
        sessions_to_remove = []
        for session_id, memory_entry in self.conversation_memory.items():
            if current_time - memory_entry['timestamp'] > max_age_seconds:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.conversation_memory[session_id]
            if session_id in self.learning_patterns:
                del self.learning_patterns[session_id]

class EnhancedContextAwareRAGService:
    """Enhanced context-aware RAG service with multi-turn conversation support"""
    
    def __init__(self,
                 rag_service: Optional[RAGService] = None,
                 embedding_provider: Optional[EmbeddingProvider] = None,
                 llm_provider: Optional[LLMProvider] = None,
                 vector_store_provider: Optional[VectorStoreProvider] = None):
        """Initialize enhanced context-aware RAG service"""
        self.context_aware_service = ContextAwareRAGService(
            rag_service=rag_service,
            embedding_provider=embedding_provider,
            llm_provider=llm_provider,
            vector_store_provider=vector_store_provider
        )
        self.rag_service = rag_service or self.context_aware_service.rag_service
        self.llm_provider = llm_provider or self.context_aware_service.llm_provider
        self.strategy_selector = AdaptiveStrategySelector()
        self.conversation_memory = ConversationMemory()
        self.confidence_manager = AdaptiveConfidenceManager()
        self.context_relaxation = ProgressiveContextRelaxation()  # Uses configuration defaults
        self.turn_tracker = ConversationTurnTracker()
        
        logger.info("Enhanced context-aware RAG service initialized", extra={
            'extra_fields': {
                'event_type': 'enhanced_context_aware_rag_service_initialization',
                'rag_service_class': type(self.rag_service).__name__
            }
        })
    
    async def ask_question_with_context_and_conversation(
        self, 
        question: str, 
        system_message: str = "",
        conversation_history: List[Dict] = None,
        session_id: str = None,
        top_k: int = None,
        context_filter: Optional[DocumentContext] = None
    ) -> Dict[str, Any]:
        """Ask question with both context awareness and conversation support"""
        correlation_id = get_correlation_id()
        
        logger.info("Enhanced context-aware question processing", extra={
            'extra_fields': {
                'event_type': 'enhanced_context_aware_question_start',
                'question_length': len(question),
                'conversation_history_length': len(conversation_history) if conversation_history else 0,
                'session_id': session_id,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Get turn information and context
            turn_number = 1
            previous_confidence = None
            if session_id:
                turn_context = self.turn_tracker.get_turn_context(session_id)
                turn_number = turn_context.get('turn_number', 1)
                previous_confidence = turn_context.get('previous_confidence')
            
            # Retrieve conversation context from memory if available
            conversation_context = {}
            if session_id:
                conversation_context = self.conversation_memory.retrieve_conversation_context(session_id)
            
            # Analyze conversation if history is provided
            strategy = None
            conversation_complexity = 0.0
            if conversation_history:
                # Select appropriate strategy
                strategy = self.strategy_selector.select_strategy(conversation_history)
                conversation_complexity = self.strategy_selector._calculate_complexity(conversation_history)
                
                # Analyze conversation
                analysis_result = await strategy.analyze_conversation(conversation_history)
                conversation_context.update(analysis_result)
                
                # Store updated context
                if session_id:
                    self.conversation_memory.store_conversation_context(session_id, conversation_context)
            
            # Get progressive context relaxation parameters
            context_params = self.context_relaxation.get_context_parameters(
                session_id or "default", turn_number, previous_confidence
            )
            
            # Calculate adaptive confidence threshold
            context_quality = len(conversation_context) / 10.0  # Simple quality metric
            adaptive_threshold = self.confidence_manager.get_adaptive_threshold(
                session_id or "default", turn_number, context_quality, conversation_complexity
            )
            
            # Generate enhanced queries using advanced strategy
            advanced_strategy = AdvancedMultiTurnStrategy()
            enhanced_queries = await advanced_strategy.generate_enhanced_queries(question, conversation_context)
            
            # Apply context filtering to each query
            all_results = []
            query_failures = 0
            total_queries = len(enhanced_queries)
            
            for query in enhanced_queries:
                try:
                    # Use progressive context relaxation parameters
                    effective_top_k = top_k or context_params['top_k']
                    
                    # Use context-aware RAG for each query
                    query_result = await self.context_aware_service.ask_question_with_context(
                        question=query,
                        system_message=system_message,
                        top_k=effective_top_k,
                        context_filter=context_filter
                    )
                    
                    if query_result.get('success') and query_result.get('sources'):
                        sources = query_result['sources']
                        
                        # Apply additional context filtering if specified
                        if context_filter:
                            filtered_sources = ContextFilter.filter_documents_by_context(sources, context_filter)
                            all_results.extend(filtered_sources)
                        else:
                            all_results.extend(sources)
                    
                except Exception as e:
                    query_failures += 1
                    logger.warning(f"Query failed: {query}", extra={
                        'extra_fields': {
                            'event_type': 'enhanced_query_failed',
                            'query': query,
                            'error': str(e),
                            'correlation_id': correlation_id
                        }
                    })
                    continue
            
            # If all queries failed due to exceptions, return error
            if query_failures == total_queries and total_queries > 0:
                logger.error("All queries failed due to exceptions", extra={
                    'extra_fields': {
                        'event_type': 'all_queries_failed',
                        'total_queries': total_queries,
                        'query_failures': query_failures,
                        'correlation_id': correlation_id
                    }
                })
                
                return {
                    "success": False,
                    "answer": "Error processing question: All queries failed due to system errors",
                    "sources": [],
                    "question": question,
                    "enhanced_queries": enhanced_queries,
                    "conversation_context": conversation_context,
                    "strategy_used": "error",
                    "session_id": session_id
                }
            
            # Deduplicate and rank results
            unique_results = self._deduplicate_results(all_results)
            
            # Generate final response
            if unique_results:
                # Use the best results to generate response
                best_sources = unique_results[:5]  # Use top 5 sources
                
                # Create context text from sources
                context_parts = []
                for source in best_sources:
                    content = source.get('content', '')
                    source_name = source.get('source', 'Unknown')
                    context_parts.append(f"Source: {source_name}\nContent: {content}")
                
                context_text = "\n\n".join(context_parts)
                
                # Generate response using LLM
                enhanced_system_message = f"{system_message}\n\nYou have access to the following relevant information:\n{context_text}\n\nUse this information to provide accurate and helpful responses."
                
                messages = [
                    {"role": "system", "content": enhanced_system_message},
                    {"role": "user", "content": question}
                ]
                
                answer = await self.llm_provider.call_llm(messages)
                
                # Calculate confidence score based on context quality and source relevance
                confidence_score = self._calculate_confidence_score(best_sources, context_params, adaptive_threshold)
                
                # Record turn in tracker
                if session_id:
                    self.turn_tracker.record_turn(
                        session_id=session_id,
                        question=question,
                        response=answer,
                        confidence=confidence_score,
                        context_used=best_sources
                    )
                
                # Update adaptive components based on performance
                if session_id:
                    self.confidence_manager.update_session_threshold(
                        session_id, confidence_score, adaptive_threshold, True
                    )
                    self.context_relaxation.update_stage_based_on_performance(
                        session_id, confidence_score, True
                    )
                
                result = {
                    "success": True,
                    "answer": answer,
                    "sources": best_sources,
                    "question": question,
                    "enhanced_queries": enhanced_queries,
                    "conversation_context": conversation_context,
                    "strategy_used": strategy.get_strategy_name() if strategy else "none",
                    "session_id": session_id,
                    "confidence_score": confidence_score,
                    "adaptive_threshold": adaptive_threshold,
                    "context_params": context_params,
                    "turn_number": turn_number
                }
            else:
                # No results found, fallback to LLM-only
                messages = [
                    {"role": "system", "content": system_message or "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ]
                
                answer = await self.llm_provider.call_llm(messages)
                
                # Calculate confidence score for fallback (lower confidence)
                fallback_confidence = adaptive_threshold * 0.5  # Lower confidence for fallback
                
                # Record turn in tracker
                if session_id:
                    self.turn_tracker.record_turn(
                        session_id=session_id,
                        question=question,
                        response=answer,
                        confidence=fallback_confidence,
                        context_used=[]
                    )
                
                # Update adaptive components based on fallback performance
                if session_id:
                    self.confidence_manager.update_session_threshold(
                        session_id, fallback_confidence, adaptive_threshold, False
                    )
                    self.context_relaxation.update_stage_based_on_performance(
                        session_id, fallback_confidence, False
                    )
                
                result = {
                    "success": True,
                    "answer": answer,
                    "sources": [],
                    "question": question,
                    "enhanced_queries": enhanced_queries,
                    "conversation_context": conversation_context,
                    "strategy_used": strategy.get_strategy_name() if strategy else "none",
                    "session_id": session_id,
                    "fallback_used": True,
                    "confidence_score": fallback_confidence,
                    "adaptive_threshold": adaptive_threshold,
                    "context_params": context_params,
                    "turn_number": turn_number
                }
            
            logger.info("Enhanced context-aware question processing completed", extra={
                'extra_fields': {
                    'event_type': 'enhanced_context_aware_question_complete',
                    'enhanced_queries_count': len(enhanced_queries),
                    'sources_found': len(unique_results),
                    'strategy_used': result.get('strategy_used'),
                    'correlation_id': correlation_id
                }
            })
            
            return result
                
        except Exception as e:
            logger.error("Error in enhanced context-aware question processing", extra={
                'extra_fields': {
                    'event_type': 'enhanced_context_aware_question_error',
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
                "enhanced_queries": [],
                "conversation_context": {},
                "strategy_used": "error",
                "session_id": session_id
            }
    
    def _calculate_confidence_score(self, sources: List[Dict[str, Any]], 
                                  context_params: Dict[str, Any], 
                                  adaptive_threshold: float) -> float:
        """Calculate confidence score based on source quality and context parameters"""
        if not sources:
            return 0.0
        
        # Base confidence from source count and quality
        source_count = len(sources)
        base_confidence = min(source_count / 5.0, 1.0)  # Normalize to 0-1
        
        # Source quality factors
        quality_factors = []
        for source in sources:
            content = source.get('content', '')
            # Content length factor
            length_factor = min(len(content) / 500.0, 1.0)
            # Source relevance factor (simple heuristic)
            relevance_factor = 0.8 if source.get('source') else 0.6
            quality_factors.append((length_factor + relevance_factor) / 2.0)
        
        avg_quality = sum(quality_factors) / len(quality_factors) if quality_factors else 0.0
        
        # Context parameter adjustment
        context_weight = context_params.get('context_weight', 1.0)
        similarity_threshold = context_params.get('similarity_threshold', 0.7)
        
        # Calculate final confidence
        confidence = (base_confidence * 0.4 + avg_quality * 0.6) * context_weight
        
        # Apply similarity threshold influence
        if similarity_threshold > 0.8:
            confidence *= 1.1  # Boost for strict thresholds
        elif similarity_threshold < 0.6:
            confidence *= 0.9  # Reduce for relaxed thresholds
        
        # Clamp to valid range
        confidence = max(0.0, min(1.0, confidence))
        
        logger.debug("Calculated confidence score", extra={
            'extra_fields': {
                'event_type': 'confidence_calculation',
                'source_count': source_count,
                'base_confidence': base_confidence,
                'avg_quality': avg_quality,
                'context_weight': context_weight,
                'similarity_threshold': similarity_threshold,
                'final_confidence': confidence
            }
        })
        
        return confidence
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate results based on content"""
        seen_contents = set()
        unique_results = []
        
        for result in results:
            content = result.get('content', '')
            content_hash = hash(content)
            
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_results.append(result)
        
        # Sort by score if available
        unique_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        return unique_results
    
    # Delegate other methods to the context-aware service
    async def add_document_with_context(self, request: DocumentUploadRequest) -> Dict[str, Any]:
        return await self.context_aware_service.add_document_with_context(request)
    
    async def add_text_with_context(self, request: TextUploadRequest) -> Dict[str, Any]:
        return await self.context_aware_service.add_text_with_context(request)
    
    async def get_stats(self) -> Dict[str, Any]:
        return await self.context_aware_service.get_stats()
    
    async def clear_knowledge_base(self) -> Dict[str, Any]:
        return await self.context_aware_service.clear_knowledge_base()
    
    def get_conversation_memory(self) -> ConversationMemory:
        return self.conversation_memory
