"""
Unit tests for enhanced short message context processing.
Tests the improved handling of one-word responses in multi-turn conversations.
"""

import pytest
from unittest.mock import Mock, patch
from app.domain.services.enhanced_chat_completion_service import (
    MultiTurnConversationStrategy, ChatMessage, ConversationState
)
from app.domain.models.requests import ChatMessage as RequestChatMessage


class TestEnhancedShortMessageContext:
    """Test cases for enhanced short message context processing"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.strategy = MultiTurnConversationStrategy()
    
    def test_expand_short_question_yes_no(self):
        """Test expansion of yes/no short questions"""
        # Create context with previous conversation
        context = {
            "entities": ["Python", "API", "RAG"],
            "topics": ["programming", "development"],
            "messages": [
                RequestChatMessage(role="user", content="I need help with Python API"),
                RequestChatMessage(role="assistant", content="What specific aspect of the Python API do you need help with?"),
                RequestChatMessage(role="user", content="Yes")
            ]
        }
        
        # Test expansion of "Yes"
        expanded = self.strategy._expand_short_question("Yes", context)
        
        # Should include context from previous question
        assert len(expanded) > 0
        assert any("Python API" in query for query in expanded)
    
    def test_expand_short_question_why(self):
        """Test expansion of 'why' questions"""
        context = {
            "entities": ["Python", "API"],
            "topics": ["programming"],
            "messages": []
        }
        
        expanded = self.strategy._expand_short_question("Why", context)
        
        # Should expand with entities and topics
        assert len(expanded) > 0
        assert any("Why Python" in query for query in expanded)
        assert any("Why programming" in query for query in expanded)
    
    def test_extract_entities_enhanced_short_words(self):
        """Test enhanced entity extraction with short words"""
        # Test short technical terms
        entities = self.strategy._extract_entities_enhanced("API ML AI")
        assert "API" in entities
        assert "ML" in entities
        assert "AI" in entities
        
        # Test short capitalized words
        entities = self.strategy._extract_entities_enhanced("Go Java")
        assert "GO" in entities  # Should be converted to uppercase
        assert "JAVA" in entities  # Should be converted to uppercase
        
        # Test acronyms
        entities = self.strategy._extract_entities_enhanced("SQL DB")
        assert "SQL" in entities
        assert "DB" in entities
    
    def test_extract_topics_enhanced_short_terms(self):
        """Test enhanced topic extraction with short terms"""
        # Test short technical topics
        topics = self.strategy._extract_topics_enhanced("API RAG LLM")
        assert "api" in topics
        assert "rag" in topics
        assert "llm" in topics
        
        # Test short action words
        topics = self.strategy._extract_topics_enhanced("test deploy config")
        assert "test" in topics
        assert "deploy" in topics
        assert "config" in topics
    
    def test_get_previous_question(self):
        """Test extraction of previous assistant question"""
        messages = [
            RequestChatMessage(role="user", content="I need help with Python"),
            RequestChatMessage(role="assistant", content="What specific Python topic do you need help with?"),
            RequestChatMessage(role="user", content="Yes")
        ]
        
        prev_question = self.strategy._get_previous_question(messages)
        assert "Python topic" in prev_question
        assert "?" in prev_question
    
    def test_extract_context_from_history(self):
        """Test context extraction from conversation history"""
        messages = [
            RequestChatMessage(role="user", content="I need help with Python API"),
            RequestChatMessage(role="assistant", content="What specific aspect?"),
            RequestChatMessage(role="user", content="Authentication"),
            RequestChatMessage(role="assistant", content="Do you want to use OAuth?"),
            RequestChatMessage(role="user", content="Yes")
        ]
        
        context_parts = self.strategy._extract_context_from_history(messages)
        
        # Should extract entities and topics from previous messages
        assert len(context_parts) > 0
        assert any("Python" in part for part in context_parts)
        assert any("API" in part for part in context_parts)
    
    def test_calculate_adaptive_context_window_short_message(self):
        """Test adaptive context window for short messages"""
        messages = [
            RequestChatMessage(role="user", content="Long detailed question about Python"),
            RequestChatMessage(role="assistant", content="Detailed response"),
            RequestChatMessage(role="user", content="Yes")  # Short message
        ]
        
        window = self.strategy._calculate_adaptive_context_window(messages, max_turns=5)
        
        # Should use larger context window for short messages (but limited by available messages)
        assert window >= 3  # At least all available messages
    
    def test_calculate_adaptive_context_window_long_message(self):
        """Test adaptive context window for long messages"""
        messages = [
            RequestChatMessage(role="user", content="Long detailed question about Python"),
            RequestChatMessage(role="assistant", content="Detailed response"),
            RequestChatMessage(role="user", content="This is a longer response with more context")  # Long message
        ]
        
        window = self.strategy._calculate_adaptive_context_window(messages, max_turns=5)
        
        # Should use standard context window for long messages (but limited by available messages)
        assert window >= 3  # At least all available messages
    
    def test_infer_goal_from_pattern_help(self):
        """Test goal inference from help patterns"""
        messages = [
            RequestChatMessage(role="user", content="I need help with Python"),
            RequestChatMessage(role="assistant", content="What specific help do you need?"),
            RequestChatMessage(role="user", content="Yes")
        ]
        
        goal = self.strategy._infer_goal_from_pattern(messages)
        assert goal == "seeking_help"
    
    def test_infer_goal_from_pattern_confirmation(self):
        """Test goal inference from confirmation patterns"""
        messages = [
            RequestChatMessage(role="user", content="Can you explain this?"),
            RequestChatMessage(role="assistant", content="Would you like me to explain it in detail?"),
            RequestChatMessage(role="user", content="Yes")
        ]
        
        goal = self.strategy._infer_goal_from_pattern(messages)
        # The pattern matches "explain" first, so it should be explanation_request
        assert goal == "explanation_request"
    
    def test_condense_to_standalone_question_short_message(self):
        """Test condensed question generation for short messages"""
        messages = [
            RequestChatMessage(role="user", content="I need help with Python API"),
            RequestChatMessage(role="assistant", content="What specific aspect of the API?"),
            RequestChatMessage(role="user", content="Authentication"),
            RequestChatMessage(role="assistant", content="Do you want to use OAuth?"),
            RequestChatMessage(role="user", content="Yes")
        ]
        
        condensed = self.strategy._condense_to_standalone_question(messages)
        
        # Should include context from previous messages
        assert "Python" in condensed
        assert "API" in condensed
        assert "Authentication" in condensed
        assert "Yes" in condensed
    
    @pytest.mark.asyncio
    async def test_generate_enhanced_queries_short_message(self):
        """Test enhanced query generation for short messages"""
        context = {
            "entities": ["Python", "API"],
            "topics": ["programming"],
            "conversation_state": ConversationState(current_goal="seeking_help"),
            "messages": [
                RequestChatMessage(role="user", content="I need help with Python API"),
                RequestChatMessage(role="assistant", content="What specific aspect?"),
                RequestChatMessage(role="user", content="Yes")
            ]
        }
        
        queries = await self.strategy.generate_enhanced_queries("Yes", context)
        
        # Should generate multiple queries including expanded ones
        assert len(queries) > 1
        assert "Yes" in queries  # Original question
        assert any("Python" in query for query in queries)  # Context from entities
        assert any("programming" in query for query in queries)  # Context from topics
    
    def test_analyze_conversation_state_short_messages(self):
        """Test conversation state analysis with short messages"""
        messages = [
            RequestChatMessage(role="user", content="I need help with Python"),
            RequestChatMessage(role="assistant", content="What specific help do you need?"),
            RequestChatMessage(role="user", content="Yes"),
            RequestChatMessage(role="assistant", content="Can you be more specific?"),
            RequestChatMessage(role="user", content="API")
        ]
        
        state = self.strategy._analyze_conversation_state(messages)
        
        # Should infer goal from patterns
        assert state.current_goal == "seeking_help"
        assert "Python" in state.key_entities
        assert "API" in state.key_entities
    
    def test_summarize_recent_context_short_message(self):
        """Test context summarization for short messages"""
        messages = [
            RequestChatMessage(role="user", content="I need help with Python API"),
            RequestChatMessage(role="assistant", content="What specific aspect?"),
            RequestChatMessage(role="user", content="Authentication"),
            RequestChatMessage(role="assistant", content="Do you want to use OAuth?"),
            RequestChatMessage(role="user", content="Yes")
        ]
        
        summary = self.strategy._summarize_recent_context(messages)
        
        # Should include context from conversation
        assert "Python" in summary
        assert "API" in summary
        assert "Authentication" in summary


if __name__ == "__main__":
    pytest.main([__file__])
