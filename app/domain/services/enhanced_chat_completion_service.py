"""
Enhanced Chat Completion Service using Strategy Pattern and Plugin Architecture.
Maintains external interface compatibility while providing extensible functionality.
"""

from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from app.domain.models.requests import ChatCompletionRequest, ChatMessage
from app.domain.models.responses import ChatCompletionResponse
from app.domain.services.rag_service import RAGService
from app.core.logging_config import get_logger, get_correlation_id
from app.core.logging_helpers import log_extra
import asyncio
from collections import defaultdict
from app.core.token_config import token_config_service
from app.core.config import Config
import re

logger = get_logger(__name__)

class ProcessingPriority(Enum):
    """Processing priority levels for plugins"""
    HIGH = 1
    NORMAL = 2
    LOW = 3

@dataclass
class ConversationState:
    """Track conversation state and goals for multi-turn conversations"""
    current_goal: str = ""
    conversation_phase: str = "planning"  # "planning", "drafting", "reviewing", "finalizing"
    key_entities: List[str] = None
    constraints: List[str] = None
    progress_markers: List[str] = None
    next_steps: List[str] = None
    conversation_history: List[str] = None
    
    def __post_init__(self):
        if self.key_entities is None:
            self.key_entities = []
        if self.constraints is None:
            self.constraints = []
        if self.progress_markers is None:
            self.progress_markers = []
        if self.next_steps is None:
            self.next_steps = []
        if self.conversation_history is None:
            self.conversation_history = []

@dataclass
class ProcessingContext:
    """Context object passed between plugins during processing"""
    request: ChatCompletionRequest
    strategy: Optional[str] = None
    conversation_context: Optional[Dict[str, Any]] = None
    enhanced_queries: Optional[List[str]] = None
    rag_results: Optional[List[Dict[str, Any]]] = None
    response_data: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    conversation_state: Optional[ConversationState] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.conversation_context is None:
            self.conversation_context = {}
        if self.conversation_state is None:
            self.conversation_state = ConversationState()

