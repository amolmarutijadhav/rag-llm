"""
Unit tests for Context-Aware Models
Tests DocumentContext, SystemMessageDirective, and enhanced request models.
"""

import pytest
from pydantic import ValidationError
from app.domain.models.requests import (
    DocumentContext, SystemMessageDirective, ResponseMode,
    DocumentUploadRequest, TextUploadRequest, ContextAwareQuestionRequest
)


class TestDocumentContext:
    """Test cases for DocumentContext model"""
    
    def test_valid_document_context(self):
        """Test valid document context creation"""
        context = DocumentContext(
            context_type=["technical", "api_docs"],
            content_domain=["api_documentation", "user_support"],
            document_category=["user_guide", "reference"],
            relevance_tags=["authentication", "endpoints"],
            description="API documentation for authentication"
        )
        
        assert context.context_type == ["technical", "api_docs"]
        assert context.content_domain == ["api_documentation", "user_support"]
        assert context.document_category == ["user_guide", "reference"]
        assert context.relevance_tags == ["authentication", "endpoints"]
        assert context.description == "API documentation for authentication"
    
    def test_document_context_normalization(self):
        """Test that values are normalized to lowercase"""
        context = DocumentContext(
            context_type=["TECHNICAL", "API_DOCS"],
            content_domain=["API_DOCUMENTATION"],
            document_category=["USER_GUIDE"],
            relevance_tags=["AUTHENTICATION", "ENDPOINTS"]
        )
        
        assert context.context_type == ["technical", "api_docs"]
        assert context.content_domain == ["api_documentation"]
        assert context.document_category == ["user_guide"]
        assert context.relevance_tags == ["authentication", "endpoints"]
    
    def test_document_context_whitespace_handling(self):
        """Test whitespace handling in values"""
        context = DocumentContext(
            context_type=["  technical  ", "  api_docs  "],
            content_domain=["  api_documentation  "],
            document_category=["  user_guide  "],
            relevance_tags=["  authentication  ", "  endpoints  "]
        )
        
        assert context.context_type == ["technical", "api_docs"]
        assert context.content_domain == ["api_documentation"]
        assert context.document_category == ["user_guide"]
        assert context.relevance_tags == ["authentication", "endpoints"]
    
    def test_document_context_empty_lists_validation(self):
        """Test validation of empty lists"""
        with pytest.raises(ValidationError, match="List cannot be empty"):
            DocumentContext(
                context_type=[],
                content_domain=["api_documentation"],
                document_category=["user_guide"]
            )
        
        with pytest.raises(ValidationError, match="List cannot be empty"):
            DocumentContext(
                context_type=["technical"],
                content_domain=[],
                document_category=["user_guide"]
            )
        
        with pytest.raises(ValidationError, match="List cannot be empty"):
            DocumentContext(
                context_type=["technical"],
                content_domain=["api_documentation"],
                document_category=[]
            )
    
    def test_document_context_empty_strings_validation(self):
        """Test validation of lists with only empty strings"""
        with pytest.raises(ValidationError, match="List cannot contain only empty values"):
            DocumentContext(
                context_type=["", "  ", ""],
                content_domain=["api_documentation"],
                document_category=["user_guide"]
            )
    
    def test_document_context_optional_fields(self):
        """Test that optional fields work correctly"""
        context = DocumentContext(
            context_type=["technical"],
            content_domain=["api_documentation"],
            document_category=["user_guide"]
        )
        
        assert context.relevance_tags == []
        assert context.description is None
    
    def test_document_context_relevance_tags_validation(self):
        """Test relevance tags validation"""
        context = DocumentContext(
            context_type=["technical"],
            content_domain=["api_documentation"],
            document_category=["user_guide"],
            relevance_tags=["", "  ", "valid_tag", ""]
        )
        
        # Should filter out empty strings and normalize
        assert context.relevance_tags == ["valid_tag"]


