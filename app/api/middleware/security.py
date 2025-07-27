import time
import logging
from typing import Dict, Optional
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis or database)
_clear_endpoint_calls = {}

class SecurityMiddleware:
    """Security middleware for protecting critical endpoints"""
    
    def __init__(self):
        self.security = HTTPBearer(auto_error=False)
    
    async def verify_api_key(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> bool:
        """Verify API key for critical endpoints"""
        if not credentials:
            raise HTTPException(
                status_code=401,
                detail="API key required for this operation"
            )
        
        if credentials.credentials != Config.CLEAR_ENDPOINT_API_KEY:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key"
            )
        
        return True
    
    def verify_confirmation_token(self, confirmation_token: str) -> bool:
        """Verify confirmation token for destructive operations"""
        if not confirmation_token:
            raise HTTPException(
                status_code=400,
                detail="Confirmation token required for this operation"
            )
        
        if confirmation_token != Config.CLEAR_ENDPOINT_CONFIRMATION_TOKEN:
            raise HTTPException(
                status_code=400,
                detail="Invalid confirmation token"
            )
        
        return True
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Check rate limiting for critical endpoints"""
        global _clear_endpoint_calls
        
        current_time = time.time()
        hour_ago = current_time - 3600  # 1 hour ago
        
        # Clean old entries
        _clear_endpoint_calls = {ip: timestamps for ip, timestamps in _clear_endpoint_calls.items() 
                               if any(timestamp > hour_ago for timestamp in timestamps)}
        
        # Get or create list of timestamps for this client
        if client_ip not in _clear_endpoint_calls:
            _clear_endpoint_calls[client_ip] = []
        
        # Filter timestamps for this client to only include recent ones
        recent_calls = [timestamp for timestamp in _clear_endpoint_calls[client_ip] 
                       if timestamp > hour_ago]
        
        if len(recent_calls) >= Config.CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {Config.CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR} calls per hour."
            )
        
        # Record this call
        _clear_endpoint_calls[client_ip].append(current_time)
        return True
    
    def log_audit_event(self, operation: str, client_ip: str, user_agent: str, success: bool, details: str = ""):
        """Log audit events for critical operations"""
        if not Config.ENABLE_CLEAR_ENDPOINT_AUDIT_LOGGING:
            return
        
        audit_message = {
            "timestamp": time.time(),
            "operation": operation,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "success": success,
            "details": details
        }
        
        logger.info(f"AUDIT: {audit_message}")
    
    def get_client_info(self, request: Request) -> Dict[str, str]:
        """Extract client information from request"""
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        return {
            "client_ip": client_ip,
            "user_agent": user_agent
        }

# Global instance
security_middleware = SecurityMiddleware() 