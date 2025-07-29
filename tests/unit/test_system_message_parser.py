"""
Unit tests for SystemMessageParser
Tests both simple keywords and JSON-like format parsing.
"""

import pytest
from app.domain.services.system_message_parser import SystemMessageParser
from app.domain.models.requests import SystemMessageDirective, ResponseMode


class TestSystemMessageParser:
    """Test cases for SystemMessageParser"""
    
    def test_parse_simple_keywords_format(self):
        """Test parsing simple keywords format"""
        system_message = """
        You are a technical support agent.
        RESPONSE_MODE: HYBRID
        DOCUMENT_CONTEXT: technical, api_docs
        CONTENT_DOMAINS: api_documentation, user_support
        DOCUMENT_CATEGORIES: user_guide, troubleshooting
        MIN_CONFIDENCE: 0.8
        FALLBACK_STRATEGY: llm_knowledge
        """
        
        directive = SystemMessageParser.parse_system_message(system_message)
        
        assert directive.response_mode == ResponseMode.HYBRID
        assert directive.document_context == ["technical", "api_docs"]
        assert directive.content_domains == ["api_documentation", "user_support"]
        assert directive.document_categories == ["user_guide", "troubleshooting"]
        assert directive.min_confidence == 0.8
        assert directive.fallback_strategy == "llm_knowledge"
    
    def test_parse_json_like_format(self):
        """Test parsing JSON-like structure format"""
        system_message = """
        You are a creative writing assistant.
        
        <config>
        RESPONSE_MODE: LLM_ONLY
        DOCUMENT_CONTEXT: creative, general
        CONTENT_DOMAINS: marketing, creative_writing
        DOCUMENT_CATEGORIES: tutorial, examples
        MIN_CONFIDENCE: 0.6
        FALLBACK_STRATEGY: refuse
        </config>
        """
        
        directive = SystemMessageParser.parse_system_message(system_message)
        
        assert directive.response_mode == ResponseMode.LLM_ONLY
        assert directive.document_context == ["creative", "general"]
        assert directive.content_domains == ["marketing", "creative_writing"]
        assert directive.document_categories == ["tutorial", "examples"]
        assert directive.min_confidence == 0.6
        assert directive.fallback_strategy == "refuse"
    
    def test_format_detection_simple_keywords(self):
        """Test automatic detection of simple keywords format"""
        system_message = "RESPONSE_MODE: RAG_ONLY DOCUMENT_CONTEXT: technical"
        format_type = SystemMessageParser._detect_format(system_message)
        assert format_type == "simple_keywords"
    
    def test_format_detection_json_like(self):
        """Test automatic detection of JSON-like format"""
        system_message = "<config>RESPONSE_MODE: HYBRID</config>"
        format_type = SystemMessageParser._detect_format(system_message)
        assert format_type == "json_like"
    
    def test_format_detection_default_fallback(self):
        """Test default fallback to simple keywords when no directives found"""
        system_message = "You are a helpful assistant."
        format_type = SystemMessageParser._detect_format(system_message)
        assert format_type == "simple_keywords"
    
    def test_invalid_response_mode_handling(self):
        """Test handling of invalid response mode"""
        system_message = "RESPONSE_MODE: INVALID_MODE"
        directive = SystemMessageParser.parse_system_message(system_message)
        
        # Should use default (HYBRID)
        assert directive.response_mode == ResponseMode.HYBRID
    
    def test_invalid_confidence_handling(self):
        """Test handling of invalid confidence value"""
        system_message = "MIN_CONFIDENCE: invalid_value"
        directive = SystemMessageParser.parse_system_message(system_message)
        
        # Should use default (0.5)
        assert directive.min_confidence == 0.5
    
    def test_empty_system_message(self):
        """Test parsing empty system message"""
        directive = SystemMessageParser.parse_system_message("")
        
        # Should return default directive
        assert directive.response_mode == ResponseMode.HYBRID
        assert directive.min_confidence == 0.5
        assert directive.fallback_strategy == "llm_knowledge"
    
    def test_partial_directives(self):
        """Test parsing with only some directives specified"""
        system_message = "RESPONSE_MODE: RAG_ONLY"
        directive = SystemMessageParser.parse_system_message(system_message)
        
        assert directive.response_mode == ResponseMode.RAG_ONLY
        assert directive.document_context is None
        assert directive.content_domains is None
        assert directive.document_categories is None
        assert directive.min_confidence == 0.5  # Default
        assert directive.fallback_strategy == "llm_knowledge"  # Default
    
    def test_case_insensitive_parsing(self):
        """Test case insensitive parsing"""
        system_message = """
        response_mode: smart_fallback
        document_context: TECHNICAL, API_DOCS
        content_domains: API_DOCUMENTATION
        """
        directive = SystemMessageParser.parse_system_message(system_message)
        
        assert directive.response_mode == ResponseMode.SMART_FALLBACK
        assert directive.document_context == ["technical", "api_docs"]
        assert directive.content_domains == ["api_documentation"]
    
    def test_whitespace_handling(self):
        """Test proper handling of whitespace in values"""
        system_message = """
        RESPONSE_MODE:  HYBRID  
        DOCUMENT_CONTEXT:  technical , api_docs  
        CONTENT_DOMAINS: api_documentation , user_support
        """
        directive = SystemMessageParser.parse_system_message(system_message)
        
        assert directive.response_mode == ResponseMode.HYBRID
        assert directive.document_context == ["technical", "api_docs"]
        assert directive.content_domains == ["api_documentation", "user_support"]
    
    def test_missing_config_section(self):
        """Test handling of JSON-like format with missing config section"""
        system_message = "You are an assistant. <config>RESPONSE_MODE: HYBRID"
        directive = SystemMessageParser.parse_system_message(system_message)
        
        # Should fall back to default directive
        assert directive.response_mode == ResponseMode.HYBRID
    
    def test_get_default_directive(self):
        """Test getting default directive"""
        directive = SystemMessageParser.get_default_directive()
        
        assert directive.response_mode == ResponseMode.HYBRID
        assert directive.min_confidence == 0.5
        assert directive.fallback_strategy == "llm_knowledge"
        assert directive.document_context is None
        assert directive.content_domains is None
        assert directive.document_categories is None
    
    def test_validate_directive_valid(self):
        """Test validation of valid directive"""
        directive = SystemMessageDirective(
            response_mode=ResponseMode.HYBRID,
            min_confidence=0.7,
            fallback_strategy="llm_knowledge"
        )
        
        assert SystemMessageParser.validate_directive(directive) is True
    
    def test_validate_directive_invalid_confidence(self):
        """Test validation of directive with invalid confidence"""
        import pytest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            SystemMessageDirective(
                response_mode=ResponseMode.HYBRID,
                min_confidence=1.5,  # Invalid: > 1.0
                fallback_strategy="llm_knowledge"
            )
    
    def test_validate_directive_invalid_fallback(self):
        """Test validation of directive with invalid fallback strategy"""
        directive = SystemMessageDirective(
            response_mode=ResponseMode.HYBRID,
            min_confidence=0.7,
            fallback_strategy="invalid_strategy"
        )
        
        assert SystemMessageParser.validate_directive(directive) is False
    
    def test_complex_json_like_format(self):
        """Test parsing complex JSON-like format with multiple lines"""
        system_message = """
        You are a technical support agent.
        
        <config>
        RESPONSE_MODE: SMART_FALLBACK
        DOCUMENT_CONTEXT: technical, api_docs, reference
        CONTENT_DOMAINS: api_documentation, user_support, troubleshooting
        DOCUMENT_CATEGORIES: user_guide, api_reference, getting_started
        MIN_CONFIDENCE: 0.75
        FALLBACK_STRATEGY: hybrid
        </config>
        
        Additional instructions here...
        """
        
        directive = SystemMessageParser.parse_system_message(system_message)
        
        assert directive.response_mode == ResponseMode.SMART_FALLBACK
        assert directive.document_context == ["technical", "api_docs", "reference"]
        assert directive.content_domains == ["api_documentation", "user_support", "troubleshooting"]
        assert directive.document_categories == ["user_guide", "api_reference", "getting_started"]
        assert directive.min_confidence == 0.75
        assert directive.fallback_strategy == "hybrid" 