class ConversationAnalysisStrategy(ABC):
    """Abstract base class for conversation analysis strategies"""
    
    @abstractmethod
    async def analyze_conversation(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """Analyze conversation and extract context"""
        pass
    
    @abstractmethod
    async def generate_enhanced_queries(self, question: str, context: Dict[str, Any]) -> List[str]:
        """Generate enhanced queries based on conversation context"""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy"""
        pass

class MultiTurnConversationStrategy(ConversationAnalysisStrategy):
    """Enhanced strategy for multi-turn conversations with goal tracking"""
    
    def get_strategy_name(self) -> str:
        return "multi_turn_conversation"
    
    async def analyze_conversation(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """Analyze conversation to extract topics, entities, and conversation state"""
        correlation_id = get_correlation_id()
        
        logger.debug(
            "Starting multi-turn conversation analysis",
            extra=log_extra('multi_turn_strategy_analysis_start', strategy=self.get_strategy_name(), messages_count=len(messages))
        )
        
        topics = []
        entities = []
        context_clues = []
        persona_info = {}
        conversation_state = ConversationState()
        
        # Extract topics and entities from all messages
        for message in messages:
            if message.role == "system":
                topics.append("system_instruction")
                context_clues.append(message.content)
                persona_info = self._extract_persona_info(message.content)
                
            elif message.role == "user":
                # Enhanced topic and entity extraction for short messages
                topics.extend(self._extract_topics_enhanced(message.content))
                entities.extend(self._extract_entities_enhanced(message.content))
                
            elif message.role == "assistant":
                entities.extend(self._extract_entities_enhanced(message.content))
        
        # Analyze conversation state and goals
        conversation_state = self._analyze_conversation_state(messages)
        
        result = {
            "topics": list(set(topics)),
            "entities": list(set(entities)),
            "context_clues": context_clues,
            "conversation_length": len(messages),
            "last_user_message": next((msg.content for msg in reversed(messages) if msg.role == "user"), ""),
            "persona_info": persona_info,
            "conversation_state": conversation_state
        }
        
        logger.debug(
            "Multi-turn conversation analysis completed",
            extra=log_extra(
                'multi_turn_strategy_analysis_complete',
                strategy=self.get_strategy_name(),
                topics_count=len(result['topics']),
                entities_count=len(result['entities']),
                goal_detected=bool(conversation_state.current_goal),
                phase=conversation_state.conversation_phase,
            )
        )
        
        return result
    
    async def generate_enhanced_queries(self, question: str, context: Dict[str, Any]) -> List[str]:
        """Generate enhanced queries including condensed and summary queries with short message support"""
        correlation_id = get_correlation_id()
        
        logger.debug("Starting multi-turn enhanced query generation", extra={
            'extra_fields': {
                'event_type': 'multi_turn_strategy_query_generation_start',
                'strategy': self.get_strategy_name(),
                'original_question': question,
                'correlation_id': correlation_id
            }
        })
        
        queries = [question]  # Always include original question
        
        # Enhanced handling for short questions (one-word responses)
        if len(question.split()) <= 2:
            # Generate context-aware expansion for short messages
            expanded_queries = self._expand_short_question(question, context)
            queries.extend(expanded_queries)
            
            logger.debug("Enhanced short question processing", extra={
                'extra_fields': {
                    'event_type': 'short_question_expansion',
                    'original_question': question,
                    'expanded_queries_count': len(expanded_queries),
                    'correlation_id': correlation_id
                }
            })
        
        # Get conversation state
        conversation_state = context.get("conversation_state", ConversationState())
        
        # Generate condensed standalone query
        if context.get("messages"):
            condensed_query = self._condense_to_standalone_question(
                context["messages"], max_turns=5
            )
            if condensed_query and condensed_query != question:
                queries.append(condensed_query)
        
        # Generate summary query
        if context.get("messages"):
            summary_query = self._summarize_recent_context(
                context["messages"], max_turns=5
            )
            if summary_query:
                queries.append(summary_query)
        
        # Add goal-oriented queries
        if conversation_state.current_goal:
            goal_query = f"{conversation_state.current_goal} {question}"
            queries.append(goal_query)
        
        # Add phase-specific queries
        if conversation_state.conversation_phase != "planning":
            phase_query = f"{conversation_state.conversation_phase} {question}"
            queries.append(phase_query)
        
        # Add entity-based queries
        for entity in context.get("entities", [])[:3]:
            queries.append(f"{entity} {question}")
        
        # Add topic-based queries
        for topic in context.get("topics", [])[:2]:
            if topic != "system_instruction":
                queries.append(f"{topic} {question}")
        
        # Deduplicate and limit queries
        unique_queries = list(set(queries))
        final_queries = unique_queries[:10]  # Increased limit for better context coverage
        
        logger.debug("Multi-turn enhanced query generation completed", extra={
            'extra_fields': {
                'event_type': 'multi_turn_strategy_query_generation_complete',
                'strategy': self.get_strategy_name(),
                'original_queries_count': len(queries),
                'unique_queries_count': len(unique_queries),
                'final_queries_count': len(final_queries),
                'condensed_query_generated': any('condensed' in q for q in final_queries),
                'summary_query_generated': any('summary' in q for q in final_queries),
                'goal_query_generated': bool(conversation_state.current_goal),
                'short_question_expanded': len(question.split()) <= 2,
                'correlation_id': correlation_id
            }
        })
        
        return final_queries
    
    def _condense_to_standalone_question(self, messages: List[ChatMessage], max_turns: int = 5) -> str:
        """Generate a standalone question from recent conversation turns with enhanced short message support"""
        if len(messages) < 2:
            return ""
        
        # Get recent turns (last max_turns * 2 to account for user/assistant pairs)
        recent_messages = messages[-max_turns * 2:]
        
        # Enhanced extraction with short message support
        entities = []
        topics = []
        constraints = []
        goal_indicators = []
        context_clues = []
        
        for message in recent_messages:
            if message.role == "user":
                # Enhanced entity extraction for short messages
                entities.extend(self._extract_entities_enhanced(message.content))
                topics.extend(self._extract_topics_enhanced(message.content))
                constraints.extend(self._extract_constraints(message.content))
                goal_indicators.extend(self._extract_goal_indicators(message.content))
                context_clues.extend(self._extract_context_clues(message.content))
        
        # Get the last user message
        last_user_message = ""
        for message in reversed(recent_messages):
            if message.role == "user":
                last_user_message = message.content
                break
        
        if not last_user_message:
            return ""
        
        # Enhanced query building with context preservation
        condensed_parts = []
        
        # Add context from previous messages if current message is short
        if len(last_user_message.split()) <= 2:
            # Include more context from previous messages
            condensed_parts.extend(self._extract_context_from_history(recent_messages))
        
        # Add key entities (including short ones)
        if entities:
            condensed_parts.extend(entities[:3])
        
        # Add key topics
        if topics:
            condensed_parts.extend(topics[:2])
        
        # Add goal indicators
        if goal_indicators:
            condensed_parts.extend(goal_indicators[:2])
        
        # Add context clues
        if context_clues:
            condensed_parts.extend(context_clues[:2])
        
        # Add the core question
        condensed_parts.append(last_user_message)
        
        # Join and clean up
        condensed_query = " ".join(condensed_parts)
        condensed_query = re.sub(r'\s+', ' ', condensed_query).strip()
        
        return condensed_query
    
    def _expand_short_question(self, question: str, context: Dict[str, Any]) -> List[str]:
        """Expand short questions with context from conversation"""
        expanded = []
        
        # Get recent context
        recent_entities = context.get("entities", [])[:3]
        recent_topics = context.get("topics", [])[:2]
        conversation_state = context.get("conversation_state", {})
        
        # Expand based on question type
        question_lower = question.lower()
        
        if question_lower in ["yes", "no"]:
            # For yes/no questions, add context from previous question
            if context.get("messages"):
                prev_question = self._get_previous_question(context["messages"])
                if prev_question:
                    expanded.append(f"{prev_question} {question}")
        
        elif question_lower in ["why", "how", "what", "when", "where"]:
            # For question words, add context from conversation
            for entity in recent_entities:
                expanded.append(f"{question} {entity}")
            for topic in recent_topics:
                if topic != "system_instruction":
                    expanded.append(f"{question} {topic}")
        
        else:
            # For other short messages, add general context
            for entity in recent_entities:
                expanded.append(f"{entity} {question}")
        
        return expanded
    
    def _get_previous_question(self, messages: List[ChatMessage]) -> str:
        """Get the previous assistant question that the user is responding to"""
        # Look for the most recent assistant message that contains a question
        for message in reversed(messages):
            if message.role == "assistant":
                content = message.content
                # Check if it contains question indicators
                if any(indicator in content.lower() for indicator in ["?", "what", "how", "why", "when", "where", "which", "do you", "can you", "would you"]):
                    # Extract the question part
                    sentences = content.split('.')
                    for sentence in sentences:
                        if any(indicator in sentence.lower() for indicator in ["?", "what", "how", "why", "when", "where", "which", "do you", "can you", "would you"]):
                            return sentence.strip()
        return ""
    
    def _extract_context_from_history(self, messages: List[ChatMessage]) -> List[str]:
        """Extract context from conversation history for short messages"""
        context_parts = []
        
        # Get recent user messages (excluding the current one)
        recent_user_messages = []
        for message in messages[:-1]:  # Exclude the last message
            if message.role == "user":
                recent_user_messages.append(message.content)
        
        # Extract key terms from recent messages
        for message in recent_user_messages[-3:]:  # Last 3 user messages
            # Extract entities and topics
            entities = self._extract_entities_enhanced(message)
            topics = self._extract_topics_enhanced(message)
            
            context_parts.extend(entities[:2])
            context_parts.extend(topics[:1])
        
        return context_parts
    
    def _extract_entities_enhanced(self, text: str) -> List[str]:
        """Enhanced entity extraction that handles short messages"""
        entities = []
        words = text.split()
        
        # Handle short words that might be entities
        short_entities = ["api", "ai", "ml", "ui", "ux", "db", "sql", "js", "ts", "py", "go", "java", "rag", "llm"]
        
        for word in words:
            word_lower = word.lower()
            
            # Check for short technical entities
            if word_lower in short_entities:
                entities.append(word.upper())
            # Check for capitalized words (including short ones)
            elif word[0].isupper() and len(word) >= 2:
                entities.append(word)
            # Check for acronyms
            elif word.isupper() and len(word) >= 2:
                entities.append(word)
            # Check for technical terms
            elif word_lower in ["python", "javascript", "typescript", "react", "angular", "vue", "node", "express", "django", "flask"]:
                entities.append(word)
        
        return entities
    
    def _extract_topics_enhanced(self, text: str) -> List[str]:
        """Enhanced topic extraction that handles short messages"""
        topics = []
        text_lower = text.lower()
        
        # Enhanced topic keywords including short terms
        topic_keywords = [
            "compliance", "risk", "policy", "document", "requirement",
            "implementation", "migration", "assessment", "analysis",
            "api", "rag", "llm", "ai", "ml", "data", "code", "test",
            "deploy", "config", "setup", "install", "error", "bug",
            "fix", "help", "guide", "tutorial", "example"
        ]
        
        for topic in topic_keywords:
            if topic in text_lower:
                topics.append(topic)
        
        return topics
    
    def _extract_context_clues(self, text: str) -> List[str]:
        """Extract context clues from text"""
        clues = []
        text_lower = text.lower()
        
        # Context clue indicators
        clue_indicators = [
            "about", "regarding", "concerning", "related to", "in terms of",
            "specifically", "particularly", "especially", "mainly", "primarily",
            "focus on", "concentrate on", "deal with", "handle", "manage"
        ]
        
        for indicator in clue_indicators:
            if indicator in text_lower:
                clues.append(indicator)
        
        return clues
    
    def _summarize_recent_context(self, messages: List[ChatMessage], max_turns: int = 5) -> str:
        """Generate a summary query from recent conversation context with enhanced short message support"""
        if len(messages) < 2:
            return ""
        
        # Use adaptive context window based on message complexity
        context_window = self._calculate_adaptive_context_window(messages, max_turns)
        recent_messages = messages[-context_window:]
        
        # Extract conversation elements with weighting
        goals = []
        entities = []
        actions = []
        context_clues = []
        
        # Weight recent messages more heavily
        for i, message in enumerate(recent_messages):
            weight = 1.0 + (i / len(recent_messages))  # Recent messages get higher weight
            
            if message.role == "user":
                goals.extend(self._extract_goals(message.content))
                entities.extend(self._extract_entities_enhanced(message.content))
                actions.extend(self._extract_actions(message.content))
                context_clues.extend(self._extract_context_clues(message.content))
        
        # Build enhanced summary query
        summary_parts = []
        
        if goals:
            summary_parts.append(f"Goal: {goals[0]}")
        
        if entities:
            summary_parts.append(f"Entities: {', '.join(entities[:3])}")
        
        if actions:
            summary_parts.append(f"Actions: {', '.join(actions[:2])}")
        
        if context_clues:
            summary_parts.append(f"Context: {', '.join(context_clues[:2])}")
        
        if summary_parts:
            summary_query = " ".join(summary_parts)
            return summary_query
        
        return ""
    
    def _calculate_adaptive_context_window(self, messages: List[ChatMessage], max_turns: int) -> int:
        """Calculate adaptive context window based on message complexity"""
        if len(messages) < 4:
            return len(messages)
        
        # Check if the last message is short
        last_message = messages[-1].content if messages else ""
        is_short_message = len(last_message.split()) <= 2
        
        if is_short_message:
            # Use larger context window for short messages
            return min(max_turns * 3, len(messages))
        else:
            # Use standard context window for longer messages
            return max_turns * 2
    
    def _analyze_conversation_state(self, messages: List[ChatMessage]) -> ConversationState:
        """Analyze conversation to determine state, goals, and progress with enhanced short message support"""
        state = ConversationState()
        
        # Extract conversation history
        for message in messages:
            if message.role in ["user", "assistant"]:
                state.conversation_history.append(message.content)
        
        # Enhanced goal detection with pattern inference
        for message in messages:
            if message.role == "user":
                goals = self._extract_goals(message.content)
                if goals:
                    state.current_goal = goals[0]
                    break
        
        # If no explicit goal found, infer from conversation pattern
        if not state.current_goal:
            state.current_goal = self._infer_goal_from_pattern(messages)
        
        # Enhanced conversation phase detection
        state.conversation_phase = self._detect_conversation_phase(messages)
        
        # Extract key entities with short message support
        for message in messages:
            if message.role in ["user", "assistant"]:
                entities = self._extract_entities_enhanced(message.content)
                state.key_entities.extend(entities)
        
        # Remove duplicates and limit
        state.key_entities = list(set(state.key_entities))[:10]
        
        # Extract constraints
        for message in messages:
            if message.role == "user":
                constraints = self._extract_constraints(message.content)
                state.constraints.extend(constraints)
        
        state.constraints = list(set(state.constraints))[:5]
        
        return state
    
    def _infer_goal_from_pattern(self, messages: List[ChatMessage]) -> str:
        """Infer conversation goal from message patterns"""
        # Analyze message patterns to infer goal
        user_messages = [msg.content for msg in messages if msg.role == "user"]
        
        # Simple pattern matching for common goals
        if any("help" in msg.lower() for msg in user_messages):
            return "seeking_help"
        elif any("explain" in msg.lower() for msg in user_messages):
            return "explanation_request"
        elif any("how to" in msg.lower() for msg in user_messages):
            return "how_to_guidance"
        elif any("problem" in msg.lower() or "error" in msg.lower() for msg in user_messages):
            return "problem_solving"
        elif any("yes" in msg.lower() or "no" in msg.lower() for msg in user_messages):
            return "confirmation_request"
        else:
            return "general_inquiry"
    
    def _detect_conversation_phase(self, messages: List[ChatMessage]) -> str:
        """Enhanced conversation phase detection"""
        phase_indicators = {
            "planning": ["plan", "structure", "outline", "framework", "approach"],
            "drafting": ["draft", "write", "create", "develop", "prepare"],
            "reviewing": ["review", "check", "validate", "verify", "assess"],
            "finalizing": ["finalize", "complete", "finish", "submit", "approve"]
        }
        
        for phase, indicators in phase_indicators.items():
            for message in messages:
                if message.role == "user":
                    if any(indicator in message.content.lower() for indicator in indicators):
                        return phase
        
        # Default to planning if no specific phase detected
        return "planning"
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        # Enhanced entity extraction
        words = text.split()
        entities = []
        for word in words:
            if word[0].isupper() and len(word) > 2:
                entities.append(word)
            elif word.lower() in ["api", "rag", "llm", "ai", "ml", "brd", "basel", "sme"]:
                entities.append(word.upper())
        return entities
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text"""
        topics = []
        text_lower = text.lower()
        
        topic_keywords = [
            "compliance", "risk", "policy", "document", "requirement",
            "implementation", "migration", "assessment", "analysis"
        ]
        
        for topic in topic_keywords:
            if topic in text_lower:
                topics.append(topic)
        
        return topics
    
    def _extract_constraints(self, text: str) -> List[str]:
        """Extract constraints from text"""
        constraints = []
        text_lower = text.lower()
        
        constraint_indicators = [
            "must", "should", "required", "mandatory", "compliance",
            "deadline", "budget", "scope", "limitation"
        ]
        
        for indicator in constraint_indicators:
            if indicator in text_lower:
                constraints.append(indicator)
        
        return constraints
    
    def _extract_goals(self, text: str) -> List[str]:
        """Extract goals from text"""
        goals = []
        text_lower = text.lower()
        
        goal_indicators = [
            "need to", "want to", "must", "should", "goal", "objective",
            "prepare", "create", "develop", "implement", "achieve"
        ]
        
        for indicator in goal_indicators:
            if indicator in text_lower:
                # Extract the goal phrase
                start_idx = text_lower.find(indicator)
                if start_idx != -1:
                    goal_phrase = text[start_idx:start_idx + 100]  # Get next 100 chars
                    goals.append(goal_phrase.strip())
                    break
        
        return goals
    
    def _extract_goal_indicators(self, text: str) -> List[str]:
        """Extract goal indicators from text"""
        indicators = []
        text_lower = text.lower()
        
        goal_words = [
            "prepare", "create", "develop", "implement", "achieve",
            "complete", "finish", "build", "design", "plan"
        ]
        
        for word in goal_words:
            if word in text_lower:
                indicators.append(word)
        
        return indicators
    
    def _extract_actions(self, text: str) -> List[str]:
        """Extract actions from text"""
        actions = []
        text_lower = text.lower()
        
        action_words = [
            "draft", "write", "review", "check", "validate",
            "update", "modify", "change", "improve", "enhance"
        ]
        
        for word in action_words:
            if word in text_lower:
                actions.append(word)
        
        return actions

    def _extract_persona_info(self, system_content: str) -> Dict[str, Any]:
        """Extract persona information from system message"""
        persona_info = {
            "role": "",
            "tone": "",
            "style": "",
            "expertise": "",
            "personality_traits": []
        }
        
        content_lower = system_content.lower()
        
        # Extract role (order matters - more specific roles first)
        role_keywords = {
            "doctor": ["doctor", "physician", "medical"],
            "lawyer": ["lawyer", "attorney", "legal"],
            "engineer": ["engineer", "developer", "technical"],
            "teacher": ["teacher", "instructor", "educator", "tutor"],
            "advisor": ["advisor", "counselor", "mentor", "guide"],
            "agent": ["agent", "representative", "customer service"],
            "analyst": ["analyst", "researcher", "investigator"],
            "expert": ["expert", "specialist", "consultant"],
            "assistant": ["assistant", "helper", "aid"]
        }
        
        for role, keywords in role_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                persona_info["role"] = role
                break
        
        # Special case: if "professional" is used as a descriptor, check for more specific roles
        if "professional" in content_lower and persona_info["role"] == "expert":
            # Look for more specific roles that might be described as "professional"
            specific_roles = ["doctor", "lawyer", "engineer", "teacher", "advisor", "agent"]
            for specific_role in specific_roles:
                if specific_role in content_lower:
                    persona_info["role"] = specific_role
                    break
        
        # Extract tone
        tone_keywords = {
            "friendly": ["friendly", "warm", "welcoming", "kind"],
            "professional": ["professional", "formal", "business"],
            "casual": ["casual", "informal", "relaxed"],
            "sarcastic": ["sarcastic", "witty", "humorous", "funny"],
            "serious": ["serious", "formal", "strict"],
            "enthusiastic": ["enthusiastic", "excited", "energetic"],
            "calm": ["calm", "patient", "gentle"]
        }
        
        for tone, keywords in tone_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                persona_info["tone"] = tone
                break
        
        # Extract style
        style_keywords = {
            "concise": ["concise", "brief", "short", "direct"],
            "detailed": ["detailed", "comprehensive", "thorough"],
            "simple": ["simple", "easy", "basic"],
            "technical": ["technical", "advanced", "complex"],
            "conversational": ["conversational", "chatty", "talkative"]
        }
        
        for style, keywords in style_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                persona_info["style"] = style
                break
        
        # Extract expertise areas
        expertise_keywords = [
            "technology", "medical", "legal", "financial", "educational",
            "customer service", "technical support", "marketing", "sales",
            "research", "analysis", "development", "design"
        ]
        
        for expertise in expertise_keywords:
            if expertise in content_lower:
                persona_info["expertise"] = expertise
                break
        
        # Extract personality traits
        trait_keywords = [
            "helpful", "patient", "knowledgeable", "experienced",
            "creative", "analytical", "empathetic", "efficient",
            "thorough", "reliable", "professional", "friendly"
        ]
        
        for trait in trait_keywords:
            if trait in content_lower:
                persona_info["personality_traits"].append(trait)
        
        return persona_info

class TopicTrackingStrategy(ConversationAnalysisStrategy):
    """Strategy that tracks conversation topics and generates topic-aware queries"""
    
    def get_strategy_name(self) -> str:
        return "topic_tracking"
    
    async def analyze_conversation(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """Analyze conversation to extract topics and context"""
        correlation_id = get_correlation_id()
        
        logger.debug(
            "Starting conversation analysis",
            extra=log_extra('topic_tracking_strategy_analysis_start', strategy=self.get_strategy_name(), messages_count=len(messages))
        )
        
        topics = []
        entities = []
        context_clues = []
        persona_info = {}
        
        # Extract topics from system messages
        for message in messages:
            if message.role == "system":
                topics.append("system_instruction")
                context_clues.append(message.content)
                
                # Extract persona information
                persona_info = self._extract_persona_info(message.content)
                
            elif message.role == "user":
                # Simple topic extraction (can be enhanced with NLP)
                words = message.content.lower().split()
                topics.extend([word for word in words if len(word) > 3])
            elif message.role == "assistant":
                # Extract entities from assistant responses
                entities.extend(self._extract_entities(message.content))
        
        result = {
            "topics": list(set(topics)),
            "entities": list(set(entities)),
            "context_clues": context_clues,
            "conversation_length": len(messages),
            "last_user_message": next((msg.content for msg in reversed(messages) if msg.role == "user"), ""),
            "persona_info": persona_info
        }
        
        logger.debug(
            "Conversation analysis completed",
            extra=log_extra(
                'topic_tracking_strategy_analysis_complete',
                strategy=self.get_strategy_name(),
                topics_count=len(result['topics']),
                entities_count=len(result['entities']),
                context_clues_count=len(result['context_clues']),
                persona_detected=bool(persona_info),
            )
        )
        
        return result
    
    async def generate_enhanced_queries(self, question: str, context: Dict[str, Any]) -> List[str]:
        """Generate enhanced queries based on conversation context"""
        correlation_id = get_correlation_id()
        
        logger.debug("Starting enhanced query generation", extra={
            'extra_fields': {
                'event_type': 'topic_tracking_strategy_query_generation_start',
                'strategy': self.get_strategy_name(),
                'original_question': question,
                'topics_count': len(context.get("topics", [])),
                'entities_count': len(context.get("entities", [])),
                'correlation_id': correlation_id
            }
        })
        
        queries = [question]  # Always include original question
        
        # Add topic-based queries
        for topic in context.get("topics", [])[:3]:  # Limit to top 3 topics
            if topic != "system_instruction":
                queries.append(f"{topic} {question}")
        
        # Add entity-based queries
        for entity in context.get("entities", [])[:2]:  # Limit to top 2 entities
            queries.append(f"{entity} {question}")
        
        # Add context-aware queries
        if context.get("context_clues"):
            context_clue = context["context_clues"][-1]  # Use last context clue
            queries.append(f"{context_clue} {question}")
        
        unique_queries = list(set(queries))  # Remove duplicates
        
        logger.debug("Enhanced query generation completed", extra={
            'extra_fields': {
                'event_type': 'topic_tracking_strategy_query_generation_complete',
                'strategy': self.get_strategy_name(),
                'original_queries_count': len(queries),
                'unique_queries_count': len(unique_queries),
                'correlation_id': correlation_id
            }
        })
        
        return unique_queries
    
    def _extract_entities(self, text: str) -> List[str]:
        """Simple entity extraction (can be enhanced with NLP)"""
        # Simple implementation - extract capitalized words as entities
        words = text.split()
        entities = [word for word in words if word[0].isupper() and len(word) > 2]
        return entities

    def _extract_persona_info(self, system_content: str) -> Dict[str, Any]:
        """Extract persona information from system message"""
        persona_info = {
            "role": "",
            "tone": "",
            "style": "",
            "expertise": "",
            "personality_traits": []
        }
        
        content_lower = system_content.lower()
        
        # Extract role (order matters - more specific roles first)
        role_keywords = {
            "doctor": ["doctor", "physician", "medical"],
            "lawyer": ["lawyer", "attorney", "legal"],
            "engineer": ["engineer", "developer", "technical"],
            "teacher": ["teacher", "instructor", "educator", "tutor"],
            "advisor": ["advisor", "counselor", "mentor", "guide"],
            "agent": ["agent", "representative", "customer service"],
            "analyst": ["analyst", "researcher", "investigator"],
            "expert": ["expert", "specialist", "consultant"],
            "assistant": ["assistant", "helper", "aid"]
        }
        
        for role, keywords in role_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                persona_info["role"] = role
                break
        
        # Special case: if "professional" is used as a descriptor, check for more specific roles
        if "professional" in content_lower and persona_info["role"] == "expert":
            # Look for more specific roles that might be described as "professional"
            specific_roles = ["doctor", "lawyer", "engineer", "teacher", "advisor", "agent"]
            for specific_role in specific_roles:
                if specific_role in content_lower:
                    persona_info["role"] = specific_role
                    break
        
        # Extract tone
        tone_keywords = {
            "friendly": ["friendly", "warm", "welcoming", "kind"],
            "professional": ["professional", "formal", "business"],
            "casual": ["casual", "informal", "relaxed"],
            "sarcastic": ["sarcastic", "witty", "humorous", "funny"],
            "serious": ["serious", "formal", "strict"],
            "enthusiastic": ["enthusiastic", "excited", "energetic"],
            "calm": ["calm", "patient", "gentle"]
        }
        
        for tone, keywords in tone_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                persona_info["tone"] = tone
                break
        
        # Extract style
        style_keywords = {
            "concise": ["concise", "brief", "short", "direct"],
            "detailed": ["detailed", "comprehensive", "thorough"],
            "simple": ["simple", "easy", "basic"],
            "technical": ["technical", "advanced", "complex"],
            "conversational": ["conversational", "chatty", "talkative"]
        }
        
        for style, keywords in style_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                persona_info["style"] = style
                break
        
        # Extract expertise areas
        expertise_keywords = [
            "technology", "medical", "legal", "financial", "educational",
            "customer service", "technical support", "marketing", "sales",
            "research", "analysis", "development", "design"
        ]
        
        for expertise in expertise_keywords:
            if expertise in content_lower:
                persona_info["expertise"] = expertise
                break
        
        # Extract personality traits
        trait_keywords = [
            "helpful", "patient", "knowledgeable", "experienced",
            "creative", "analytical", "empathetic", "efficient",
            "thorough", "reliable", "professional", "friendly"
        ]
        
        for trait in trait_keywords:
            if trait in content_lower:
                persona_info["personality_traits"].append(trait)
        
        return persona_info

class EntityExtractionStrategy(ConversationAnalysisStrategy):
    """Strategy that focuses on entity extraction and entity-aware queries"""
    
    def get_strategy_name(self) -> str:
        return "entity_extraction"
    
    async def analyze_conversation(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        """Analyze conversation focusing on entity extraction"""
        correlation_id = get_correlation_id()
        
        logger.debug("Starting entity extraction analysis", extra={
            'extra_fields': {
                'event_type': 'entity_extraction_strategy_analysis_start',
                'strategy': self.get_strategy_name(),
                'messages_count': len(messages),
                'correlation_id': correlation_id
            }
        })
        
        entities = []
        relationships = []
        
        for message in messages:
            if message.role in ["user", "assistant"]:
                entities.extend(self._extract_entities(message.content))
                relationships.extend(self._extract_relationships(message.content))
        
        result = {
            "entities": list(set(entities)),
            "relationships": list(set(relationships)),
            "conversation_length": len(messages),
            "last_user_message": next((msg.content for msg in reversed(messages) if msg.role == "user"), "")
        }
        
        logger.debug("Entity extraction analysis completed", extra={
            'extra_fields': {
                'event_type': 'entity_extraction_strategy_analysis_complete',
                'strategy': self.get_strategy_name(),
                'entities_count': len(result['entities']),
                'relationships_count': len(result['relationships']),
                'correlation_id': correlation_id
            }
        })
        
        return result
    
    async def generate_enhanced_queries(self, question: str, context: Dict[str, Any]) -> List[str]:
        """Generate entity-aware queries"""
        correlation_id = get_correlation_id()
        
        logger.debug("Starting entity-aware query generation", extra={
            'extra_fields': {
                'event_type': 'entity_extraction_strategy_query_generation_start',
                'strategy': self.get_strategy_name(),
                'original_question': question,
                'entities_count': len(context.get("entities", [])),
                'relationships_count': len(context.get("relationships", [])),
                'correlation_id': correlation_id
            }
        })
        
        queries = [question]
        
        # Add entity-based queries
        for entity in context.get("entities", [])[:3]:
            queries.append(f"{entity} {question}")
            queries.append(f"{question} {entity}")
        
        # Add relationship-based queries
        for relationship in context.get("relationships", [])[:2]:
            queries.append(f"{relationship} {question}")
        
        unique_queries = list(set(queries))
        
        logger.debug("Entity-aware query generation completed", extra={
            'extra_fields': {
                'event_type': 'entity_extraction_strategy_query_generation_complete',
                'strategy': self.get_strategy_name(),
                'original_queries_count': len(queries),
                'unique_queries_count': len(unique_queries),
                'correlation_id': correlation_id
            }
        })
        
        return unique_queries
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text"""
        # Enhanced entity extraction
        words = text.split()
        entities = []
        for word in words:
            if word[0].isupper() and len(word) > 2:
                entities.append(word)
            elif word.lower() in ["api", "rag", "llm", "ai", "ml"]:
                entities.append(word.upper())
        return entities
    
    def _extract_relationships(self, text: str) -> List[str]:
        """Extract relationships from text"""
        relationships = []
        text_lower = text.lower()
        
        if "how" in text_lower:
            relationships.append("how")
        if "what" in text_lower:
            relationships.append("what")
        if "why" in text_lower:
            relationships.append("why")
        if "when" in text_lower:
            relationships.append("when")
        if "where" in text_lower:
            relationships.append("where")
        
        return relationships

class ChatCompletionPlugin(ABC):
    """Abstract base class for chat completion plugins"""
    
    @abstractmethod
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        """Process the context and return updated context"""
        pass
    
    @abstractmethod
    def get_priority(self) -> ProcessingPriority:
        """Get the processing priority of this plugin"""
        pass
    
    @abstractmethod
    def get_plugin_name(self) -> str:
        """Get the name of this plugin"""
        pass

class ConversationContextPlugin(ChatCompletionPlugin):
    """Plugin that analyzes conversation context"""
    
    def __init__(self, strategy_factory: 'ConversationStrategyFactory'):
        self.strategy_factory = strategy_factory
    
    def get_priority(self) -> ProcessingPriority:
        return ProcessingPriority.HIGH
    
    def get_plugin_name(self) -> str:
        return "conversation_context"
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        """Analyze conversation context and determine strategy"""
        correlation_id = get_correlation_id()
        
        logger.debug("Processing conversation context", extra={
            'extra_fields': {
                'event_type': 'conversation_context_plugin_start',
                'plugin': self.get_plugin_name(),
                'correlation_id': correlation_id
            }
        })
        
        # Extract and preserve original persona
        original_persona = ""
        for message in context.request.messages:
            if message.role == "system":
                original_persona = message.content
                break
        
        # Determine strategy based on request characteristics
        strategy = self.strategy_factory.get_strategy(context.request)
        context.strategy = strategy.get_strategy_name()
        
        # Analyze conversation
        conversation_context = await strategy.analyze_conversation(context.request.messages)
        context.conversation_context = conversation_context
        
        # Add messages to context for multi-turn processing
        context.conversation_context["messages"] = context.request.messages
        
        # Add conversation state if available
        if "conversation_state" in conversation_context:
            context.conversation_state = conversation_context["conversation_state"]
        
        # Add persona information to conversation context
        if original_persona:
            context.conversation_context["original_persona"] = original_persona
            context.conversation_context["persona_detected"] = True
            context.conversation_context["persona_length"] = len(original_persona)
        else:
            context.conversation_context["original_persona"] = ""
            context.conversation_context["persona_detected"] = False
            context.conversation_context["persona_length"] = 0
        
        logger.info("Conversation context processed", extra={
            'extra_fields': {
                'event_type': 'conversation_context_plugin_complete',
                'plugin': self.get_plugin_name(),
                'strategy': context.strategy,
                'topics_count': len(conversation_context.get('topics', [])),
                'entities_count': len(conversation_context.get('entities', [])),
                'persona_detected': bool(original_persona),
                'persona_length': len(original_persona),
                'correlation_id': correlation_id
            }
        })
        
        return context

class MultiQueryRAGPlugin(ChatCompletionPlugin):
    """Plugin that performs multi-query RAG processing"""
    
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service
    
    def get_priority(self) -> ProcessingPriority:
        return ProcessingPriority.NORMAL
    
    def get_plugin_name(self) -> str:
        return "multi_query_rag"
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        """Perform multi-query RAG processing"""
        correlation_id = get_correlation_id()
        
        logger.debug("Processing multi-query RAG", extra={
            'extra_fields': {
                'event_type': 'multi_query_rag_plugin_start',
                'plugin': self.get_plugin_name(),
                'correlation_id': correlation_id
            }
        })
        
        # Get the last user message
        last_user_message = context.conversation_context.get('last_user_message', '')
        if not last_user_message:
            # Fallback: extract from messages
            for message in reversed(context.request.messages):
                if message.role == "user":
                    last_user_message = message.content
                    break
        
        if not last_user_message:
            logger.warning("No user message found", extra={
                'extra_fields': {
                    'event_type': 'multi_query_rag_no_user_message',
                    'correlation_id': correlation_id
                }
            })
            return context
        
        # Generate enhanced queries using the strategy
        strategy = context.strategy
        if strategy == "multi_turn_conversation":
            analysis_strategy = MultiTurnConversationStrategy()
        elif strategy == "topic_tracking":
            analysis_strategy = TopicTrackingStrategy()
        elif strategy == "entity_extraction":
            analysis_strategy = EntityExtractionStrategy()
        else:
            analysis_strategy = MultiTurnConversationStrategy()  # Default to multi-turn
        
        enhanced_queries = await analysis_strategy.generate_enhanced_queries(
            last_user_message, context.conversation_context
        )
        context.enhanced_queries = enhanced_queries
        
        # Extract original system message (persona) for RAG calls
        original_system_message = ""
        for message in context.request.messages:
            if message.role == "system":
                original_system_message = message.content
                break
        
        # Perform parallel multi-query retrieval
        all_results = await self._process_queries_parallel(enhanced_queries, correlation_id)
        
        # Deduplicate and rank results
        unique_results = self._deduplicate_results(all_results)
        # If retrieval-only produced nothing, fallback to single ask_question to maintain compatibility
        if not unique_results:
            try:
                fallback_result = await self.rag_service.ask_question(
                    last_user_message,
                    top_k=5,
                    system_message=original_system_message
                )
                if fallback_result.get('success') and fallback_result.get('sources'):
                    # Normalize to same shape
                    for src in fallback_result['sources']:
                        context_source = {
                            "content": src.get("content", ""),
                            "source": src.get("source", "Unknown"),
                            "score": src.get("score", 0.0)
                        }
                        unique_results.append(context_source)
            except Exception:
                pass
        # Increase limit from 5 to 10 for better context coverage
        context.rag_results = unique_results[:10]  # Limit to top 10 results
        
        logger.info("Multi-query RAG processing completed", extra={
            'extra_fields': {
                'event_type': 'multi_query_rag_plugin_complete',
                'plugin': self.get_plugin_name(),
                'queries_count': len(enhanced_queries),
                'results_count': len(context.rag_results),
                'correlation_id': correlation_id
            }
        })
        
        return context
    
    async def _process_queries_parallel(self, enhanced_queries: List[str], correlation_id: str) -> List[Dict[str, Any]]:
        """Process multiple queries in parallel for better performance"""
        
        # Check if parallel processing is enabled in configuration
        try:
            from app.core.enhanced_chat_config import get_performance_config
            performance_config = get_performance_config()
            enable_parallel = performance_config.get("enable_parallel_processing", True)
            max_concurrent = performance_config.get("max_concurrent_queries", 4)
        except ImportError:
            # Fallback to default values if config is not available
            enable_parallel = True
            max_concurrent = 4
        
        if not enable_parallel:
            logger.debug("Parallel processing disabled, using sequential processing", extra={
                'extra_fields': {
                    'event_type': 'parallel_processing_disabled',
                    'correlation_id': correlation_id
                }
            })
            return await self._process_queries_sequential(enhanced_queries, correlation_id)
        
        async def process_single_query(query: str) -> List[Dict[str, Any]]:
            """Process a single query with embedding and vector search"""
            try:
                # Check cache for embedding
                from app.core.cache_service import cache_service
                cached_embedding = await cache_service.get_embedding(query)
                
                if cached_embedding:
                    query_vector = cached_embedding
                    logger.debug(f"Using cached embedding for query: {query[:50]}...", extra={
                        'extra_fields': {
                            'event_type': 'cache_embedding_hit',
                            'query_length': len(query)
                        }
                    })
                else:
                    # Get embedding from API
                    query_vector = (await self.rag_service.embedding_provider.get_embeddings([query]))[0]
                    # Cache the embedding
                    await cache_service.set_embedding(query, query_vector)
                    logger.debug(f"Cached new embedding for query: {query[:50]}...", extra={
                        'extra_fields': {
                            'event_type': 'cache_embedding_miss',
                            'query_length': len(query)
                        }
                    })
                
                # Check cache for search results
                cached_search_results = await cache_service.get_search_results(
                    query_vector, 5, Config.QDRANT_COLLECTION_NAME
                )
                
                if cached_search_results:
                    search_results = cached_search_results
                    logger.debug(f"Using cached search results for query: {query[:50]}...", extra={
                        'extra_fields': {
                            'event_type': 'cache_search_hit',
                            'results_count': len(search_results)
                        }
                    })
                else:
                    # Get search results from API
                    search_results = await self.rag_service.vector_store_provider.search_vectors(
                        query_vector, 5, Config.QDRANT_COLLECTION_NAME
                    )
                    # Cache the search results
                    await cache_service.set_search_results(
                        query_vector, 5, Config.QDRANT_COLLECTION_NAME, search_results
                    )
                    logger.debug(f"Cached new search results for query: {query[:50]}...", extra={
                        'extra_fields': {
                            'event_type': 'cache_search_miss',
                            'results_count': len(search_results)
                        }
                    })
                
                # Normalize to common source structure used downstream
                normalized_results = []
                for item in search_results:
                    payload = item.get("payload", {})
                    content = payload.get("content", "")
                    metadata = payload.get("metadata", {})
                    source = metadata.get("source", "Unknown")
                    normalized_results.append({
                        "content": content,
                        "source": source,
                        "score": item.get("score", 0.0)
                    })
                
                return normalized_results
                
            except Exception as e:
                logger.warning(f"Query failed: {query}", extra={
                    'extra_fields': {
                        'event_type': 'multi_query_rag_query_failed',
                        'query': query,
                        'error': str(e),
                        'correlation_id': correlation_id
                    }
                })
                return []
        
        # Execute all queries concurrently using asyncio.gather
        tasks = [process_single_query(query) for query in enhanced_queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine all results
        all_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Query {i} failed with exception: {result}", extra={
                    'extra_fields': {
                        'event_type': 'multi_query_rag_query_exception',
                        'query_index': i,
                        'query': enhanced_queries[i] if i < len(enhanced_queries) else "unknown",
                        'error': str(result),
                        'correlation_id': correlation_id
                    }
                })
            else:
                all_results.extend(result)
        
        logger.debug(f"Parallel query processing completed: {len(all_results)} results from {len(enhanced_queries)} queries", extra={
            'extra_fields': {
                'event_type': 'parallel_query_processing_complete',
                'queries_count': len(enhanced_queries),
                'results_count': len(all_results),
                'correlation_id': correlation_id
            }
        })
        
        return all_results
    
    async def _process_queries_sequential(self, enhanced_queries: List[str], correlation_id: str) -> List[Dict[str, Any]]:
        """Process multiple queries sequentially (fallback method)"""
        all_results = []
        
        for query in enhanced_queries:
            try:
                # Check cache for embedding
                from app.core.cache_service import cache_service
                cached_embedding = await cache_service.get_embedding(query)
                
                if cached_embedding:
                    query_vector = cached_embedding
                    logger.debug(f"Using cached embedding for query: {query[:50]}...", extra={
                        'extra_fields': {
                            'event_type': 'cache_embedding_hit_sequential',
                            'query_length': len(query)
                        }
                    })
                else:
                    # Get embedding from API
                    query_vector = (await self.rag_service.embedding_provider.get_embeddings([query]))[0]
                    # Cache the embedding
                    await cache_service.set_embedding(query, query_vector)
                    logger.debug(f"Cached new embedding for query: {query[:50]}...", extra={
                        'extra_fields': {
                            'event_type': 'cache_embedding_miss_sequential',
                            'query_length': len(query)
                        }
                    })
                
                # Check cache for search results
                cached_search_results = await cache_service.get_search_results(
                    query_vector, 5, Config.QDRANT_COLLECTION_NAME
                )
                
                if cached_search_results:
                    search_results = cached_search_results
                    logger.debug(f"Using cached search results for query: {query[:50]}...", extra={
                        'extra_fields': {
                            'event_type': 'cache_search_hit_sequential',
                            'results_count': len(search_results)
                        }
                    })
                else:
                    # Get search results from API
                    search_results = await self.rag_service.vector_store_provider.search_vectors(
                        query_vector, 5, Config.QDRANT_COLLECTION_NAME
                    )
                    # Cache the search results
                    await cache_service.set_search_results(
                        query_vector, 5, Config.QDRANT_COLLECTION_NAME, search_results
                    )
                    logger.debug(f"Cached new search results for query: {query[:50]}...", extra={
                        'extra_fields': {
                            'event_type': 'cache_search_miss_sequential',
                            'results_count': len(search_results)
                        }
                    })
                # Normalize to common source structure used downstream
                for item in search_results:
                    payload = item.get("payload", {})
                    content = payload.get("content", "")
                    metadata = payload.get("metadata", {})
                    source = metadata.get("source", "Unknown")
                    all_results.append({
                        "content": content,
                        "source": source,
                        "score": item.get("score", 0.0)
                    })
            except Exception as e:
                logger.warning(f"Query failed: {query}", extra={
                    'extra_fields': {
                        'event_type': 'multi_query_rag_query_failed',
                        'query': query,
                        'error': str(e),
                        'correlation_id': correlation_id
                    }
                })
        
        logger.debug(f"Sequential query processing completed: {len(all_results)} results from {len(enhanced_queries)} queries", extra={
            'extra_fields': {
                'event_type': 'sequential_query_processing_complete',
                'queries_count': len(enhanced_queries),
                'results_count': len(all_results),
                'correlation_id': correlation_id
            }
        })
        
        return all_results
    
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

class ResponseEnhancementPlugin(ChatCompletionPlugin):
    """Plugin that enhances the final response"""
    
    def __init__(self, llm_provider):
        self.llm_provider = llm_provider
    
    def get_priority(self) -> ProcessingPriority:
        return ProcessingPriority.LOW
    
    def get_plugin_name(self) -> str:
        return "response_enhancement"
    
    async def process(self, context: ProcessingContext) -> ProcessingContext:
        """Enhance the final response with context and metadata"""
        correlation_id = get_correlation_id()
        
        logger.debug("Enhancing response", extra={
            'extra_fields': {
                'event_type': 'response_enhancement_plugin_start',
                'plugin': self.get_plugin_name(),
                'correlation_id': correlation_id
            }
        })
        
        # Extract original system message (persona)
        original_system_message = ""
        for message in context.request.messages:
            if message.role == "system":
                original_system_message = message.content
                break
        
        # Get the last user message
        last_user_message = context.conversation_context.get('last_user_message', '')
        
        # Prepare context for LLM
        context_text = ""
        if context.rag_results:
            context_parts = []
            for result in context.rag_results:
                content = result.get('content', '')
                source = result.get('source', 'Unknown')
                context_parts.append(f"Source: {source}\nContent: {content}")
            context_text = "\n\n".join(context_parts)
            
            # Monitor context quality
            context_length = len(context_text)
            estimated_tokens = len(context_text.split()) * 1.3
            
            logger.info("Context prepared for LLM", extra={
                'extra_fields': {
                    'event_type': 'response_enhancement_context_prepared',
                    'context_length': context_length,
                    'estimated_tokens': estimated_tokens,
                    'sources_count': len(context.rag_results),
                    'correlation_id': correlation_id
                }
            })
        
        # Preserve original persona while adding RAG context
        if context_text:
            enhanced_system_message = f"{original_system_message}\n\nYou have access to the following relevant information that may help answer the user's question:\n{context_text}\n\nUse this information to provide more accurate and helpful responses while maintaining your designated role and personality."
        else:
            enhanced_system_message = original_system_message
        
        # Generate response using LLM with preserved persona
        messages = [
            {
                "role": "system",
                "content": enhanced_system_message
            },
            {
                "role": "user",
                "content": last_user_message
            }
        ]
        
        # Use call_llm_api for full control with token-aware parameters
        token_config = token_config_service.get_config()
        max_tokens = token_config.get_response_tokens(context.request.max_tokens)
        
        request = {
            "model": context.request.model,
            "messages": messages,
            "temperature": context.request.temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = await self.llm_provider.call_llm_api(request, return_full_response=True)
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Prepare response data
            context.response_data = {
                "id": f"chatcmpl-{correlation_id}",
                "object": "chat.completion",
                "created": int(__import__('time').time()),
                "model": context.request.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": response.get("usage", {
                    "prompt_tokens": len(last_user_message.split()),
                    "completion_tokens": len(content.split()),
                    "total_tokens": len(last_user_message.split()) + len(content.split())
                }),
                "sources": context.rag_results or []
            }
            
            # Add enhanced metadata
            context.metadata = {
                "conversation_aware": True,
                "strategy_used": context.strategy,
                "enhanced_queries_count": len(context.enhanced_queries or []),
                "conversation_context": context.conversation_context,
                "processing_plugins": ["conversation_context", "multi_query_rag", "response_enhancement"],
                "persona_preserved": True,
                "original_persona_length": len(original_system_message),
                "rag_context_added": bool(context_text),
                "multi_turn_enabled": True,
                "conversation_state": {
                    "current_goal": context.conversation_state.current_goal if context.conversation_state else "",
                    "conversation_phase": context.conversation_state.conversation_phase if context.conversation_state else "planning",
                    "key_entities_count": len(context.conversation_state.key_entities) if context.conversation_state else 0,
                    "constraints_count": len(context.conversation_state.constraints) if context.conversation_state else 0
                } if context.conversation_state else {}
            }
            
            logger.info("Response enhancement completed", extra={
                'extra_fields': {
                    'event_type': 'response_enhancement_plugin_complete',
                    'plugin': self.get_plugin_name(),
                    'content_length': len(content),
                    'sources_count': len(context.rag_results or []),
                    'persona_preserved': True,
                    'correlation_id': correlation_id
                }
            })
            
        except Exception as e:
            logger.error("Response enhancement failed", extra={
                'extra_fields': {
                    'event_type': 'response_enhancement_plugin_error',
                    'plugin': self.get_plugin_name(),
                    'error': str(e),
                    'correlation_id': correlation_id
                }
            })
            # Fallback response
            context.response_data = {
                "id": f"chatcmpl-{correlation_id}",
                "object": "chat.completion",
                "created": int(__import__('time').time()),
                "model": context.request.model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I'm sorry, I encountered an error while processing your request."
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                },
                "sources": []
            }
            
            # Preserve existing metadata and add fallback info
            if not context.metadata:
                context.metadata = {}
            
            context.metadata.update({
                "conversation_aware": True,
                "strategy_used": context.strategy or "unknown",
                "enhanced_queries_count": len(context.enhanced_queries or []),
                "processing_plugins": ["conversation_context", "multi_query_rag", "response_enhancement_fallback"],
                "persona_preserved": True,
                "original_persona_length": len(original_system_message),
                "persona_detected": bool(original_system_message),
                "rag_context_added": bool(context_text),
                "multi_turn_enabled": True,
                "conversation_state": {
                    "current_goal": context.conversation_state.current_goal if context.conversation_state else "",
                    "conversation_phase": context.conversation_state.conversation_phase if context.conversation_state else "planning",
                    "key_entities_count": len(context.conversation_state.key_entities) if context.conversation_state else 0,
                    "constraints_count": len(context.conversation_state.constraints) if context.conversation_state else 0
                } if context.conversation_state else {},
                "error_occurred": True,
                "error_plugin": "response_enhancement"
            })
        
        return context

class ConversationStrategyFactory:
    """Factory for creating conversation analysis strategies"""
    
    def __init__(self):
        self.strategies = {
            "multi_turn_conversation": MultiTurnConversationStrategy(),
            "topic_tracking": TopicTrackingStrategy(),
            "entity_extraction": EntityExtractionStrategy()
        }
    
    def get_strategy(self, request: ChatCompletionRequest) -> ConversationAnalysisStrategy:
        """Determine the best strategy based on request characteristics"""
        correlation_id = get_correlation_id()
        
        logger.debug("Determining conversation analysis strategy", extra={
            'extra_fields': {
                'event_type': 'strategy_factory_strategy_selection_start',
                'messages_count': len(request.messages),
                'correlation_id': correlation_id
            }
        })
        
        # Analyze request to determine strategy
        messages = request.messages
        system_messages = [msg for msg in messages if msg.role == "system"]
        user_messages = [msg for msg in messages if msg.role == "user"]
        
        # If there are system messages with specific instructions, use topic tracking
        if system_messages and any("entity" in msg.content.lower() for msg in system_messages):
            selected_strategy = "entity_extraction"
            logger.debug("Entity extraction strategy selected", extra={
                'extra_fields': {
                    'event_type': 'strategy_factory_strategy_selected',
                    'strategy': selected_strategy,
                    'reason': 'entity_instruction_in_system_message',
                    'correlation_id': correlation_id
                }
            })
            return self.strategies[selected_strategy]
        
        # If conversation is long, use multi-turn conversation strategy
        if len(messages) > 3:
            selected_strategy = "multi_turn_conversation"
            logger.debug("Multi-turn conversation strategy selected", extra={
                'extra_fields': {
                    'event_type': 'strategy_factory_strategy_selected',
                    'strategy': selected_strategy,
                    'reason': 'long_conversation',
                    'correlation_id': correlation_id
                }
            })
            return self.strategies[selected_strategy]
        
        # Default to multi-turn conversation strategy
        selected_strategy = "multi_turn_conversation"
        logger.debug("Multi-turn conversation strategy selected (default)", extra={
            'extra_fields': {
                'event_type': 'strategy_factory_strategy_selected',
                'strategy': selected_strategy,
                'reason': 'default_strategy',
                'correlation_id': correlation_id
            }
        })
        return self.strategies[selected_strategy]

class ChatCompletionPluginManager:
    """Manages the execution of chat completion plugins"""
    
    def __init__(self):
        self.plugins: List[ChatCompletionPlugin] = []
    
    def register_plugin(self, plugin: ChatCompletionPlugin):
        """Register a plugin for processing"""
        self.plugins.append(plugin)
        # Sort by priority
        self.plugins.sort(key=lambda p: p.get_priority().value)
    
    async def process_request(self, context: ProcessingContext) -> ProcessingContext:
        """Process the request through all registered plugins"""
        correlation_id = get_correlation_id()
        
        logger.info("Starting plugin processing", extra={
            'extra_fields': {
                'event_type': 'plugin_processing_start',
                'plugins_count': len(self.plugins),
                'correlation_id': correlation_id
            }
        })
        
        for plugin in self.plugins:
            try:
                logger.debug(f"Processing plugin: {plugin.get_plugin_name()}", extra={
                    'extra_fields': {
                        'event_type': 'plugin_processing_step',
                        'plugin': plugin.get_plugin_name(),
                        'priority': plugin.get_priority().value,
                        'correlation_id': correlation_id
                    }
                })
                
                context = await plugin.process(context)
                
            except Exception as e:
                logger.error(f"Plugin {plugin.get_plugin_name()} failed", extra={
                    'extra_fields': {
                        'event_type': 'plugin_processing_error',
                        'plugin': plugin.get_plugin_name(),
                        'error': str(e),
                        'correlation_id': correlation_id
                    }
                })
                # Continue with next plugin
        
        logger.info("Plugin processing completed", extra={
            'extra_fields': {
                'event_type': 'plugin_processing_complete',
                'correlation_id': correlation_id
            }
        })
        
        return context

class EnhancedChatCompletionService:
    """Enhanced chat completion service using Strategy Pattern and Plugin Architecture"""
    
    def __init__(self, rag_service: RAGService, llm_provider):
        self.rag_service = rag_service
        self.llm_provider = llm_provider
        self.strategy_factory = ConversationStrategyFactory()
        self.plugin_manager = ChatCompletionPluginManager()
        
        # Register core plugins
        self.plugin_manager.register_plugin(
            ConversationContextPlugin(self.strategy_factory)
        )
        self.plugin_manager.register_plugin(
            MultiQueryRAGPlugin(self.rag_service)
        )
        self.plugin_manager.register_plugin(
            ResponseEnhancementPlugin(self.llm_provider)
        )
        
        logger.info("Enhanced Chat Completion Service initialized", extra={
            'extra_fields': {
                'event_type': 'enhanced_chat_completion_service_initialized',
                'plugins_count': 3,
                'strategies_count': 2
            }
        })
    
    async def process_request(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Process a chat completion request with enhanced capabilities"""
        correlation_id = get_correlation_id()
        
        logger.info("Enhanced chat completion request received", extra={
            'extra_fields': {
                'event_type': 'enhanced_chat_completion_request_start',
                'model': request.model,
                'messages_count': len(request.messages),
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Create processing context
            context = ProcessingContext(request)
            
            # Process through plugin pipeline
            context = await self.plugin_manager.process_request(context)
            
            # Build response with fallback if needed
            if context.response_data is None:
                # Create fallback response if plugins failed
                correlation_id = get_correlation_id()
                last_user_message = ""
                for message in request.messages:
                    if message.role == "user":
                        last_user_message = message.content
                        break
                
                # Extract original persona for fallback metadata
                original_persona = ""
                for message in request.messages:
                    if message.role == "system":
                        original_persona = message.content
                        break
                
                context.response_data = {
                    "id": f"chatcmpl-{correlation_id}",
                    "object": "chat.completion",
                    "created": int(__import__('time').time()),
                    "model": request.model,
                    "choices": [
                        {
                            "index": 0,
                            "message": {
                                "role": "assistant",
                                "content": "I'm sorry, I encountered an error while processing your request."
                            },
                            "finish_reason": "stop"
                        }
                    ],
                    "usage": {
                        "prompt_tokens": len(last_user_message.split()),
                        "completion_tokens": 0,
                        "total_tokens": len(last_user_message.split())
                    },
                    "sources": []
                }
                
                # Set fallback metadata
                context.metadata = {
                    "conversation_aware": False,
                    "strategy_used": "fallback",
                    "enhanced_queries_count": 0,
                    "processing_plugins": ["fallback"],
                    "persona_preserved": False,
                    "original_persona_length": len(original_persona),
                    "persona_detected": bool(original_persona),
                    "rag_context_added": False,
                    "multi_turn_enabled": False,
                    "conversation_state": {},
                    "error_occurred": True
                }
            
            response = ChatCompletionResponse(**context.response_data)
            
            # Add enhanced metadata if available
            if context.metadata:
                response.metadata = context.metadata
            else:
                # Ensure metadata is always present
                response.metadata = {
                    "conversation_aware": False,
                    "strategy_used": "unknown",
                    "enhanced_queries_count": 0,
                    "processing_plugins": [],
                    "persona_preserved": False,
                    "original_persona_length": 0,
                    "persona_detected": False,
                    "rag_context_added": False,
                    "multi_turn_enabled": False,
                    "conversation_state": {}
                }
            
            logger.info("Enhanced chat completion request completed", extra={
                'extra_fields': {
                    'event_type': 'enhanced_chat_completion_request_complete',
                    'model': request.model,
                    'strategy_used': context.strategy,
                    'correlation_id': correlation_id
                }
            })
            
            return response
            
        except Exception as e:
            logger.error("Enhanced chat completion request failed", extra={
                'extra_fields': {
                    'event_type': 'enhanced_chat_completion_request_error',
                    'model': request.model,
                    'error': str(e),
                    'correlation_id': correlation_id
                }
            })
            raise 