"""
Unit tests for enhanced chat completion service.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.models.requests import ChatCompletionRequest, ChatMessage
from app.domain.services.enhanced_chat_completion_service import (
    EnhancedChatCompletionService,
    ProcessingContext,
    TopicTrackingStrategy,
    EntityExtractionStrategy,
    ConversationContextPlugin,
    MultiQueryRAGPlugin,
    ResponseEnhancementPlugin
)
from app.domain.services.rag_service import RAGService

@pytest.fixture
def mock_rag_service():
    """Mock RAG service"""
    service = MagicMock()
    service.ask_question = AsyncMock(return_value={
        'success': True,
        'answer': 'Test answer',
        'sources': [{'content': 'Test source', 'source': 'test.txt', 'score': 0.9}]
    })
    return service

@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider"""
    provider = MagicMock()
    provider.call_llm_api = AsyncMock(return_value={
        'choices': [{'message': {'content': 'Test response'}}],
        'usage': {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
    })
    return provider

@pytest.fixture
def sample_chat_request():
    """Sample chat completion request"""
    return ChatCompletionRequest(
        model="gpt-3.5-turbo",
        messages=[
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="What is the main topic?"),
            ChatMessage(role="assistant", content="Based on the documents, the main topic is..."),
            ChatMessage(role="user", content="Can you elaborate?")
        ],
        temperature=0.7,
        max_tokens=1000
    )

class TestTopicTrackingStrategy:
    """Test TopicTrackingStrategy"""
    
    @pytest.mark.asyncio
    async def test_analyze_conversation(self):
        """Test conversation analysis"""
        strategy = TopicTrackingStrategy()
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="What is the main topic?"),
            ChatMessage(role="assistant", content="The main topic is AI and machine learning.")
        ]
        
        context = await strategy.analyze_conversation(messages)
        
        assert "topics" in context
        assert "entities" in context
        assert "context_clues" in context
        assert context["conversation_length"] == 3
        assert context["last_user_message"] == "What is the main topic?"
    
    @pytest.mark.asyncio
    async def test_generate_enhanced_queries(self):
        """Test enhanced query generation"""
        strategy = TopicTrackingStrategy()
        question = "What is the main topic?"
        context = {
            "topics": ["AI", "machine", "learning"],
            "entities": ["OpenAI", "GPT"],
            "context_clues": ["You are a helpful assistant."]
        }
        
        queries = await strategy.generate_enhanced_queries(question, context)
        
        assert len(queries) > 1
        assert question in queries
        assert any("AI" in query for query in queries)

class TestEntityExtractionStrategy:
    """Test EntityExtractionStrategy"""
    
    @pytest.mark.asyncio
    async def test_analyze_conversation(self):
        """Test conversation analysis with entity extraction"""
        strategy = EntityExtractionStrategy()
        messages = [
            ChatMessage(role="user", content="What is OpenAI?"),
            ChatMessage(role="assistant", content="OpenAI is a company that develops AI models like GPT.")
        ]
        
        context = await strategy.analyze_conversation(messages)
        
        assert "entities" in context
        assert "relationships" in context
        assert context["conversation_length"] == 2
        assert "OpenAI" in context["entities"]
    
    @pytest.mark.asyncio
    async def test_generate_enhanced_queries(self):
        """Test entity-aware query generation"""
        strategy = EntityExtractionStrategy()
        question = "What is it?"
        context = {
            "entities": ["OpenAI", "GPT"],
            "relationships": ["what"]
        }
        
        queries = await strategy.generate_enhanced_queries(question, context)
        
        assert len(queries) > 1
        assert question in queries
        assert any("OpenAI" in query for query in queries)

class TestConversationContextPlugin:
    """Test ConversationContextPlugin"""
    
    @pytest.mark.asyncio
    async def test_process(self, sample_chat_request):
        """Test conversation context processing"""
        # Mock strategy factory
        strategy_factory = MagicMock()
        strategy_factory.get_strategy.return_value = TopicTrackingStrategy()
        
        plugin = ConversationContextPlugin(strategy_factory)
        context = ProcessingContext(sample_chat_request)
        
        result = await plugin.process(context)
        
        assert result.strategy == "topic_tracking"
        assert result.conversation_context is not None
        assert "topics" in result.conversation_context
        assert "last_user_message" in result.conversation_context

