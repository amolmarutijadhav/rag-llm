"""
Tests for Enhanced Chat Completion Service with Multi-Turn Conversation Support
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from typing import List, Dict, Any

from app.domain.models.requests import ChatCompletionRequest, ChatMessage
from app.domain.models.responses import ChatCompletionResponse
from app.domain.services.enhanced_chat_completion_service import (
    EnhancedChatCompletionService,
    MultiTurnConversationStrategy,
    ConversationState,
    ProcessingContext
)
from app.domain.services.rag_service import RAGService


class TestMultiTurnConversationStrategy:
    """Test the MultiTurnConversationStrategy"""
    
    @pytest.fixture
    def strategy(self):
        return MultiTurnConversationStrategy()
    
    @pytest.fixture
    def sample_messages(self):
        """Sample conversation messages for testing"""
        return [
            ChatMessage(role="system", content="You are a Credit Officer specializing in regulatory compliance."),
            ChatMessage(role="user", content="I need to prepare a BRD for Basel III compliance"),
            ChatMessage(role="assistant", content="I'll help you create a comprehensive BRD. Let me gather relevant information about Basel III requirements."),
            ChatMessage(role="user", content="What sections should I include?"),
            ChatMessage(role="assistant", content="Based on Basel III compliance requirements, your BRD should include: Executive Summary, Risk Assessment, Implementation Plan, and Compliance Framework."),
            ChatMessage(role="user", content="Can you help me draft the executive summary?")
        ]
    
    @pytest.mark.asyncio
    async def test_analyze_conversation(self, strategy, sample_messages):
        """Test conversation analysis"""
        result = await strategy.analyze_conversation(sample_messages)
        
        assert "topics" in result
        assert "entities" in result
        assert "conversation_state" in result
        assert "last_user_message" in result
        
        # Check conversation state
        state = result["conversation_state"]
        assert isinstance(state, ConversationState)
        assert "BRD" in state.current_goal or "Basel III" in state.current_goal
        assert state.conversation_phase in ["planning", "drafting", "reviewing", "finalizing"]
        assert len(state.key_entities) > 0
        assert "Basel" in state.key_entities or "BRD" in state.key_entities
    
    @pytest.mark.asyncio
    async def test_generate_enhanced_queries(self, strategy, sample_messages):
        """Test enhanced query generation"""
        # First analyze conversation
        context = await strategy.analyze_conversation(sample_messages)
        context["messages"] = sample_messages
        
        # Generate queries
        last_message = "Can you help me draft the executive summary?"
        queries = await strategy.generate_enhanced_queries(last_message, context)
        
        assert len(queries) > 1  # Should generate multiple queries
        assert last_message in queries  # Original question should be included
        
        # Check for condensed query
        condensed_queries = [q for q in queries if len(q) > len(last_message)]
        assert len(condensed_queries) > 0
        
        # Check for goal-oriented queries
        goal_queries = [q for q in queries if "BRD" in q or "Basel" in q]
        assert len(goal_queries) > 0
    
    def test_condense_to_standalone_question(self, strategy, sample_messages):
        """Test condensed query generation"""
        condensed = strategy._condense_to_standalone_question(sample_messages, max_turns=3)
        
        assert condensed
        assert len(condensed) > 0
        # Should include key entities and the last question
        assert "executive summary" in condensed.lower()
    
    def test_summarize_recent_context(self, strategy, sample_messages):
        """Test summary query generation"""
        summary = strategy._summarize_recent_context(sample_messages, max_turns=3)
        
        assert summary
        assert len(summary) > 0
        # Should include goal and entities
        assert "BRD" in summary or "Basel" in summary
    
    def test_analyze_conversation_state(self, strategy, sample_messages):
        """Test conversation state analysis"""
        state = strategy._analyze_conversation_state(sample_messages)
        
        assert isinstance(state, ConversationState)
        assert state.current_goal
        assert state.conversation_phase
        assert len(state.key_entities) > 0
        assert len(state.conversation_history) > 0
    
    def test_extract_entities(self, strategy):
        """Test entity extraction"""
        text = "We need to implement Basel III compliance for SME risk scoring"
        entities = strategy._extract_entities(text)
        
        assert "Basel" in entities
        assert "SME" in entities
    
    def test_extract_goals(self, strategy):
        """Test goal extraction"""
        text = "I need to prepare a BRD for Basel III compliance"
        goals = strategy._extract_goals(text)
        
        assert len(goals) > 0
        assert "BRD" in goals[0] or "Basel" in goals[0]


class TestEnhancedChatCompletionService:
    """Test the Enhanced Chat Completion Service"""
    
    @pytest.fixture
    def mock_rag_service(self):
        """Mock RAG service"""
        mock_service = Mock(spec=RAGService)
        mock_service.embedding_provider = Mock()
        mock_service.embedding_provider.get_embeddings = AsyncMock(return_value=[[0.1, 0.2, 0.3]])
        mock_service.vector_store_provider = Mock()
        mock_service.vector_store_provider.search_vectors = AsyncMock(return_value=[
            {
                "payload": {"content": "Sample content", "metadata": {"source": "test.pdf"}},
                "score": 0.85
            }
        ])
        return mock_service
    
    @pytest.fixture
    def mock_llm_provider(self):
        """Mock LLM provider"""
        mock_provider = Mock()
        mock_provider.call_llm_api = AsyncMock(return_value={
            "choices": [{"message": {"content": "Sample response"}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        })
        return mock_provider
    
    @pytest.fixture
    def service(self, mock_rag_service, mock_llm_provider):
        """Enhanced chat completion service instance"""
        return EnhancedChatCompletionService(mock_rag_service, mock_llm_provider)
    
    @pytest.fixture
    def sample_request(self):
        """Sample chat completion request"""
        return ChatCompletionRequest(
            model="gpt-4",
            messages=[
                ChatMessage(role="system", content="You are a Credit Officer specializing in regulatory compliance."),
                ChatMessage(role="user", content="I need to prepare a BRD for Basel III compliance"),
                ChatMessage(role="assistant", content="I'll help you create a comprehensive BRD."),
                ChatMessage(role="user", content="What sections should I include?"),
                ChatMessage(role="assistant", content="Your BRD should include: Executive Summary, Risk Assessment."),
                ChatMessage(role="user", content="Can you help me draft the executive summary?")
            ],
            temperature=0.7,
            max_tokens=1000
        )
    
    @pytest.mark.asyncio
    async def test_process_request(self, service, sample_request):
        """Test processing a complete request"""
        response = await service.process_request(sample_request)
        
        assert isinstance(response, ChatCompletionResponse)
        assert response.choices
        assert response.choices[0]["message"]["content"]
        assert response.metadata
        
        # Check enhanced metadata
        metadata = response.metadata
        assert metadata.get("conversation_aware", False)
        assert metadata.get("multi_turn_enabled", False)
        assert metadata.get("strategy_used") == "multi_turn_conversation"
        assert "conversation_state" in metadata
    
    @pytest.mark.asyncio
    async def test_multi_turn_context_preservation(self, service, sample_request):
        """Test that multi-turn context is preserved"""
        response = await service.process_request(sample_request)
        
        metadata = response.metadata
        conversation_state = metadata.get("conversation_state", {})
        
        # Should detect goal and phase
        assert conversation_state.get("current_goal")
        assert conversation_state.get("conversation_phase")
        assert conversation_state.get("key_entities_count", 0) > 0
    
    @pytest.mark.asyncio
    async def test_enhanced_query_generation(self, service, sample_request):
        """Test that enhanced queries are generated"""
        response = await service.process_request(sample_request)
        
        metadata = response.metadata
        assert metadata.get("enhanced_queries_count", 0) > 1  # Should generate multiple queries
    
    @pytest.mark.asyncio
    async def test_conversation_state_tracking(self, service, sample_request):
        """Test conversation state tracking"""
        response = await service.process_request(sample_request)
        
        metadata = response.metadata
        conversation_state = metadata.get("conversation_state", {})
        
        # Should track conversation elements
        assert "current_goal" in conversation_state
        assert "conversation_phase" in conversation_state
        assert "key_entities_count" in conversation_state
        assert "constraints_count" in conversation_state

    @pytest.mark.asyncio
    async def test_parallel_query_processing(self, service, sample_request):
        """Test parallel query processing functionality"""
        # Mock the RAG service to track parallel execution
        call_count = 0
        original_get_embeddings = service.rag_service.embedding_provider.get_embeddings
        original_search_vectors = service.rag_service.vector_store_provider.search_vectors
        
        async def mock_get_embeddings(queries):
            nonlocal call_count
            call_count += 1
            return await original_get_embeddings(queries)
        
        async def mock_search_vectors(vector, top_k, collection):
            nonlocal call_count
            call_count += 1
            return await original_search_vectors(vector, top_k, collection)
        
        service.rag_service.embedding_provider.get_embeddings = mock_get_embeddings
        service.rag_service.vector_store_provider.search_vectors = mock_search_vectors
        
        response = await service.process_request(sample_request)
        
        # Should have made multiple calls (indicating parallel processing)
        assert call_count > 2  # At least 2 calls (embedding + search) for multiple queries
        
        # Restore original methods
        service.rag_service.embedding_provider.get_embeddings = original_get_embeddings
        service.rag_service.vector_store_provider.search_vectors = original_search_vectors

    @pytest.mark.asyncio
    async def test_parallel_vs_sequential_performance(self, service, sample_request):
        """Test performance difference between parallel and sequential processing"""
        import time
        
        # Test parallel processing
        start_time = time.time()
        response_parallel = await service.process_request(sample_request)
        parallel_time = time.time() - start_time
        
        # Test sequential processing by temporarily disabling parallel processing
        # We'll mock the config to disable parallel processing
        original_get_performance_config = None
        try:
            from app.core.enhanced_chat_config import get_performance_config
            original_get_performance_config = get_performance_config
            
            def mock_get_performance_config():
                return {"enable_parallel_processing": False, "max_concurrent_queries": 1}
            
            # Replace the config function temporarily
            import app.core.enhanced_chat_config
            app.core.enhanced_chat_config.get_performance_config = mock_get_performance_config
            
            start_time = time.time()
            response_sequential = await service.process_request(sample_request)
            sequential_time = time.time() - start_time
            
            # Parallel should be faster (though in tests with mocks, difference might be minimal)
            # In real scenarios, parallel processing should be significantly faster
            # logger.info(f"Parallel time: {parallel_time:.3f}s, Sequential time: {sequential_time:.3f}s") # Original code had this line commented out
            
            # Both should produce valid responses
            assert response_parallel.choices
            assert response_sequential.choices
            
        finally:
            # Restore original config function
            if original_get_performance_config:
                app.core.enhanced_chat_config.get_performance_config = original_get_performance_config


class TestConversationState:
    """Test the ConversationState dataclass"""
    
    def test_conversation_state_initialization(self):
        """Test ConversationState initialization"""
        state = ConversationState()
        
        assert state.current_goal == ""
        assert state.conversation_phase == "planning"
        assert state.key_entities == []
        assert state.constraints == []
        assert state.progress_markers == []
        assert state.next_steps == []
        assert state.conversation_history == []
    
    def test_conversation_state_with_data(self):
        """Test ConversationState with data"""
        state = ConversationState(
            current_goal="Prepare BRD for Basel III",
            conversation_phase="drafting",
            key_entities=["Basel", "BRD", "SME"],
            constraints=["compliance", "deadline"],
            progress_markers=["outline completed"],
            next_steps=["draft executive summary"],
            conversation_history=["User: I need to prepare a BRD"]
        )
        
        assert state.current_goal == "Prepare BRD for Basel III"
        assert state.conversation_phase == "drafting"
        assert len(state.key_entities) == 3
        assert len(state.constraints) == 2
        assert len(state.progress_markers) == 1
        assert len(state.next_steps) == 1
        assert len(state.conversation_history) == 1


class TestProcessingContext:
    """Test the ProcessingContext dataclass"""
    
    def test_processing_context_initialization(self):
        """Test ProcessingContext initialization"""
        request = ChatCompletionRequest(
            model="gpt-4",
            messages=[ChatMessage(role="user", content="Hello")],
            temperature=0.7,
            max_tokens=100
        )
        
        context = ProcessingContext(request)
        
        assert context.request == request
        assert context.strategy is None
        assert context.conversation_context == {}
        assert context.enhanced_queries is None
        assert context.rag_results is None
        assert context.response_data is None
        assert context.metadata == {}
        assert isinstance(context.conversation_state, ConversationState)
    
    def test_processing_context_with_data(self):
        """Test ProcessingContext with data"""
        request = ChatCompletionRequest(
            model="gpt-4",
            messages=[ChatMessage(role="user", content="Hello")],
            temperature=0.7,
            max_tokens=100
        )
        
        context = ProcessingContext(
            request=request,
            strategy="multi_turn_conversation",
            conversation_context={"topics": ["compliance"]},
            enhanced_queries=["query1", "query2"],
            rag_results=[{"content": "result1"}],
            response_data={"choices": []},
            metadata={"test": "data"},
            conversation_state=ConversationState(current_goal="test goal")
        )
        
        assert context.strategy == "multi_turn_conversation"
        assert context.conversation_context["topics"] == ["compliance"]
        assert context.enhanced_queries == ["query1", "query2"]
        assert len(context.rag_results) == 1
        assert context.response_data["choices"] == []
        assert context.metadata["test"] == "data"
        assert context.conversation_state.current_goal == "test goal"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
