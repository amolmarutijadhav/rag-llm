"""
Integration tests for enhanced chat completion endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestEnhancedChatCompletionEndpoint:
    """Test enhanced chat completion endpoint"""
    
    def test_enhanced_chat_completion_basic(self):
        """Test basic enhanced chat completion"""
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the main topic?"}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "id" in data
        assert "object" in data
        assert data["object"] == "chat.completion"
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert "message" in data["choices"][0]
        assert "content" in data["choices"][0]["message"]
        assert "usage" in data
        assert "sources" in data
    
    def test_enhanced_chat_completion_with_conversation(self):
        """Test enhanced chat completion with conversation context"""
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is AI?"},
                {"role": "assistant", "content": "AI stands for Artificial Intelligence."},
                {"role": "user", "content": "Can you elaborate on machine learning?"}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that response includes conversation awareness
        assert "id" in data
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert "content" in data["choices"][0]["message"]
    
    def test_enhanced_chat_completion_no_messages(self):
        """Test enhanced chat completion with no messages"""
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "Messages cannot be empty" in data["detail"]
    
    def test_enhanced_chat_completion_no_user_message(self):
        """Test enhanced chat completion with no user message"""
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "assistant", "content": "Hello!"}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "No user message found" in data["detail"]
    
    def test_get_available_strategies(self):
        """Test getting available strategies"""
        response = client.get("/enhanced-chat/strategies")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "strategies" in data
        assert "total" in data
        assert data["total"] > 0
        
        strategies = data["strategies"]
        assert len(strategies) > 0
        
        # Check strategy structure
        for strategy in strategies:
            assert "name" in strategy
            assert "description" in strategy
            assert "features" in strategy
            assert isinstance(strategy["features"], list)
    
    def test_get_available_plugins(self):
        """Test getting available plugins"""
        response = client.get("/enhanced-chat/plugins")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "plugins" in data
        assert "total" in data
        assert data["total"] > 0
        
        plugins = data["plugins"]
        assert len(plugins) > 0
        
        # Check plugin structure
        for plugin in plugins:
            assert "name" in plugin
            assert "description" in plugin
            assert "priority" in plugin
            assert "features" in plugin
            assert isinstance(plugin["features"], list)
    
    def test_enhanced_chat_completion_with_metadata(self):
        """Test enhanced chat completion includes metadata"""
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is the main topic?"}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for enhanced metadata
        assert "metadata" in data
        metadata = data["metadata"]
        assert metadata["conversation_aware"] is True
        assert "strategy_used" in metadata
        assert "enhanced_queries_count" in metadata
        assert "conversation_context" in metadata
        assert "processing_plugins" in metadata 