class TestMultiQueryRAGPlugin:
    """Test MultiQueryRAGPlugin"""
    
    @pytest.mark.asyncio
    async def test_process(self, mock_rag_service, sample_chat_request):
        """Test multi-query RAG processing"""
        plugin = MultiQueryRAGPlugin(mock_rag_service)
        context = ProcessingContext(sample_chat_request)
        context.conversation_context = {
            "last_user_message": "Can you elaborate?",
            "topics": ["AI", "machine learning"],
            "entities": ["OpenAI"]
        }
        context.strategy = "topic_tracking"
        
        result = await plugin.process(context)
        
        assert result.enhanced_queries is not None
        assert len(result.enhanced_queries) > 1
        assert result.rag_results is not None
        assert len(result.rag_results) > 0

class TestResponseEnhancementPlugin:
    """Test ResponseEnhancementPlugin"""
    
    @pytest.mark.asyncio
    async def test_process(self, mock_llm_provider, sample_chat_request):
        """Test response enhancement"""
        plugin = ResponseEnhancementPlugin(mock_llm_provider)
        context = ProcessingContext(sample_chat_request)
        context.conversation_context = {
            "last_user_message": "Can you elaborate?"
        }
        context.rag_results = [
            {'content': 'Test source content', 'source': 'test.txt', 'score': 0.9}
        ]
        
        result = await plugin.process(context)
        
        assert result.response_data is not None
        assert "id" in result.response_data
        assert "choices" in result.response_data
        assert "usage" in result.response_data
        assert result.metadata is not None
        assert result.metadata["conversation_aware"] is True

