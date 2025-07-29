"""
Integration tests for Context-Aware RAG system.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.domain.models.requests import DocumentContext, DocumentUploadRequest, TextUploadRequest

@pytest.fixture
def client(clean_app):
    """Create a test client for each test to avoid shared state issues."""
    return TestClient(clean_app)


class TestContextAwareDocumentUpload:
    """Test context-aware document upload endpoints"""
    
    @patch('app.domain.services.context_aware_rag_service.ContextAwareRAGService.add_document_with_context')
    def test_upload_document_with_context_success(self, mock_add_document, client):
        """Test successful document upload with context"""
        # Mock the service response
        mock_add_document.return_value = {
            "success": True,
            "message": "Document uploaded successfully with context",
            "documents_added": 1,
            "context": {
                "context_type": ["technical"],
                "content_domain": ["api_documentation"],
                "document_category": ["user_guide"]
            }
        }
        
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test API documentation file.")
            temp_file_path = f.name
        
        try:
            # Prepare form data (not JSON)
            with open(temp_file_path, 'rb') as file:
                response = client.post(
                    "/context-aware-documents/upload",
                    files={"file": ("test_doc.txt", file, "text/plain")},
                    data={
                        "context_type": "technical",
                        "content_domain": "api_documentation",
                        "document_category": "user_guide",
                        "relevance_tags": "authentication,endpoints",
                        "description": "API documentation for testing"
                    }
                )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert "documents_added" in data
            assert "context" in data
            
            # Verify the mock was called
            mock_add_document.assert_called_once()
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    @patch('app.domain.services.context_aware_rag_service.ContextAwareRAGService.add_text_with_context')
    def test_upload_text_with_context_success(self, mock_add_text, client):
        """Test successful text upload with context"""
        # Mock the service response
        mock_add_text.return_value = {
            "success": True,
            "message": "Text uploaded successfully with context",
            "documents_added": 1,
            "context": {
                "context_type": ["creative"],
                "content_domain": ["marketing"],
                "document_category": ["blog_post"]
            }
        }
        
        # Use form data (not JSON)
        response = client.post(
            "/context-aware-documents/upload-text",
            data={
                "text": "This is a marketing blog post about our new product features.",
                "context_type": "creative",
                "content_domain": "marketing",
                "document_category": "user_guide",  # Use valid category
                "relevance_tags": "product,features",
                "description": "Marketing content for new product launch",
                "source_name": "product_launch_blog"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "documents_added" in data
        assert data["context"]["content_domain"] == ["marketing"]
        
        # Verify the mock was called
        mock_add_text.assert_called_once()
    
    def test_upload_document_missing_context(self, client):
        """Test document upload without required context"""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_file_path = f.name
        
        try:
            # Missing required form fields
            with open(temp_file_path, 'rb') as file:
                response = client.post(
                    "/context-aware-documents/upload",
                    files={"file": ("test.txt", file, "text/plain")}
                    # Missing context_type, content_domain, document_category
                )
            
            assert response.status_code == 422  # Validation error
            error_detail = response.json()["detail"]
            # Check that required fields are mentioned in the error
            error_fields = [error["loc"][-1] for error in error_detail]
            assert "context_type" in error_fields or "content_domain" in error_fields or "document_category" in error_fields
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    def test_upload_document_invalid_context(self, client):
        """Test document upload with invalid context"""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_file_path = f.name
        
        try:
            # Use invalid context type
            with open(temp_file_path, 'rb') as file:
                response = client.post(
                    "/context-aware-documents/upload",
                    files={"file": ("test.txt", file, "text/plain")},
                    data={
                        "context_type": "invalid_type",  # Invalid context type
                        "content_domain": "api_documentation",
                        "document_category": "user_guide"
                    }
                )
            
            assert response.status_code == 400  # Bad request for invalid context type
            assert "Invalid context_type" in response.json()["detail"]
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    def test_context_options_endpoint(self, client):
        """Test context options endpoint"""
        response = client.get("/context-aware-documents/context-options")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check the actual response structure
        assert "context_types" in data
        assert "document_categories" in data
        assert "example_domains" in data
        
        # Verify some expected values
        context_types = data["context_types"]
        assert "technical" in context_types
        assert "creative" in context_types
        assert "api_docs" in context_types
        
        document_categories = data["document_categories"]
        assert "user_guide" in document_categories
        assert "reference" in document_categories
        assert "tutorial" in document_categories


class TestContextAwareChatCompletions:
    """Test context-aware chat completion endpoints"""
    
    @patch('app.domain.services.context_aware_rag_service.ContextAwareRAGService.ask_question_with_context')
    def test_chat_with_simple_context_directives(self, mock_ask_question, client):
        """Test chat completion with simple context directives"""
        # Mock the service response
        mock_ask_question.return_value = {
            "success": True,
            "answer": "This is a RAG-based response using technical documentation.",
            "sources": [
                {
                    "content": "API documentation content",
                    "metadata": {"source": "api_docs.txt"},
                    "score": 0.95
                }
            ],
            "response_mode": "RAG_ONLY",
            "context_used": "rag_only",
            "confidence_score": 0.95
        }
        
        request_data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. RESPONSE_MODE: RAG_ONLY"
                },
                {
                    "role": "user",
                    "content": "How do I authenticate with the API?"
                }
            ]
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "choices" in data
        assert len(data["choices"]) > 0
        assert "message" in data["choices"][0]
        assert "content" in data["choices"][0]["message"]
        
        # Verify the mock was called
        mock_ask_question.assert_called_once()
    
    @patch('app.domain.services.context_aware_rag_service.ContextAwareRAGService.ask_question_with_context')
    def test_chat_with_json_like_directives(self, mock_ask_question, client):
        """Test chat completion with JSON-like context directives"""
        # Mock the service response
        mock_ask_question.return_value = {
            "success": True,
            "answer": "This is a hybrid response combining RAG and LLM knowledge.",
            "sources": [
                {
                    "content": "Technical documentation",
                    "metadata": {"source": "tech_docs.txt"},
                    "score": 0.85
                }
            ],
            "response_mode": "HYBRID",
            "context_used": "hybrid",
            "confidence_score": 0.85
        }
        
        request_data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. <config>RESPONSE_MODE: HYBRID\nMIN_CONFIDENCE: 0.8</config>"
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
        
        assert "choices" in data
        assert len(data["choices"]) > 0
        
        # Verify the mock was called
        mock_ask_question.assert_called_once()
    
    @patch('app.domain.services.enhanced_chat_completion_service.EnhancedChatCompletionService.process_request')
    def test_chat_without_context_directives_fallback(self, mock_process_request, client):
        """Test chat completion without context directives (fallback to existing service)"""
        # Mock the existing service response
        from app.domain.models.responses import ChatCompletionResponse
        
        mock_response = ChatCompletionResponse(
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
        
        mock_process_request.return_value = mock_response
        
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
        
        assert "choices" in data
        assert len(data["choices"]) > 0
        
        # Verify the existing service was called (not context-aware)
        mock_process_request.assert_called_once()
    
    @patch('app.domain.services.context_aware_rag_service.ContextAwareRAGService.ask_question_with_context')
    def test_chat_with_smart_fallback_mode(self, mock_ask_question, client):
        """Test chat completion with SMART_FALLBACK response mode"""
        # Mock the service response
        mock_ask_question.return_value = {
            "success": True,
            "answer": "This is a smart fallback response with confidence scoring.",
            "sources": [
                {
                    "content": "Relevant documentation",
                    "metadata": {"source": "docs.txt"},
                    "score": 0.75
                }
            ],
            "response_mode": "SMART_FALLBACK",
            "context_used": "high_confidence_rag",
            "confidence_score": 0.75
        }
        
        request_data = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. RESPONSE_MODE: SMART_FALLBACK\nMIN_CONFIDENCE: 0.7"
                },
                {
                    "role": "user",
                    "content": "What are the system requirements?"
                }
            ]
        }
        
        response = client.post("/enhanced-chat/completions", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "choices" in data
        assert len(data["choices"]) > 0
        
        # Verify the mock was called
        mock_ask_question.assert_called_once()
    
    def test_chat_validation_errors(self, client):
        """Test chat completion validation errors"""
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


class TestContextAwareStatsAndManagement:
    """Test context-aware stats and management endpoints"""
    
    @patch('app.domain.services.context_aware_rag_service.ContextAwareRAGService.get_stats')
    def test_context_aware_stats_endpoint(self, mock_get_stats, client):
        """Test context-aware stats endpoint"""
        mock_get_stats.return_value = {
            "total_documents": 25,
            "context_types": {"technical": 15, "creative": 10},
            "content_domains": {"api_documentation": 20, "marketing": 5},
            "document_categories": {"user_guide": 12, "blog_post": 8, "reference": 5}
        }
        
        response = client.get("/context-aware-documents/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["total_documents"] == 25
        assert data["context_types"]["technical"] == 15
        assert data["content_domains"]["api_documentation"] == 20
        assert data["document_categories"]["user_guide"] == 12
        
        # Verify the mock was called
        mock_get_stats.assert_called_once()
    
    @patch('app.domain.services.context_aware_rag_service.ContextAwareRAGService.clear_knowledge_base')
    def test_context_aware_clear_endpoint(self, mock_clear, client):
        """Test context-aware clear endpoint"""
        mock_clear.return_value = {
            "success": True,
            "message": "Context-aware knowledge base cleared successfully"
        }
        
        response = client.delete("/context-aware-documents/clear")  # Use DELETE method
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "cleared successfully" in data["message"]
        
        # Verify the mock was called
        mock_clear.assert_called_once()
    
    def test_enhanced_chat_context_options_endpoint(self, client):
        """Test enhanced chat context options endpoint"""
        response = client.get("/enhanced-chat/context-options")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "context_options" in data
        assert "context_types" in data["context_options"]
        assert "response_modes" in data["context_options"]
        
        # Verify expected response modes
        response_modes = data["context_options"]["response_modes"]
        assert "RAG_ONLY" in response_modes
        assert "LLM_ONLY" in response_modes
        assert "HYBRID" in response_modes
        assert "SMART_FALLBACK" in response_modes
        assert "RAG_PRIORITY" in response_modes
        assert "LLM_PRIORITY" in response_modes
    
    def test_enhanced_chat_context_aware_stats_endpoint(self, client):
        """Test enhanced chat context-aware stats endpoint"""
        response = client.get("/enhanced-chat/context-aware-stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check the actual response structure (from the logs, it returns vector_store stats)
        assert "success" in data
        assert "vector_store" in data
        assert "total_documents" in data["vector_store"]
    
    def test_enhanced_chat_context_aware_clear_endpoint(self, client):
        """Test enhanced chat context-aware clear endpoint"""
        response = client.delete("/enhanced-chat/context-aware-clear")  # Use DELETE method
        
        assert response.status_code == 200
        data = response.json()
        
        assert "success" in data


class TestContextAwareEndToEndWorkflow:
    """Test end-to-end context-aware RAG workflow"""
    
    @patch('app.domain.services.context_aware_rag_service.ContextAwareRAGService.add_document_with_context')
    @patch('app.domain.services.context_aware_rag_service.ContextAwareRAGService.ask_question_with_context')
    def test_full_context_aware_workflow(self, mock_ask_question, mock_add_document, client):
        """Test complete context-aware workflow: upload document and ask question"""
        # Mock document upload
        mock_add_document.return_value = {
            "success": True,
            "message": "Document uploaded successfully",
            "document_id": "doc-123"
        }
        
        # Mock question asking
        mock_ask_question.return_value = {
            "success": True,
            "answer": "Based on the uploaded documentation, here's the answer...",
            "sources": [
                {
                    "content": "Relevant documentation content",
                    "metadata": {"source": "uploaded_doc.txt"},
                    "score": 0.92
                }
            ],
            "response_mode": "RAG_ONLY",
            "context_used": "rag_only"
        }
        
        # Step 1: Upload document with context
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is API documentation for authentication methods.")
            temp_file_path = f.name
        
        try:
            # Upload document using form data
            with open(temp_file_path, 'rb') as file:
                upload_response = client.post(
                    "/context-aware-documents/upload",
                    files={"file": ("auth_docs.txt", file, "text/plain")},
                    data={
                        "context_type": "technical",
                        "content_domain": "api_documentation",
                        "document_category": "user_guide",
                        "relevance_tags": "authentication,security",
                        "description": "API authentication documentation"
                    }
                )
            assert upload_response.status_code == 200
            
            # Step 2: Ask question with context-aware directives
            chat_request = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. RESPONSE_MODE: RAG_ONLY"
                    },
                    {
                        "role": "user",
                        "content": "How do I authenticate with the API?"
                    }
                ]
            }
            
            chat_response = client.post("/enhanced-chat/completions", json=chat_request)
            assert chat_response.status_code == 200
            
            chat_data = chat_response.json()
            assert "choices" in chat_data
            assert len(chat_data["choices"]) > 0
            
            # Verify both mocks were called
            mock_add_document.assert_called_once()
            mock_ask_question.assert_called_once()
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path) 