class TestSystemMessageDirective:
    """Test cases for SystemMessageDirective model"""
    
    def test_valid_system_message_directive(self):
        """Test valid system message directive creation"""
        directive = SystemMessageDirective(
            response_mode=ResponseMode.HYBRID,
            document_context=["technical", "api_docs"],
            content_domains=["api_documentation", "user_support"],
            document_categories=["user_guide", "troubleshooting"],
            min_confidence=0.8,
            fallback_strategy="llm_knowledge"
        )
        
        assert directive.response_mode == ResponseMode.HYBRID
        assert directive.document_context == ["technical", "api_docs"]
        assert directive.content_domains == ["api_documentation", "user_support"]
        assert directive.document_categories == ["user_guide", "troubleshooting"]
        assert directive.min_confidence == 0.8
        assert directive.fallback_strategy == "llm_knowledge"
    
    def test_system_message_directive_defaults(self):
        """Test default values for system message directive"""
        directive = SystemMessageDirective()
        
        assert directive.response_mode == ResponseMode.SMART_FALLBACK
        assert directive.document_context is None
        assert directive.content_domains is None
        assert directive.document_categories is None
        assert directive.min_confidence == 0.7
        assert directive.fallback_strategy == "hybrid"
    
    def test_system_message_directive_confidence_validation(self):
        """Test confidence validation"""
        # Valid confidence values
        directive1 = SystemMessageDirective(min_confidence=0.0)
        directive2 = SystemMessageDirective(min_confidence=1.0)
        directive3 = SystemMessageDirective(min_confidence=0.5)
        
        assert directive1.min_confidence == 0.0
        assert directive2.min_confidence == 1.0
        assert directive3.min_confidence == 0.5
        
        # Invalid confidence values
        with pytest.raises(ValidationError, match="min_confidence must be between 0.0 and 1.0"):
            SystemMessageDirective(min_confidence=-0.1)
        
        with pytest.raises(ValidationError, match="min_confidence must be between 0.0 and 1.0"):
            SystemMessageDirective(min_confidence=1.1)
    
    def test_system_message_directive_all_response_modes(self):
        """Test all response modes"""
        modes = [
            ResponseMode.RAG_ONLY,
            ResponseMode.LLM_ONLY,
            ResponseMode.HYBRID,
            ResponseMode.SMART_FALLBACK,
            ResponseMode.RAG_PRIORITY,
            ResponseMode.LLM_PRIORITY
        ]
        
        for mode in modes:
            directive = SystemMessageDirective(response_mode=mode)
            assert directive.response_mode == mode


class TestDocumentUploadRequest:
    """Test cases for DocumentUploadRequest model"""
    
    def test_valid_document_upload_request(self):
        """Test valid document upload request creation"""
        context = DocumentContext(
            context_type=["technical"],
            content_domain=["api_documentation"],
            document_category=["user_guide"]
        )
        
        request = DocumentUploadRequest(
            file_path="/path/to/document.pdf",
            context=context
        )
        
        assert request.file_path == "/path/to/document.pdf"
        assert request.context == context
    
    def test_document_upload_request_file_path_validation(self):
        """Test file path validation"""
        context = DocumentContext(
            context_type=["technical"],
            content_domain=["api_documentation"],
            document_category=["user_guide"]
        )
        
        # Valid file path
        request = DocumentUploadRequest(file_path="document.pdf", context=context)
        assert request.file_path == "document.pdf"
        
        # Empty file path
        with pytest.raises(ValidationError, match="File path cannot be empty"):
            DocumentUploadRequest(file_path="", context=context)
        
        # Whitespace-only file path
        with pytest.raises(ValidationError, match="File path cannot be empty"):
            DocumentUploadRequest(file_path="   ", context=context)
    
    def test_document_upload_request_file_path_normalization(self):
        """Test file path whitespace normalization"""
        context = DocumentContext(
            context_type=["technical"],
            content_domain=["api_documentation"],
            document_category=["user_guide"]
        )
        
        request = DocumentUploadRequest(file_path="  document.pdf  ", context=context)
        assert request.file_path == "document.pdf"


