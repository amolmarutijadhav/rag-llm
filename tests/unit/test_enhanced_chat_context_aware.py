"""
Unit tests for Enhanced Chat Endpoints with Context-Aware Features
Tests the enhanced /enhanced-chat/completions endpoint with context-aware functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.domain.models.requests import ChatMessage, ChatCompletionRequest

client = TestClient(app)


class TestEnhancedChatContextAware:
    """Test cases for enhanced chat endpoints with context-aware features"""
    
    @pytest.fixture
    def mock_context_aware_rag_service(self):
        """Mock context-aware RAG service"""
        with patch('app.api.routes.enhanced_chat.context_aware_rag_service') as mock:
            mock.ask_question_with_context = AsyncMock()
            yield mock
    
    @pytest.fixture
    def mock_enhanced_service(self):
        """Mock enhanced service"""
        with patch('app.api.routes.enhanced_chat.enhanced_service') as mock:
            mock.process_request = AsyncMock()
            yield mock
    
    def test_enhanced_chat_completions_with_context_directives(self, mock_context_aware_rag_service):
        """Test enhanced chat completions with context-aware directives"""
        # Mock successful context-aware RAG response
        mock_context_aware_rag_service.ask_question_with_context.return_value = {
            "success": True,
            "answer": "Based on the technical documentation, you can authenticate using API keys.",
            "sources": [{"content": "API authentication guide", "score": 0.9}],
            "response_mode": "HYBRID",
            "context_used": "rag_enhanced_with_llm"
        }
        
        request_data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a technical support agent. RESPONSE_MODE: HYBRID DOCUMENT_CONTEXT: technical"
                },
                {
                    "role": "user",
                    "content": "How do I authenticate with the API?"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert data["id"].startswith("chatcmpl-")
        assert data["object"] == "chat.completion"
        assert data["model"] == "gpt-4"
        assert len(data["choices"]) == 1
        assert data["choices"][0]["message"]["role"] == "assistant"
        assert "authenticate using API keys" in data["choices"][0]["message"]["content"]
        assert data["choices"][0]["finish_reason"] == "stop"
        
        # Verify context-aware metadata
        assert data["metadata"]["context_aware"] is True
        assert data["metadata"]["response_mode"] == "HYBRID"
        assert data["metadata"]["context_used"] == "rag_enhanced_with_llm"
        
        # Verify sources
        assert len(data["sources"]) == 1
        assert data["sources"][0]["content"] == "API authentication guide"
        
        # Verify service was called correctly
        mock_context_aware_rag_service.ask_question_with_context.assert_called_once()
        call_args = mock_context_aware_rag_service.ask_question_with_context.call_args
        assert call_args[1]["question"] == "How do I authenticate with the API?"
        assert "RESPONSE_MODE: HYBRID" in call_args[1]["system_message"]
        assert call_args[1]["top_k"] == 3
    
    def test_enhanced_chat_completions_with_json_like_directives(self, mock_context_aware_rag_service):
        """Test enhanced chat completions with JSON-like directives"""
        mock_context_aware_rag_service.ask_question_with_context.return_value = {
            "success": True,
            "answer": "Based on the creative content, here's a marketing approach.",
            "sources": [{"content": "Marketing guide", "score": 0.8}],
            "response_mode": "LLM_PRIORITY",
            "context_used": "llm_priority_with_rag_supplement"
        }
        
        request_data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": """
                    You are a creative marketing assistant.
                    
                    <config>
                    RESPONSE_MODE: LLM_PRIORITY
                    DOCUMENT_CONTEXT: creative, marketing
                    CONTENT_DOMAINS: marketing, creative_writing
                    MIN_CONFIDENCE: 0.7
                    </config>
                    """
                },
                {
                    "role": "user",
                    "content": "Write a marketing copy for our new product."
                }
            ]
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["metadata"]["context_aware"] is True
        assert data["metadata"]["response_mode"] == "LLM_PRIORITY"
        assert data["metadata"]["context_used"] == "llm_priority_with_rag_supplement"
    
    def test_enhanced_chat_completions_fallback_response(self, mock_context_aware_rag_service):
        """Test enhanced chat completions with fallback response"""
        mock_context_aware_rag_service.ask_question_with_context.return_value = {
            "success": False,
            "answer": "I'm sorry, I couldn't process your request.",
            "response_mode": "HYBRID",
            "context_used": "fallback"
        }
        
        request_data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a technical support agent. RESPONSE_MODE: HYBRID"
                },
                {
                    "role": "user",
                    "content": "What is the meaning of life?"
                }
            ]
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["metadata"]["context_aware"] is True
        assert data["metadata"]["response_mode"] == "HYBRID"
        assert "couldn't process your request" in data["choices"][0]["message"]["content"]
    
    def test_enhanced_chat_completions_no_context_directives(self, mock_enhanced_service):
        """Test enhanced chat completions without context directives (backward compatibility)"""
        mock_enhanced_service.process_request.return_value = Mock(
            id="chatcmpl-test",
            object="chat.completion",
            created=1234567890,
            model="gpt-4",
            choices=[{
                "index": 0,
                "message": {"role": "assistant", "content": "Regular response"},
                "finish_reason": "stop"
            }],
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            sources=[],
            metadata={"context_aware": False, "response_mode": "enhanced"}
        )
        
        request_data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Hello, how are you?"
                }
            ]
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should use existing enhanced service
        assert data["metadata"]["context_aware"] is False
        mock_enhanced_service.process_request.assert_called_once()
    
    def test_enhanced_chat_completions_validation_errors(self):
        """Test enhanced chat completions validation errors"""
        # Empty messages
        request_data = {
            "model": "gpt-4",
            "messages": []
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        assert response.status_code == 400
        assert "Messages cannot be empty" in response.json()["detail"]
        
        # No user message
        request_data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                }
            ]
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        assert response.status_code == 400
        assert "No user message found" in response.json()["detail"]
    
    def test_context_options_endpoint(self):
        """Test context options endpoint"""
        response = client.get("/enhanced-chat/context-options")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "context_options" in data
        assert "context_types" in data["context_options"]
        assert "content_domains" in data["context_options"]
        assert "document_categories" in data["context_options"]
        assert "response_modes" in data["context_options"]
        assert "fallback_strategies" in data["context_options"]
        
        # Verify some expected values
        context_types = data["context_options"]["context_types"]
        assert "technical" in context_types
        assert "creative" in context_types
        assert "api_docs" in context_types
        
        response_modes = data["context_options"]["response_modes"]
        assert "RAG_ONLY" in response_modes
        assert "LLM_ONLY" in response_modes
        assert "HYBRID" in response_modes
        assert "SMART_FALLBACK" in response_modes
    
    def test_context_aware_stats_endpoint(self, mock_context_aware_rag_service):
        """Test context-aware stats endpoint"""
        mock_context_aware_rag_service.get_stats.return_value = {
            "total_documents": 25,
            "context_types": {"technical": 15, "creative": 10},
            "content_domains": {"api_documentation": 20, "marketing": 5}
        }
        
        response = client.get("/enhanced-chat/context-aware-stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_documents"] == 25
        assert data["context_types"]["technical"] == 15
        assert data["content_domains"]["api_documentation"] == 20
    
    def test_context_aware_clear_endpoint(self, mock_context_aware_rag_service):
        """Test context-aware clear endpoint"""
        mock_context_aware_rag_service.clear_knowledge_base.return_value = {
            "success": True,
            "message": "Knowledge base cleared successfully"
        }
        
        response = client.delete("/enhanced-chat/context-aware-clear")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "cleared successfully" in data["message"]
        mock_context_aware_rag_service.clear_knowledge_base.assert_called_once()
    
    def test_enhanced_chat_completions_with_confidence_score(self, mock_context_aware_rag_service):
        """Test enhanced chat completions with confidence score"""
        mock_context_aware_rag_service.ask_question_with_context.return_value = {
            "success": True,
            "answer": "High confidence answer based on technical docs.",
            "sources": [{"content": "Technical guide", "score": 0.95}],
            "response_mode": "SMART_FALLBACK",
            "context_used": "high_confidence_rag",
            "confidence_score": 0.95
        }
        
        request_data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a technical expert. RESPONSE_MODE: SMART_FALLBACK MIN_CONFIDENCE: 0.8"
                },
                {
                    "role": "user",
                    "content": "What are the best practices for API design?"
                }
            ]
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["metadata"]["context_aware"] is True
        assert data["metadata"]["response_mode"] == "SMART_FALLBACK"
        assert data["metadata"]["context_used"] == "high_confidence_rag"
        assert data["metadata"]["confidence_score"] == 0.95
    
    def test_enhanced_chat_completions_error_handling(self, mock_context_aware_rag_service):
        """Test enhanced chat completions error handling"""
        mock_context_aware_rag_service.ask_question_with_context.side_effect = Exception("Service error")
        
        request_data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a technical support agent. RESPONSE_MODE: HYBRID"
                },
                {
                    "role": "user",
                    "content": "Test question"
                }
            ]
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 500
        assert "Service error" in response.json()["detail"] 