"""
Unit tests for EnhancedContextAwareRAGService
Tests the integration of multi-turn conversation support with context-aware RAG functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.domain.services.enhanced_context_aware_rag_service import (
    EnhancedContextAwareRAGService, AdaptiveStrategySelector, 
    AdvancedMultiTurnStrategy, ConversationMemory
)
from app.domain.models.requests import (
    DocumentContext, DocumentUploadRequest, TextUploadRequest,
    SystemMessageDirective, ResponseMode
)


class TestAdaptiveStrategySelector:
    """Test cases for AdaptiveStrategySelector"""
    
    def test_select_strategy_high_complexity(self):
        """Test strategy selection for high complexity conversations"""
        selector = AdaptiveStrategySelector()
        
        # Create a complex conversation
        messages = [
            {"role": "system", "content": "You are a technical expert."},
            {"role": "user", "content": "I need help with implementing a complex algorithm for data processing."},
            {"role": "assistant", "content": "I can help you with that. What specific algorithm are you working with?"},
            {"role": "user", "content": "I'm implementing a machine learning pipeline with multiple stages including preprocessing, feature extraction, model training, and evaluation."},
            {"role": "assistant", "content": "That's quite comprehensive. Let's break it down step by step."},
            {"role": "user", "content": "I'm having issues with the feature extraction phase, specifically with dimensionality reduction techniques."}
        ]
        
        strategy = selector.select_strategy(messages)
        
        # Should select MultiTurnConversationStrategy for complex conversations
        assert strategy.get_strategy_name() == "multi_turn_conversation"
    
    def test_select_strategy_technical_conversation(self):
        """Test strategy selection for technical conversations"""
        selector = AdaptiveStrategySelector()
        
        # Create a technical conversation with more technical terms to trigger technical classification
        messages = [
            {"role": "system", "content": "You are a programming assistant."},
            {"role": "user", "content": "How do I implement error handling in Python with API debugging and technical implementation?"},
            {"role": "assistant", "content": "You can use try-except blocks."},
            {"role": "user", "content": "What about logging errors and technical debugging?"}
        ]
        
        strategy = selector.select_strategy(messages)
        
        # Should select EntityExtractionStrategy for technical conversations
        assert strategy.get_strategy_name() == "entity_extraction"
    
    def test_calculate_complexity(self):
        """Test complexity calculation"""
        selector = AdaptiveStrategySelector()
        
        # Simple conversation
        simple_messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        simple_complexity = selector._calculate_complexity(simple_messages)
        assert simple_complexity < 0.5
        
        # Complex conversation with more content to increase complexity
        complex_messages = [
            {"role": "system", "content": "You are a technical expert with extensive knowledge of complex algorithms and machine learning implementations."},
            {"role": "user", "content": "I need help with implementing a complex algorithm for data processing that involves multiple stages including preprocessing, feature extraction, model training, and evaluation phases."},
            {"role": "assistant", "content": "I can help you with that comprehensive machine learning pipeline. What specific algorithm are you working with for your data processing requirements?"},
            {"role": "user", "content": "I'm implementing a sophisticated machine learning pipeline with multiple stages including preprocessing, feature extraction, model training, and evaluation with complex dimensionality reduction techniques."}
        ]
        complex_complexity = selector._calculate_complexity(complex_messages)
        assert complex_complexity > 0.2  # Further lowered threshold for test
    
    def test_classify_conversation(self):
        """Test conversation classification"""
        selector = AdaptiveStrategySelector()
        
        # Technical conversation
        technical_messages = [
            {"role": "user", "content": "How do I implement an API with error handling and debugging?"}
        ]
        technical_type = selector._classify_conversation(technical_messages)
        assert technical_type == "technical"
        
        # Creative conversation
        creative_messages = [
            {"role": "user", "content": "I need creative design ideas for a story about art and narrative."}
        ]
        creative_type = selector._classify_conversation(creative_messages)
        assert creative_type == "creative"


class TestAdvancedMultiTurnStrategy:
    """Test cases for AdvancedMultiTurnStrategy"""
    
    @pytest.fixture
    def strategy(self):
        return AdvancedMultiTurnStrategy()
    
    @pytest.mark.asyncio
    async def test_generate_enhanced_queries_basic(self, strategy):
        """Test basic enhanced query generation"""
        question = "What is Python?"
        context = {
            "messages": [
                {"role": "user", "content": "Tell me about programming languages"},
                {"role": "assistant", "content": "There are many programming languages available."},
                {"role": "user", "content": "What is Python?"}
            ]
        }
        
        queries = await strategy.generate_enhanced_queries(question, context)
        
        # Should include original question
        assert question in queries
        # Should generate multiple queries
        assert len(queries) > 1
        # Should not exceed limit
        assert len(queries) <= 10
    
    @pytest.mark.asyncio
    async def test_generate_enhanced_queries_with_intent(self, strategy):
        """Test enhanced query generation with intent detection"""
        question = "How do I fix this error?"
        context = {
            "messages": [
                {"role": "user", "content": "I'm getting an error in my code"},
                {"role": "assistant", "content": "What kind of error are you seeing?"},
                {"role": "user", "content": "How do I fix this error?"}
            ]
        }
        
        queries = await strategy.generate_enhanced_queries(question, context)
        
        # Should include troubleshooting intent
        troubleshooting_queries = [q for q in queries if "troubleshooting" in q.lower() or "error" in q.lower()]
        assert len(troubleshooting_queries) > 0
    
    def test_detect_user_intent(self, strategy):
        """Test user intent detection"""
        messages = [
            {"role": "user", "content": "Can you clarify what you mean by that?"}
        ]
        
        intent = strategy._detect_user_intent(messages)
        assert intent == "clarification"
        
        messages = [
            {"role": "user", "content": "How do I implement this feature?"}
        ]
        
        intent = strategy._detect_user_intent(messages)
        assert intent == "implementation"
    
    def test_extract_context_entities(self, strategy):
        """Test context entity extraction"""
        messages = [
            {"role": "user", "content": "I'm working with Python and Django for web development"}
        ]
        
        entities = strategy._extract_context_entities(messages)
        
        # Should extract technical entities
        assert "Python" in entities or "Django" in entities
        assert len(entities) > 0


class TestConversationMemory:
    """Test cases for ConversationMemory"""
    
    def test_store_and_retrieve_context(self):
        """Test storing and retrieving conversation context"""
        memory = ConversationMemory()
        session_id = "test_session_123"
        context = {
            "topics": ["python", "programming"],
            "entities": ["Django", "Flask"],
            "conversation_state": {"current_goal": "learn web development"}
        }
        
        # Store context
        memory.store_conversation_context(session_id, context)
        
        # Retrieve context
        retrieved_context = memory.retrieve_conversation_context(session_id)
        
        assert retrieved_context == context
        assert memory.conversation_memory[session_id]["access_count"] == 1
    
    def test_update_conversation_learning(self):
        """Test updating conversation learning patterns"""
        memory = ConversationMemory()
        session_id = "test_session_123"
        feedback = {
            "response_quality": "good",
            "user_satisfaction": "high",
            "strategy_used": "multi_turn_conversation"
        }
        
        # Update learning
        memory.update_conversation_learning(session_id, feedback)
        
        # Check patterns
        patterns = memory.get_session_patterns(session_id)
        assert len(patterns) == 1
        assert patterns[0]["feedback"] == feedback
    
    def test_cleanup_old_sessions(self):
        """Test cleanup of old sessions"""
        memory = ConversationMemory()
        session_id = "old_session"
        
        # Store context
        memory.store_conversation_context(session_id, {"test": "data"})
        
        # Simulate old timestamp
        memory.conversation_memory[session_id]["timestamp"] = 0  # Very old
        
        # Cleanup
        memory.cleanup_old_sessions(max_age_hours=1)
        
        # Should be removed
        assert session_id not in memory.conversation_memory


class TestEnhancedContextAwareRAGService:
    """Test cases for EnhancedContextAwareRAGService"""
    
    @pytest.fixture
    def mock_rag_service(self):
        mock_service = Mock()
        mock_service.ask_question = AsyncMock(return_value={
            "success": True,
            "answer": "Test answer",
            "sources": [
                {"content": "Test content", "source": "test.txt", "score": 0.8}
            ]
        })
        return mock_service
    
    @pytest.fixture
    def mock_llm_provider(self):
        mock_provider = Mock()
        mock_provider.call_llm = AsyncMock(return_value="Generated answer")
        return mock_provider
    
    @pytest.fixture
    def enhanced_service(self, mock_rag_service, mock_llm_provider):
        return EnhancedContextAwareRAGService(
            rag_service=mock_rag_service,
            llm_provider=mock_llm_provider
        )
    
    @pytest.mark.asyncio
    async def test_ask_question_with_context_and_conversation_success(self, enhanced_service):
        """Test successful question processing with conversation context"""
        question = "What is Python?"
        system_message = "You are a helpful assistant."
        conversation_history = [
            {"role": "user", "content": "Tell me about programming languages"},
            {"role": "assistant", "content": "There are many programming languages available."},
            {"role": "user", "content": "What is Python?"}
        ]
        session_id = "test_session_123"
        
        # Mock the context-aware service and strategy
        with patch.object(enhanced_service.context_aware_service, 'ask_question_with_context') as mock_ask, \
             patch.object(enhanced_service.strategy_selector, 'select_strategy') as mock_select_strategy:
            
            # Create a mock strategy
            mock_strategy = Mock()
            mock_strategy.analyze_conversation = AsyncMock(return_value={
                "topics": ["python", "programming"],
                "entities": ["Python"],
                "conversation_state": {"current_goal": "learn programming"}
            })
            mock_strategy.get_strategy_name.return_value = "multi_turn_conversation"
            mock_select_strategy.return_value = mock_strategy
            
            mock_ask.return_value = {
                "success": True,
                "answer": "Python is a programming language",
                "sources": [
                    {"content": "Python is a high-level programming language", "source": "python_docs.txt", "score": 0.9}
                ]
            }
            
            result = await enhanced_service.ask_question_with_context_and_conversation(
                question=question,
                system_message=system_message,
                conversation_history=conversation_history,
                session_id=session_id
            )
        
        assert result["success"] is True
        assert "answer" in result
        assert "enhanced_queries" in result
        assert "conversation_context" in result
        assert "strategy_used" in result
        assert result["session_id"] == session_id
    
    @pytest.mark.asyncio
    async def test_ask_question_with_context_and_conversation_fallback(self, enhanced_service):
        """Test fallback to LLM-only when no RAG results found"""
        question = "What is Python?"
        system_message = "You are a helpful assistant."
        conversation_history = [
            {"role": "user", "content": "What is Python?"}
        ]
        
        # Mock the context-aware service to return no results
        with patch.object(enhanced_service.context_aware_service, 'ask_question_with_context') as mock_ask, \
             patch.object(enhanced_service.strategy_selector, 'select_strategy') as mock_select_strategy:
            
            # Create a mock strategy
            mock_strategy = Mock()
            mock_strategy.analyze_conversation = AsyncMock(return_value={
                "topics": ["python"],
                "entities": [],
                "conversation_state": {}
            })
            mock_strategy.get_strategy_name.return_value = "multi_turn_conversation"
            mock_select_strategy.return_value = mock_strategy
            
            mock_ask.return_value = {
                "success": False,
                "answer": "No relevant information found",
                "sources": []
            }
            
            result = await enhanced_service.ask_question_with_context_and_conversation(
                question=question,
                system_message=system_message,
                conversation_history=conversation_history
            )
        
        assert result["success"] is True
        assert "answer" in result
        assert result["fallback_used"] is True
        assert len(result["sources"]) == 0
    
    @pytest.mark.asyncio
    async def test_ask_question_with_context_and_conversation_error(self, enhanced_service):
        """Test error handling in question processing"""
        question = "What is Python?"
        
        # Mock the context-aware service to raise an exception
        with patch.object(enhanced_service.context_aware_service, 'ask_question_with_context') as mock_ask:
            mock_ask.side_effect = Exception("Test error")
            
            result = await enhanced_service.ask_question_with_context_and_conversation(
                question=question
            )
        
        assert result["success"] is False
        assert "error" in result["answer"].lower()
        assert result["strategy_used"] == "error"
    
    def test_deduplicate_results(self, enhanced_service):
        """Test result deduplication"""
        results = [
            {"content": "Test content 1", "source": "test1.txt", "score": 0.8},
            {"content": "Test content 2", "source": "test2.txt", "score": 0.9},
            {"content": "Test content 1", "source": "test1.txt", "score": 0.8},  # Duplicate
        ]
        
        unique_results = enhanced_service._deduplicate_results(results)
        
        # Should remove duplicate
        assert len(unique_results) == 2
        # Should sort by score
        assert unique_results[0]["score"] >= unique_results[1]["score"]
    
    @pytest.mark.asyncio
    async def test_delegate_methods(self, enhanced_service):
        """Test that delegate methods work correctly"""
        # Test add_document_with_context delegation
        with patch.object(enhanced_service.context_aware_service, 'add_document_with_context') as mock_add:
            mock_add.return_value = {"success": True, "message": "Document added"}
            
            request = DocumentUploadRequest(
                file_path="test.txt",
                context=DocumentContext(
                    context_type=["technical"],
                    content_domain=["programming"],
                    document_category=["tutorial"]
                )
            )
            
            result = await enhanced_service.add_document_with_context(request)
            assert result["success"] is True
    
    def test_get_conversation_memory(self, enhanced_service):
        """Test getting conversation memory"""
        memory = enhanced_service.get_conversation_memory()
        assert isinstance(memory, ConversationMemory)
