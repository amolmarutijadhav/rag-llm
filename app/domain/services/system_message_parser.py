"""
System Message Parser for Context-Aware RAG
Implements hybrid approach supporting both simple keywords and JSON-like structure formats.
"""

import re
from typing import Optional
from app.domain.models.requests import SystemMessageDirective, ResponseMode
from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)

class SystemMessageParser:
    """Parser for system message directives with hybrid format support"""
    
    @staticmethod
    def parse_system_message(system_message: str) -> SystemMessageDirective:
        """
        Parse system message for response mode and document context directives.
        Supports both simple keywords and JSON-like structure formats.
        """
        correlation_id = get_correlation_id()
        
        logger.debug("Parsing system message for directives", extra={
            'extra_fields': {
                'event_type': 'system_message_parsing_start',
                'system_message_length': len(system_message),
                'correlation_id': correlation_id
            }
        })
        
        # Default directive
        directive = SystemMessageDirective()
        
        # Detect format and parse accordingly
        format_type = SystemMessageParser._detect_format(system_message)
        
        if format_type == 'json_like':
            directive = SystemMessageParser._parse_json_like_format(system_message, directive)
        else:
            directive = SystemMessageParser._parse_simple_keywords(system_message, directive)
        
        logger.info("System message parsing completed", extra={
            'extra_fields': {
                'event_type': 'system_message_parsing_complete',
                'format_type': format_type,
                'response_mode': directive.response_mode,
                'document_context': directive.document_context,
                'content_domains': directive.content_domains,
                'document_categories': directive.document_categories,
                'min_confidence': directive.min_confidence,
                'fallback_strategy': directive.fallback_strategy,
                'correlation_id': correlation_id
            }
        })
        
        return directive
    
    @staticmethod
    def _detect_format(system_message: str) -> str:
        """
        Detect if system message uses JSON-like or simple keyword format
        """
        if '<config>' in system_message and '</config>' in system_message:
            return 'json_like'
        elif any(keyword in system_message.upper() for keyword in [
            'RESPONSE_MODE:', 'DOCUMENT_CONTEXT:', 'CONTENT_DOMAINS:', 
            'DOCUMENT_CATEGORIES:', 'MIN_CONFIDENCE:', 'FALLBACK_STRATEGY:'
        ]):
            return 'simple_keywords'
        else:
            return 'simple_keywords'  # Default fallback
    
    @staticmethod
    def _parse_simple_keywords(system_message: str, directive: SystemMessageDirective) -> SystemMessageDirective:
        """Parse simple keyword format"""
        
        # Extract RESPONSE_MODE
        response_mode_match = re.search(r'RESPONSE_MODE:\s*(\w+)', system_message, re.IGNORECASE)
        if response_mode_match:
            mode_value = response_mode_match.group(1).upper()
            try:
                directive.response_mode = ResponseMode(mode_value)
            except ValueError:
                logger.warning(f"Invalid response mode: {mode_value}, using default", extra={
                    'extra_fields': {
                        'event_type': 'system_message_invalid_response_mode',
                        'invalid_mode': mode_value,
                        'default_mode': directive.response_mode
                    }
                })
        
        # Extract DOCUMENT_CONTEXT
        doc_context_match = re.search(r'DOCUMENT_CONTEXT:\s*([^.\n]+)', system_message, re.IGNORECASE)
        if doc_context_match:
            context_types = [ctx.strip().lower() for ctx in doc_context_match.group(1).split(',')]
            directive.document_context = [ctx for ctx in context_types if ctx]
        
        # Extract CONTENT_DOMAINS
        domains_match = re.search(r'CONTENT_DOMAINS:\s*([^.\n]+)', system_message, re.IGNORECASE)
        if domains_match:
            domains = [domain.strip().lower() for domain in domains_match.group(1).split(',')]
            directive.content_domains = [domain for domain in domains if domain]
        
        # Extract DOCUMENT_CATEGORIES
        categories_match = re.search(r'DOCUMENT_CATEGORIES:\s*([^.\n]+)', system_message, re.IGNORECASE)
        if categories_match:
            categories = [cat.strip().lower() for cat in categories_match.group(1).split(',')]
            directive.document_categories = [cat for cat in categories if cat]
        
        # Extract MIN_CONFIDENCE
        confidence_match = re.search(r'MIN_CONFIDENCE:\s*([0-9.]+)', system_message, re.IGNORECASE)
        if confidence_match:
            try:
                directive.min_confidence = float(confidence_match.group(1))
            except ValueError:
                logger.warning(f"Invalid confidence value: {confidence_match.group(1)}, using default", extra={
                    'extra_fields': {
                        'event_type': 'system_message_invalid_confidence',
                        'invalid_confidence': confidence_match.group(1),
                        'default_confidence': directive.min_confidence
                    }
                })
        
        # Extract FALLBACK_STRATEGY
        fallback_match = re.search(r'FALLBACK_STRATEGY:\s*(\w+)', system_message, re.IGNORECASE)
        if fallback_match:
            directive.fallback_strategy = fallback_match.group(1).lower()
        
        return directive
    
    @staticmethod
    def _parse_json_like_format(system_message: str, directive: SystemMessageDirective) -> SystemMessageDirective:
        """Parse JSON-like structure format"""
        
        # Extract config section
        config_match = re.search(r'<config>(.*?)</config>', system_message, re.DOTALL | re.IGNORECASE)
        if not config_match:
            logger.warning("JSON-like format detected but no config section found", extra={
                'extra_fields': {
                    'event_type': 'system_message_missing_config_section'
                }
            })
            return directive
        
        config_content = config_match.group(1).strip()
        
        # Parse each line in config section
        for line in config_content.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'response_mode':
                    try:
                        directive.response_mode = ResponseMode(value.upper())
                    except ValueError:
                        logger.warning(f"Invalid response mode in config: {value}, using default", extra={
                            'extra_fields': {
                                'event_type': 'system_message_config_invalid_response_mode',
                                'invalid_mode': value,
                                'default_mode': directive.response_mode
                            }
                        })
                
                elif key == 'document_context':
                    context_types = [ctx.strip().lower() for ctx in value.split(',')]
                    directive.document_context = [ctx for ctx in context_types if ctx]
                
                elif key == 'content_domains':
                    domains = [domain.strip().lower() for domain in value.split(',')]
                    directive.content_domains = [domain for domain in domains if domain]
                
                elif key == 'document_categories':
                    categories = [cat.strip().lower() for cat in value.split(',')]
                    directive.document_categories = [cat for cat in categories if cat]
                
                elif key == 'min_confidence':
                    try:
                        directive.min_confidence = float(value)
                    except ValueError:
                        logger.warning(f"Invalid confidence value in config: {value}, using default", extra={
                            'extra_fields': {
                                'event_type': 'system_message_config_invalid_confidence',
                                'invalid_confidence': value,
                                'default_confidence': directive.min_confidence
                            }
                        })
                
                elif key == 'fallback_strategy':
                    directive.fallback_strategy = value.lower()
        
        return directive
    
    @staticmethod
    def get_default_directive() -> SystemMessageDirective:
        """Get default system message directive"""
        return SystemMessageDirective()
    
    @staticmethod
    def validate_directive(directive: SystemMessageDirective) -> bool:
        """Validate parsed directive"""
        try:
            # Validate response mode
            if directive.response_mode not in ResponseMode:
                return False
            
            # Validate confidence range
            if directive.min_confidence is not None and (directive.min_confidence < 0.0 or directive.min_confidence > 1.0):
                return False
            
            # Validate fallback strategy
            valid_fallbacks = ['llm_knowledge', 'refuse', 'hybrid']
            if directive.fallback_strategy not in valid_fallbacks:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating directive: {e}", extra={
                'extra_fields': {
                    'event_type': 'system_message_directive_validation_error',
                    'error': str(e)
                }
            })
            return False 