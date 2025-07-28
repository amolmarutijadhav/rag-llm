import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.domain.models.requests import ChatMessage
from app.domain.services.conversation_aware_rag_service import ConversationAwareRAGService

client = TestClient(app)

@pytest.mark.unit
class TestConversationAwareChat:
    """Test suite for conversation-aware chat completions."""

    @pytest.fixture
    def sample_chat_request(self):
        """Sample chat completion request for testing."""
        return {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "What is Python?"},
                {"role": "assistant", "content": "Python is a programming language."},
                {"role": "user", "content": "How does it compare to Java?"},
                {"role": "assistant", "content": "Python and Java are both programming languages but have different characteristics."},
                {"role": "user", "content": "Tell me more about Python's features."}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }

    @pytest.fixture
    def mock_conversation_aware_rag_service(self):
        """Mock conversation-aware RAG service."""
        mock = Mock(spec=ConversationAwareRAGService)
        mock.ask_question_with_conversation = AsyncMock(return_value={
            "success": True,
            "answer": "Python is a high-level programming language known for its simplicity and readability.",
            "sources": [
                {
                    "content": "Python is a programming language created by Guido van Rossum",
                    "source": "python_docs.txt",
                    "score": 0.95
                }
            ],
            "question": "Tell me more about Python's features.",
            "conversation_context_used": True,
            "conversation_analysis": {
                "strategy_used": "hybrid",
                "confidence_score": 0.8,
                "processing_time_ms": 150.0,
                "topics_found": 2,
                "entities_found": 3,
                "context_clues_found": 1
            },
            "enhanced_queries": {
                "original_query": "Tell me more about Python's features.",
                "enhanced_queries_count": 3,
                "query_generation_method": "conversation_context_enhancement"
            },
            "conversation_context": {
                "topics": ["programming", "technology"],
                "entities": ["Python", "Java", "programming"],
                "context_clues": ["important"],
                "conversation_length": 5
            }
        })
        return mock

    @pytest.mark.asyncio
    async def test_conversation_aware_completions_success(self, sample_chat_request, mock_conversation_aware_rag_service):
        """Test successful conversation-aware chat completions."""
        with patch('app.api.routes.conversation_aware_chat.ConversationAwareRAGService', return_value=mock_conversation_aware_rag_service):
            response = client.post("/chat/conversation-aware-completions", json=sample_chat_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Check basic response structure
            assert data["object"] == "chat.completion"
            assert data["model"] == "gpt-3.5-turbo"
            assert len(data["choices"]) == 1
            assert data["choices"][0]["message"]["role"] == "assistant"
            assert "Python" in data["choices"][0]["message"]["content"]
            
            # Check conversation context information
            assert "conversation_context" in data
            assert data["conversation_context"]["used"] == True
            assert "analysis" in data["conversation_context"]
            assert "enhanced_queries" in data["conversation_context"]
            assert "context_summary" in data["conversation_context"]
            
            # Check sources
            assert "sources" in data
            assert len(data["sources"]) == 1
            assert data["sources"][0]["source"] == "python_docs.txt"

    @pytest.mark.asyncio
    async def test_conversation_aware_completions_fallback(self, sample_chat_request, mock_conversation_aware_rag_service):
        """Test conversation-aware chat completions with fallback."""
        # Mock RAG service to return failure
        mock_conversation_aware_rag_service.ask_question_with_conversation.return_value = {
            "success": False,
            "answer": "Error processing question: Analysis failed",
            "sources": [],
            "question": "Tell me more about Python's features.",
            "conversation_context_used": False,
            "fallback_reason": "Analysis failed"
        }
        
        with patch('app.api.routes.conversation_aware_chat.ConversationAwareRAGService', return_value=mock_conversation_aware_rag_service):
            response = client.post("/chat/conversation-aware-completions", json=sample_chat_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Check fallback response
            assert "couldn't find relevant information" in data["choices"][0]["message"]["content"]
            assert data["conversation_context"]["used"] == False
            assert "fallback_reason" in data["conversation_context"]

    @pytest.mark.asyncio
    async def test_conversation_aware_completions_no_messages(self):
        """Test conversation-aware chat completions with no messages."""
        request = {
            "model": "gpt-3.5-turbo",
            "messages": [],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = client.post("/chat/conversation-aware-completions", json=request)
        
        assert response.status_code == 400
        assert "Messages cannot be empty" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_conversation_aware_completions_no_user_message(self):
        """Test conversation-aware chat completions with no user message."""
        request = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "assistant", "content": "Hello! How can I help you?"}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = client.post("/chat/conversation-aware-completions", json=request)
        
        assert response.status_code == 400
        assert "No user message found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_enhanced_completions_alias(self, sample_chat_request, mock_conversation_aware_rag_service):
        """Test the enhanced completions alias endpoint."""
        with patch('app.api.routes.conversation_aware_chat.ConversationAwareRAGService', return_value=mock_conversation_aware_rag_service):
            response = client.post("/chat/completions-enhanced", json=sample_chat_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Should work exactly like conversation-aware completions
            assert data["object"] == "chat.completion"
            assert "Python" in data["choices"][0]["message"]["content"]
            assert data["conversation_context"]["used"] == True

    @pytest.mark.asyncio
    async def test_conversation_aware_completions_with_different_strategies(self, sample_chat_request, mock_conversation_aware_rag_service):
        """Test conversation-aware completions with different analysis strategies."""
        # Test with topic extraction strategy
        mock_conversation_aware_rag_service.ask_question_with_conversation.return_value = {
            "success": True,
            "answer": "Python is a programming language with many features.",
            "sources": [{"content": "test", "source": "test.txt", "score": 0.9}],
            "question": "Tell me more about Python's features.",
            "conversation_context_used": True,
            "conversation_analysis": {
                "strategy_used": "topic_extraction",
                "confidence_score": 0.7,
                "processing_time_ms": 100.0
            },
            "enhanced_queries": {
                "original_query": "Tell me more about Python's features.",
                "enhanced_queries_count": 2,
                "query_generation_method": "conversation_context_enhancement"
            },
            "conversation_context": {
                "topics": ["programming"],
                "entities": [],
                "context_clues": [],
                "conversation_length": 5
            }
        }
        
        with patch('app.api.routes.conversation_aware_chat.ConversationAwareRAGService', return_value=mock_conversation_aware_rag_service):
            response = client.post("/chat/conversation-aware-completions", json=sample_chat_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Check that topic extraction strategy was used
            assert data["conversation_context"]["analysis"]["strategy_used"] == "topic_extraction"
            assert data["conversation_context"]["context_summary"]["topics"] == ["programming"]

    @pytest.mark.asyncio
    async def test_conversation_aware_completions_error_handling(self, sample_chat_request):
        """Test error handling in conversation-aware completions."""
        # Mock RAG service to raise exception
        with patch('app.api.routes.conversation_aware_chat.ConversationAwareRAGService') as mock_service_class:
            mock_service = Mock()
            mock_service.ask_question_with_conversation = AsyncMock(side_effect=Exception("Service error"))
            mock_service_class.return_value = mock_service
            
            response = client.post("/chat/conversation-aware-completions", json=sample_chat_request)
            
            assert response.status_code == 500
            assert "Service error" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_conversation_aware_completions_response_structure(self, sample_chat_request, mock_conversation_aware_rag_service):
        """Test the complete response structure of conversation-aware completions."""
        with patch('app.api.routes.conversation_aware_chat.ConversationAwareRAGService', return_value=mock_conversation_aware_rag_service):
            response = client.post("/chat/conversation-aware-completions", json=sample_chat_request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Check required fields
            assert "id" in data
            assert "object" in data
            assert "created" in data
            assert "model" in data
            assert "choices" in data
            assert "usage" in data
            assert "sources" in data
            assert "conversation_context" in data
            
            # Check choices structure
            choice = data["choices"][0]
            assert "index" in choice
            assert "message" in choice
            assert "finish_reason" in choice
            assert choice["message"]["role"] == "assistant"
            assert "content" in choice["message"]
            
            # Check usage structure
            usage = data["usage"]
            assert "prompt_tokens" in usage
            assert "completion_tokens" in usage
            assert "total_tokens" in usage
            
            # Check conversation context structure
            context = data["conversation_context"]
            assert "used" in context
            assert "analysis" in context
            assert "enhanced_queries" in context
            assert "context_summary" in context 