class TestTextUploadRequest:
    """Test cases for TextUploadRequest model"""
    
    def test_valid_text_upload_request(self):
        """Test valid text upload request creation"""
        context = DocumentContext(
            context_type=["creative"],
            content_domain=["marketing"],
            document_category=["tutorial"]
        )
        
        request = TextUploadRequest(
            text="This is sample text content for testing.",
            context=context,
            source_name="test_source"
        )
        
        assert request.text == "This is sample text content for testing."
        assert request.context == context
        assert request.source_name == "test_source"
    
    def test_text_upload_request_text_validation(self):
        """Test text validation"""
        context = DocumentContext(
            context_type=["creative"],
            content_domain=["marketing"],
            document_category=["tutorial"]
        )
        
        # Valid text
        request = TextUploadRequest(text="Valid text content", context=context)
        assert request.text == "Valid text content"
        
        # Empty text
        with pytest.raises(ValidationError, match="Text cannot be empty"):
            TextUploadRequest(text="", context=context)
        
        # Whitespace-only text
        with pytest.raises(ValidationError, match="Text cannot be empty"):
            TextUploadRequest(text="   ", context=context)
    
    def test_text_upload_request_text_normalization(self):
        """Test text whitespace normalization"""
        context = DocumentContext(
            context_type=["creative"],
            content_domain=["marketing"],
            document_category=["tutorial"]
        )
        
        request = TextUploadRequest(text="  Sample text content  ", context=context)
        assert request.text == "Sample text content"
    
    def test_text_upload_request_optional_source_name(self):
        """Test optional source name"""
        context = DocumentContext(
            context_type=["creative"],
            content_domain=["marketing"],
            document_category=["tutorial"]
        )
        
        request = TextUploadRequest(text="Sample text", context=context)
        assert request.source_name is None


class TestContextAwareQuestionRequest:
    """Test cases for ContextAwareQuestionRequest model"""
    
    def test_valid_context_aware_question_request(self):
        """Test valid context-aware question request creation"""
        context_filter = DocumentContext(
            context_type=["technical"],
            content_domain=["api_documentation"],
            document_category=["user_guide"]
        )
        
        request = ContextAwareQuestionRequest(
            question="How do I authenticate with the API?",
            top_k=5,
            context_filter=context_filter
        )
        
        assert request.question == "How do I authenticate with the API?"
        assert request.top_k == 5
        assert request.context_filter == context_filter
    
    def test_context_aware_question_request_question_validation(self):
        """Test question validation"""
        # Valid question
        request = ContextAwareQuestionRequest(question="Valid question?")
        assert request.question == "Valid question?"
        
        # Empty question
        with pytest.raises(ValidationError, match="Question cannot be empty"):
            ContextAwareQuestionRequest(question="")
        
        # Whitespace-only question
        with pytest.raises(ValidationError, match="Question cannot be empty"):
            ContextAwareQuestionRequest(question="   ")
    
    def test_context_aware_question_request_top_k_validation(self):
        """Test top_k validation"""
        # Valid top_k values
        request1 = ContextAwareQuestionRequest(question="Test?", top_k=1)
        request2 = ContextAwareQuestionRequest(question="Test?", top_k=10)
        request3 = ContextAwareQuestionRequest(question="Test?", top_k=None)
        
        assert request1.top_k == 1
        assert request2.top_k == 10
        assert request3.top_k is None
        
        # Invalid top_k values
        with pytest.raises(ValidationError, match="top_k must be greater than 0"):
            ContextAwareQuestionRequest(question="Test?", top_k=0)
        
        with pytest.raises(ValidationError, match="top_k must be greater than 0"):
            ContextAwareQuestionRequest(question="Test?", top_k=-1)
    
    def test_context_aware_question_request_optional_context_filter(self):
        """Test optional context filter"""
        request = ContextAwareQuestionRequest(question="Test question?")
        assert request.context_filter is None
        assert request.top_k is None
    
    def test_context_aware_question_request_question_normalization(self):
        """Test question whitespace normalization"""
        request = ContextAwareQuestionRequest(question="  Sample question?  ")
        assert request.question == "Sample question?" 