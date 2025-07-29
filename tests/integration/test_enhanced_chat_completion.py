"""
Integration tests for enhanced chat completion endpoint.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

@pytest.fixture
def client(clean_app):
    """Create a test client for each test to avoid shared state issues."""
    return TestClient(clean_app)

class TestEnhancedChatCompletionEndpoint:
    """Test enhanced chat completion endpoint"""
    
    @patch('app.domain.services.enhanced_chat_completion_service.EnhancedChatCompletionService.process_request')
    def test_enhanced_chat_completion_basic(self, mock_process_request, client):
        """Test basic enhanced chat completion"""
        # Mock the service response
        from app.domain.models.responses import ChatCompletionResponse
        
        mock_response = ChatCompletionResponse(
            id="chatcmpl-test-123",
            object="chat.completion",
            created=1234567890,
            model="gpt-3.5-turbo",
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a test response from the enhanced chat completion service."
                    },
                    "finish_reason": "stop"
                }
            ],
            usage={
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            },
            sources=[
                {
                    "content": "Test source content",
                    "metadata": {"source": "test.txt"},
                    "score": 0.95
                }
            ],
            metadata={
                "conversation_aware": True,
                "strategy_used": "topic_tracking",
                "enhanced_queries_count": 3,
                "conversation_context": {
                    "topics": ["test", "topic"],
                    "entities": ["test"],
                    "conversation_length": 2
                },
                "processing_plugins": ["conversation_context", "multi_query_rag", "response_enhancement"]
            }
        )
        
        mock_process_request.return_value = mock_response
        
        # Test request
        request_data = {
            "messages": [
                {"role": "user", "content": "What is Python?"}
            ],
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "chatcmpl-test-123"
        assert data["object"] == "chat.completion"
        assert data["model"] == "gpt-3.5-turbo"
        assert len(data["choices"]) == 1
        assert data["choices"][0]["message"]["role"] == "assistant"
        assert "test response" in data["choices"][0]["message"]["content"]
        
        # Verify metadata
        assert data["metadata"]["conversation_aware"] is True
        assert data["metadata"]["strategy_used"] == "topic_tracking"
        assert data["metadata"]["enhanced_queries_count"] == 3
        
        # Verify sources
        assert len(data["sources"]) == 1
        assert data["sources"][0]["content"] == "Test source content"
        assert data["sources"][0]["score"] == 0.95

    @patch('app.domain.services.enhanced_chat_completion_service.EnhancedChatCompletionService.process_request')
    def test_enhanced_chat_completion_with_conversation(self, mock_process_request, client):
        """Test enhanced chat completion with conversation history"""
        # Mock the service response
        from app.domain.models.responses import ChatCompletionResponse
        
        mock_response = ChatCompletionResponse(
            id="chatcmpl-test-456",
            object="chat.completion",
            created=1234567890,
            model="gpt-3.5-turbo",
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Based on our conversation about Python, it's a programming language."
                    },
                    "finish_reason": "stop"
                }
            ],
            usage={
                "prompt_tokens": 15,
                "completion_tokens": 25,
                "total_tokens": 40
            },
            sources=[],
            metadata={
                "conversation_aware": True,
                "strategy_used": "conversation_context",
                "enhanced_queries_count": 2,
                "conversation_context": {
                    "topics": ["python", "programming"],
                    "entities": ["python"],
                    "conversation_length": 3
                },
                "processing_plugins": ["conversation_context"]
            }
        )
        
        mock_process_request.return_value = mock_response
        
        # Test request with conversation history
        request_data = {
            "messages": [
                {"role": "user", "content": "What is programming?"},
                {"role": "assistant", "content": "Programming is the process of creating instructions for computers."},
                {"role": "user", "content": "Tell me more about Python"}
            ],
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "chatcmpl-test-456"
        assert "conversation" in data["choices"][0]["message"]["content"].lower()
        
        # Verify conversation context
        assert data["metadata"]["conversation_aware"] is True
        assert data["metadata"]["strategy_used"] == "conversation_context"
        assert data["metadata"]["conversation_context"]["conversation_length"] == 3

    @patch('app.domain.services.enhanced_chat_completion_service.EnhancedChatCompletionService.process_request')
    def test_enhanced_chat_completion_no_messages(self, mock_process_request, client):
        """Test enhanced chat completion with no messages"""
        # Mock the service response
        from app.domain.models.responses import ChatCompletionResponse
        
        mock_response = ChatCompletionResponse(
            id="chatcmpl-test-789",
            object="chat.completion",
            created=1234567890,
            model="gpt-3.5-turbo",
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?"
                    },
                    "finish_reason": "stop"
                }
            ],
            usage={
                "prompt_tokens": 5,
                "completion_tokens": 10,
                "total_tokens": 15
            },
            sources=[],
            metadata={
                "conversation_aware": False,
                "strategy_used": "basic",
                "enhanced_queries_count": 1,
                "conversation_context": {
                    "topics": [],
                    "entities": [],
                    "conversation_length": 0
                },
                "processing_plugins": []
            }
        )
        
        mock_process_request.return_value = mock_response
        
        # Test request with empty messages
        request_data = {
            "messages": [],
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        # API correctly validates and returns 400 for empty messages
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "messages" in data["detail"].lower()

    @patch('app.domain.services.enhanced_chat_completion_service.EnhancedChatCompletionService.process_request')
    def test_enhanced_chat_completion_no_user_message(self, mock_process_request, client):
        """Test enhanced chat completion with no user message"""
        # Mock the service response
        from app.domain.models.responses import ChatCompletionResponse
        
        mock_response = ChatCompletionResponse(
            id="chatcmpl-test-101",
            object="chat.completion",
            created=1234567890,
            model="gpt-3.5-turbo",
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "I need a user message to provide a helpful response."
                    },
                    "finish_reason": "stop"
                }
            ],
            usage={
                "prompt_tokens": 5,
                "completion_tokens": 15,
                "total_tokens": 20
            },
            sources=[],
            metadata={
                "conversation_aware": False,
                "strategy_used": "basic",
                "enhanced_queries_count": 1,
                "conversation_context": {
                    "topics": [],
                    "entities": [],
                    "conversation_length": 0
                },
                "processing_plugins": []
            }
        )
        
        mock_process_request.return_value = mock_response
        
        # Test request with only assistant messages
        request_data = {
            "messages": [
                {"role": "assistant", "content": "Hello! How can I help you?"}
            ],
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        # API correctly validates and returns 400 for no user message
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "user" in data["detail"].lower()

    def test_get_available_strategies(self, client):
        """Test getting available strategies endpoint"""
        response = client.get("/enhanced-chat/strategies")
        
        assert response.status_code == 200
        data = response.json()
        assert "strategies" in data
        assert isinstance(data["strategies"], list)
        assert len(data["strategies"]) > 0
        
        # Verify strategy structure
        for strategy in data["strategies"]:
            assert "name" in strategy
            assert "description" in strategy
            assert "features" in strategy  # API returns "features" not "enabled"

    def test_get_available_plugins(self, client):
        """Test getting available plugins endpoint"""
        response = client.get("/enhanced-chat/plugins")
        
        assert response.status_code == 200
        data = response.json()
        assert "plugins" in data
        assert isinstance(data["plugins"], list)
        assert len(data["plugins"]) > 0
        
        # Verify plugin structure
        for plugin in data["plugins"]:
            assert "name" in plugin
            assert "description" in plugin
            assert "features" in plugin  # API returns "features" not "enabled"
            assert "priority" in plugin  # API returns "priority"

    @patch('app.domain.services.enhanced_chat_completion_service.EnhancedChatCompletionService.process_request')
    def test_enhanced_chat_completion_with_metadata(self, mock_process_request, client):
        """Test enhanced chat completion with custom metadata"""
        # Mock the service response
        from app.domain.models.responses import ChatCompletionResponse
        
        mock_response = ChatCompletionResponse(
            id="chatcmpl-test-metadata",
            object="chat.completion",
            created=1234567890,
            model="gpt-3.5-turbo",
            choices=[
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This response includes custom metadata."
                    },
                    "finish_reason": "stop"
                }
            ],
            usage={
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            },
            sources=[],
            metadata={
                "conversation_aware": True,
                "strategy_used": "custom_metadata",
                "enhanced_queries_count": 1,
                "conversation_context": {
                    "topics": ["metadata", "custom"],
                    "entities": ["metadata"],
                    "conversation_length": 1
                },
                "processing_plugins": ["custom_metadata"],
                "custom_field": "custom_value",
                "test_flag": True
            }
        )
        
        mock_process_request.return_value = mock_response
        
        # Test request with custom metadata
        request_data = {
            "messages": [
                {"role": "user", "content": "Test with metadata"}
            ],
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 100,
            "metadata": {
                "custom_field": "custom_value",
                "test_flag": True
            }
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "chatcmpl-test-metadata"
        assert "metadata" in data["choices"][0]["message"]["content"].lower()
        
        # Verify custom metadata
        assert data["metadata"]["custom_field"] == "custom_value"
        assert data["metadata"]["test_flag"] is True
        assert data["metadata"]["strategy_used"] == "custom_metadata" 