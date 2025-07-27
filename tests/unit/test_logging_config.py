"""
Unit tests for logging configuration and correlation ID functionality.
"""

import pytest
import json
import logging
from unittest.mock import patch, MagicMock
from app.core.logging_config import (
    get_logger, set_correlation_id, get_correlation_id, 
    generate_correlation_id, sanitize_for_logging, 
    ProductionLoggingConfig, StructuredJSONFormatter
)


class TestLoggingConfig:
    """Test logging configuration functionality"""
    
    def test_get_logger(self):
        """Test logger creation"""
        logger = get_logger("test_logger")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
    
    def test_correlation_id_management(self):
        """Test correlation ID setting and getting"""
        # Test initial state
        assert get_correlation_id() == ""
        
        # Test setting correlation ID
        test_id = "test-correlation-id"
        set_correlation_id(test_id)
        assert get_correlation_id() == test_id
        
        # Test generating new correlation ID
        new_id = generate_correlation_id()
        assert isinstance(new_id, str)
        assert len(new_id) > 0
    
    def test_sanitize_for_logging(self):
        """Test data sanitization for logging"""
        # Test dictionary with sensitive data
        test_data = {
            "api_key": "secret-key",
            "password": "secret-password",
            "normal_field": "normal-value",
            "nested": {
                "token": "secret-token",
                "public_field": "public-value"
            }
        }
        
        sanitized = sanitize_for_logging(test_data)
        
        assert sanitized["api_key"] == "[REDACTED]"
        assert sanitized["password"] == "[REDACTED]"
        assert sanitized["normal_field"] == "normal-value"
        assert sanitized["nested"]["token"] == "[REDACTED]"
        assert sanitized["nested"]["public_field"] == "public-value"
    
    def test_sanitize_for_logging_list(self):
        """Test sanitization of list data"""
        test_data = [
            {"api_key": "secret1", "name": "item1"},
            {"api_key": "secret2", "name": "item2"}
        ]
        
        sanitized = sanitize_for_logging(test_data)
        
        assert sanitized[0]["api_key"] == "[REDACTED]"
        assert sanitized[0]["name"] == "item1"
        assert sanitized[1]["api_key"] == "[REDACTED]"
        assert sanitized[1]["name"] == "item2"
    
    def test_sanitize_for_logging_non_dict(self):
        """Test sanitization of non-dictionary data"""
        assert sanitize_for_logging("string") == "string"
        assert sanitize_for_logging(123) == 123
        assert sanitize_for_logging(None) is None


class TestStructuredJSONFormatter:
    """Test structured JSON formatter"""
    
    def test_format_basic_log(self):
        """Test basic log formatting"""
        formatter = StructuredJSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_logger"
        assert log_data["message"] == "Test message"
        assert "correlation_id" in log_data
        assert "timestamp" in log_data
    
    def test_format_with_extra_fields(self):
        """Test formatting with extra fields"""
        formatter = StructuredJSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.extra_fields = {
            "event_type": "test_event",
            "user_id": "12345"
        }
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data["event_type"] == "test_event"
        assert log_data["user_id"] == "12345"
    
    def test_format_with_exception(self):
        """Test formatting with exception information"""
        formatter = StructuredJSONFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Test error",
                args=(),
                exc_info=True
            )
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert "exception" in log_data
        assert log_data["exception"]["type"] == "ValueError"
        assert log_data["exception"]["message"] == "Test exception"


class TestProductionLoggingConfig:
    """Test production logging configuration"""
    
    @patch.dict('os.environ', {
        'ENVIRONMENT': 'development',
        'LOG_LEVEL': 'DEBUG',
        'ENABLE_STRUCTURED_LOGGING': 'true'
    })
    def test_config_initialization(self):
        """Test configuration initialization from environment"""
        config = ProductionLoggingConfig()
        
        assert config.environment == "development"
        assert config.log_level == "DEBUG"
        assert config.enable_structured_logging is True
    
    @patch.dict('os.environ', {
        'ENVIRONMENT': 'production',
        'LOG_LEVEL': 'WARNING',
        'ENABLE_CURL_DEBUGGING': 'false'
    })
    def test_production_config(self):
        """Test production configuration settings"""
        config = ProductionLoggingConfig()
        
        assert config.environment == "production"
        assert config.log_level == "WARNING"
        assert config.enable_curl_debugging is False
    
    def test_sensitive_data_redaction(self):
        """Test sensitive data redaction configuration"""
        config = ProductionLoggingConfig()
        
        # Test sensitive headers
        assert "authorization" in config.redact_sensitive_headers
        assert "api-key" in config.redact_sensitive_headers
        assert "cookie" in config.redact_sensitive_headers
        
        # Test sensitive fields
        assert "api_key" in config.redact_sensitive_fields
        assert "password" in config.redact_sensitive_fields
        assert "token" in config.redact_sensitive_fields


if __name__ == "__main__":
    pytest.main([__file__]) 