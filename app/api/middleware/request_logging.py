"""
Enhanced HTTP Request/Response Logging Middleware

This middleware provides comprehensive logging of HTTP requests and responses,
including request/response bodies (sanitized), performance metrics, and structured events.
"""

import time
import json
from typing import Dict, Any, Optional
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from app.core.logging_config import get_logger, get_correlation_id, sanitize_for_logging

logger = get_logger(__name__)

class EnhancedRequestLoggingMiddleware:
    """Enhanced middleware for detailed HTTP request/response logging"""
    
    def __init__(self, 
                 log_request_body: bool = True,
                 log_response_body: bool = True,
                 max_body_size: int = 1024 * 10,  # 10KB
                 sensitive_headers: Optional[list] = None,
                 sensitive_body_fields: Optional[list] = None):
        """
        Initialize the enhanced request logging middleware.
        
        Args:
            log_request_body: Whether to log request bodies
            log_response_body: Whether to log response bodies
            max_body_size: Maximum body size to log (in bytes)
            sensitive_headers: List of sensitive header names to redact
            sensitive_body_fields: List of sensitive body field names to redact
        """
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_size = max_body_size
        self.sensitive_headers = sensitive_headers or [
            'authorization', 'cookie', 'x-api-key', 'x-auth-token'
        ]
        self.sensitive_body_fields = sensitive_body_fields or [
            'password', 'token', 'api_key', 'secret', 'key'
        ]
        
        logger.info("Enhanced request logging middleware initialized", extra={
            'extra_fields': {
                'event_type': 'middleware_enhanced_logging_initialized',
                'log_request_body': self.log_request_body,
                'log_response_body': self.log_response_body,
                'max_body_size': self.max_body_size,
                'sensitive_headers_count': len(self.sensitive_headers),
                'sensitive_body_fields_count': len(self.sensitive_body_fields)
            }
        })
    
    async def __call__(self, request: Request, call_next):
        """Process the request and log detailed information"""
        correlation_id = get_correlation_id()
        start_time = time.time()
        
        # Log request details
        await self._log_request(request, correlation_id, start_time)
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log response details
        await self._log_response(request, response, correlation_id, start_time, processing_time)
        
        return response
    
    async def _log_request(self, request: Request, correlation_id: str, start_time: float):
        """Log detailed request information"""
        try:
            # Get request headers (sanitized)
            headers = dict(request.headers)
            sanitized_headers = self._sanitize_headers(headers)
            
            # Get request body if enabled and not too large
            # NOTE: Don't read body for POST requests to avoid consuming the stream
            # that FastAPI needs for parameter parsing
            request_body = None
            if self.log_request_body and request.method in ['PUT', 'PATCH']:
                request_body = await self._get_request_body(request)
            
            # Log request event
            logger.info("HTTP Request received", extra={
                'extra_fields': {
                    'event_type': 'http_request_received',
                    'method': request.method,
                    'url': str(request.url),
                    'path': request.url.path,
                    'query_params': dict(request.query_params),
                    'client_ip': request.client.host if request.client else "unknown",
                    'user_agent': request.headers.get('user-agent', 'unknown'),
                    'content_type': request.headers.get('content-type', 'unknown'),
                    'content_length': request.headers.get('content-length', '0'),
                    'headers_count': len(headers),
                    'sanitized_headers': sanitized_headers,
                    'request_body_size': len(request_body) if request_body else 0,
                    'request_body_preview': request_body[:200] + "..." if request_body and len(request_body) > 200 else request_body,
                    'correlation_id': correlation_id,
                    'timestamp': start_time
                }
            })
            
        except Exception as e:
            logger.error("Error logging request details", extra={
                'extra_fields': {
                    'event_type': 'http_request_logging_error',
                    'method': request.method,
                    'url': str(request.url),
                    'error': str(e),
                    'correlation_id': correlation_id
                }
            })
    
    async def _log_response(self, request: Request, response: Response, 
                          correlation_id: str, start_time: float, processing_time: float):
        """Log detailed response information"""
        try:
            # Get response headers
            headers = dict(response.headers)
            sanitized_headers = self._sanitize_headers(headers)
            
            # Get response body if enabled and not too large
            response_body = None
            if self.log_response_body and not isinstance(response, StreamingResponse):
                response_body = await self._get_response_body(response)
            
            # Log response event
            logger.info("HTTP Response sent", extra={
                'extra_fields': {
                    'event_type': 'http_response_sent',
                    'method': request.method,
                    'url': str(request.url),
                    'path': request.url.path,
                    'status_code': response.status_code,
                    'status_message': response.status_text if hasattr(response, 'status_text') else 'Unknown',
                    'processing_time_ms': round(processing_time * 1000, 2),
                    'content_type': response.headers.get('content-type', 'unknown'),
                    'content_length': response.headers.get('content-length', '0'),
                    'headers_count': len(headers),
                    'sanitized_headers': sanitized_headers,
                    'response_body_size': len(response_body) if response_body else 0,
                    'response_body_preview': response_body[:200] + "..." if response_body and len(response_body) > 200 else response_body,
                    'correlation_id': correlation_id,
                    'timestamp': time.time()
                }
            })
            
            # Log performance metrics for slow requests
            if processing_time > 1.0:  # Log slow requests (>1 second)
                logger.warning("Slow request detected", extra={
                    'extra_fields': {
                        'event_type': 'http_slow_request',
                        'method': request.method,
                        'url': str(request.url),
                        'path': request.url.path,
                        'processing_time_ms': round(processing_time * 1000, 2),
                        'status_code': response.status_code,
                        'correlation_id': correlation_id
                    }
                })
            
        except Exception as e:
            logger.error("Error logging response details", extra={
                'extra_fields': {
                    'event_type': 'http_response_logging_error',
                    'method': request.method,
                    'url': str(request.url),
                    'status_code': response.status_code,
                    'error': str(e),
                    'correlation_id': correlation_id
                }
            })
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize sensitive headers"""
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
        return sanitized
    
    async def _get_request_body(self, request: Request) -> Optional[str]:
        """Get request body with size limits and sanitization"""
        try:
            # Check content length
            content_length = request.headers.get('content-length')
            if content_length and int(content_length) > self.max_body_size:
                return f"[BODY_TOO_LARGE: {content_length} bytes]"
            
            # Get body
            body = await request.body()
            if not body:
                return None
            
            # Convert to string
            try:
                body_str = body.decode('utf-8')
            except UnicodeDecodeError:
                return "[BINARY_BODY]"
            
            # Check size after decoding
            if len(body_str) > self.max_body_size:
                return f"[BODY_TOO_LARGE: {len(body_str)} characters]"
            
            # Try to parse as JSON for sanitization
            try:
                body_json = json.loads(body_str)
                sanitized_body = sanitize_for_logging(body_json)
                return json.dumps(sanitized_body, indent=2)
            except json.JSONDecodeError:
                # Not JSON, return as-is
                return body_str
                
        except Exception as e:
            logger.warning("Error reading request body", extra={
                'extra_fields': {
                    'event_type': 'http_request_body_read_error',
                    'error': str(e)
                }
            })
            return f"[ERROR_READING_BODY: {str(e)}]"
    
    async def _get_response_body(self, response: Response) -> Optional[str]:
        """Get response body with size limits"""
        try:
            # Check if response has a body
            if not hasattr(response, 'body') or not response.body:
                return None
            
            # Get body
            body = response.body
            if isinstance(body, bytes):
                try:
                    body_str = body.decode('utf-8')
                except UnicodeDecodeError:
                    return "[BINARY_BODY]"
            else:
                body_str = str(body)
            
            # Check size
            if len(body_str) > self.max_body_size:
                return f"[BODY_TOO_LARGE: {len(body_str)} characters]"
            
            # Try to parse as JSON for sanitization
            try:
                body_json = json.loads(body_str)
                sanitized_body = sanitize_for_logging(body_json)
                return json.dumps(sanitized_body, indent=2)
            except json.JSONDecodeError:
                # Not JSON, return as-is
                return body_str
                
        except Exception as e:
            logger.warning("Error reading response body", extra={
                'extra_fields': {
                    'event_type': 'http_response_body_read_error',
                    'error': str(e)
                }
            })
            return f"[ERROR_READING_BODY: {str(e)}]"

# Global instance for easy access
enhanced_request_logging = EnhancedRequestLoggingMiddleware() 