import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from app.api.middleware.security import SecurityMiddleware
from app.core.config import Config

@pytest.mark.unit
class TestSecurityMiddleware:
    """Test security middleware functionality"""
    
    @pytest.fixture
    def security_middleware(self):
        return SecurityMiddleware()
    
    def test_verify_confirmation_token_valid(self, security_middleware):
        """Test valid confirmation token verification"""
        result = security_middleware.verify_confirmation_token(Config.CLEAR_ENDPOINT_CONFIRMATION_TOKEN)
        assert result == True
    
    def test_verify_confirmation_token_invalid(self, security_middleware):
        """Test invalid confirmation token verification"""
        with pytest.raises(HTTPException) as exc_info:
            security_middleware.verify_confirmation_token("invalid_token")
        
        assert exc_info.value.status_code == 400
        assert "Invalid confirmation token" in str(exc_info.value.detail)
    
    def test_verify_confirmation_token_empty(self, security_middleware):
        """Test empty confirmation token verification"""
        with pytest.raises(HTTPException) as exc_info:
            security_middleware.verify_confirmation_token("")
        
        assert exc_info.value.status_code == 400
        assert "Confirmation token required" in str(exc_info.value.detail)
    
    def test_check_rate_limit_first_call(self, security_middleware):
        """Test rate limiting on first call"""
        result = security_middleware.check_rate_limit("192.168.1.1")
        assert result == True
    
    def test_check_rate_limit_within_limit(self, security_middleware):
        """Test rate limiting within allowed limit"""
        # Make multiple calls within limit
        for i in range(Config.CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR - 1):
            result = security_middleware.check_rate_limit("192.168.1.1")
            assert result == True
    
    def test_check_rate_limit_exceeded(self, security_middleware):
        """Test rate limiting when exceeded"""
        # Make calls up to the limit
        for i in range(Config.CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR):
            security_middleware.check_rate_limit("192.168.1.2")
        
        # Next call should fail
        with pytest.raises(HTTPException) as exc_info:
            security_middleware.check_rate_limit("192.168.1.2")
        
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in str(exc_info.value.detail)
    
    def test_get_client_info(self, security_middleware):
        """Test client information extraction"""
        mock_request = Mock()
        mock_request.client.host = "192.168.1.100"
        mock_request.headers.get.return_value = "test-user-agent"
        
        client_info = security_middleware.get_client_info(mock_request)
        
        assert client_info["client_ip"] == "192.168.1.100"
        assert client_info["user_agent"] == "test-user-agent"
    
    def test_get_client_info_no_client(self, security_middleware):
        """Test client information extraction when no client info"""
        mock_request = Mock()
        mock_request.client = None
        mock_request.headers.get.return_value = "test-user-agent"
        
        client_info = security_middleware.get_client_info(mock_request)
        
        assert client_info["client_ip"] == "unknown"
        assert client_info["user_agent"] == "test-user-agent"
    
    @patch('app.api.middleware.security.logger')
    def test_log_audit_event_enabled(self, mock_logger, security_middleware):
        """Test audit event logging when enabled"""
        with patch.object(Config, 'ENABLE_CLEAR_ENDPOINT_AUDIT_LOGGING', True):
            security_middleware.log_audit_event(
                operation="test_operation",
                client_ip="192.168.1.1",
                user_agent="test-agent",
                success=True,
                details="test details"
            )
            
            mock_logger.info.assert_called_once()
            log_message = mock_logger.info.call_args[0][0]
            assert "AUDIT:" in log_message
            assert "test_operation" in log_message
    
    @patch('app.api.middleware.security.logger')
    def test_log_audit_event_disabled(self, mock_logger, security_middleware):
        """Test audit event logging when disabled"""
        with patch.object(Config, 'ENABLE_CLEAR_ENDPOINT_AUDIT_LOGGING', False):
            security_middleware.log_audit_event(
                operation="test_operation",
                client_ip="192.168.1.1",
                user_agent="test-agent",
                success=True,
                details="test details"
            )
            
            mock_logger.info.assert_not_called() 