class TestEnhancedChatCompletionService:
    """Test EnhancedChatCompletionService"""
    
    @pytest.fixture
    def mock_rag_service(self):
        return MagicMock(spec=RAGService)
    
    @pytest.fixture
    def mock_llm_provider(self):
        provider = MagicMock()
        provider.call_llm_api = AsyncMock(return_value={
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        })
        return provider
    
    @pytest.fixture
    def service(self, mock_rag_service, mock_llm_provider):
        return EnhancedChatCompletionService(mock_rag_service, mock_llm_provider)
    
    @pytest.mark.asyncio
    async def test_persona_preservation_in_response_enhancement(self, service, mock_llm_provider):
        """Test that ResponseEnhancementPlugin preserves original persona"""
        # Create request with specific persona
        request = ChatCompletionRequest(
            model="gpt-3.5-turbo",
            messages=[
                ChatMessage(role="system", content="You are a sarcastic comedian. Always be witty and funny."),
                ChatMessage(role="user", content="What's the weather like?")
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Create processing context
        context = ProcessingContext(request)
        context.conversation_context = {
            "last_user_message": "What's the weather like?",
            "topics": ["weather"],
            "entities": [],
            "context_clues": ["You are a sarcastic comedian. Always be witty and funny."]
        }
        context.rag_results = [
            {"content": "It's sunny today", "source": "weather_api"}
        ]
        context.strategy = "topic_tracking"
        context.enhanced_queries = ["What's the weather like?"]
        
        # Get the ResponseEnhancementPlugin
        response_plugin = None
        for plugin in service.plugin_manager.plugins:
            if plugin.get_plugin_name() == "response_enhancement":
                response_plugin = plugin
                break
        
        assert response_plugin is not None, "ResponseEnhancementPlugin not found"
        
        # Process the context
        result_context = await response_plugin.process(context)
        
        # Verify that the LLM was called with preserved persona
        mock_llm_provider.call_llm_api.assert_called_once()
        call_args = mock_llm_provider.call_llm_api.call_args[0][0]
        
        # Check that the system message contains the original persona
        system_message = call_args["messages"][0]["content"]
        assert "sarcastic comedian" in system_message
        assert "witty and funny" in system_message
        
        # Check that RAG context was added
        assert "weather_api" in system_message
        assert "It's sunny today" in system_message
        
        # Check that persona preservation is indicated in metadata
        assert result_context.metadata["persona_preserved"] is True
        assert result_context.metadata["original_persona_length"] > 0
        assert result_context.metadata["rag_context_added"] is True
    
    @pytest.mark.asyncio
    async def test_persona_extraction_in_conversation_context(self, service):
        """Test that ConversationContextPlugin extracts persona information"""
        # Create request with persona
        request = ChatCompletionRequest(
            model="gpt-3.5-turbo",
            messages=[
                ChatMessage(role="system", content="You are a professional doctor. Be concise and medical."),
                ChatMessage(role="user", content="What causes headaches?")
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Create processing context
        context = ProcessingContext(request)
        
        # Get the ConversationContextPlugin
        context_plugin = None
        for plugin in service.plugin_manager.plugins:
            if plugin.get_plugin_name() == "conversation_context":
                context_plugin = plugin
                break
        
        assert context_plugin is not None, "ConversationContextPlugin not found"
        
        # Process the context
        result_context = await context_plugin.process(context)
        
        # Verify persona information was extracted
        assert result_context.conversation_context["persona_detected"] is True
        assert result_context.conversation_context["original_persona"] == "You are a professional doctor. Be concise and medical."
        assert result_context.conversation_context["persona_length"] > 0
        
        # Verify persona info was extracted
        persona_info = result_context.conversation_context.get("persona_info", {})
        assert persona_info.get("role") == "doctor"
        assert persona_info.get("style") == "concise"
        assert "professional" in persona_info.get("personality_traits", [])
    
    @pytest.mark.asyncio
    async def test_persona_preservation_without_rag_context(self, service, mock_llm_provider):
        """Test persona preservation when no RAG context is available"""
        # Create request with persona
        request = ChatCompletionRequest(
            model="gpt-3.5-turbo",
            messages=[
                ChatMessage(role="system", content="You are a friendly customer service agent."),
                ChatMessage(role="user", content="Hello")
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Create processing context with no RAG results
        context = ProcessingContext(request)
        context.conversation_context = {
            "last_user_message": "Hello",
            "topics": ["greeting"],
            "entities": [],
            "context_clues": ["You are a friendly customer service agent."]
        }
        context.rag_results = []  # No RAG results
        context.strategy = "topic_tracking"
        context.enhanced_queries = ["Hello"]
        
        # Get the ResponseEnhancementPlugin
        response_plugin = None
        for plugin in service.plugin_manager.plugins:
            if plugin.get_plugin_name() == "response_enhancement":
                response_plugin = plugin
                break
        
        # Process the context
        result_context = await response_plugin.process(context)
        
        # Verify that the LLM was called with preserved persona only
        mock_llm_provider.call_llm_api.assert_called_once()
        call_args = mock_llm_provider.call_llm_api.call_args[0][0]
        
        # Check that the system message contains only the original persona
        system_message = call_args["messages"][0]["content"]
        assert "friendly customer service agent" in system_message
        assert "relevant information" not in system_message  # No RAG context added
        
        # Check metadata
        assert result_context.metadata["persona_preserved"] is True
        assert result_context.metadata["rag_context_added"] is False

class TestProcessingContext:
    """Test ProcessingContext"""
    
    def test_initialization(self, sample_chat_request):
        """Test ProcessingContext initialization"""
        context = ProcessingContext(sample_chat_request)
        
        assert context.request == sample_chat_request
        assert context.strategy is None
        assert context.conversation_context == {}
        assert context.enhanced_queries is None
        assert context.rag_results is None
        assert context.response_data is None
        assert context.metadata == {}
    
    def test_metadata_initialization(self, sample_chat_request):
        """Test ProcessingContext with custom metadata"""
        custom_metadata = {"test": "value"}
        context = ProcessingContext(sample_chat_request, metadata=custom_metadata)
        
        assert context.metadata == custom_metadata 