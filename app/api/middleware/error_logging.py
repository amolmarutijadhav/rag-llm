"""
FastAPI middleware for logging unhandled exceptions.
"""

import os
import sys
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.error_logging import ErrorLogger

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs unhandled exceptions without interfering with FastAPI."""
    
    def __init__(self, app):
        super().__init__(app)
        # More precise test environment detection
        self.is_test_environment = self._is_test_environment()
    
    def _is_test_environment(self) -> bool:
        """
        Detect if we're in a test environment using multiple reliable indicators.
        This is designed to be conservative - only disable logging when we're confident
        we're in a test environment to avoid missing errors in production.
        """
        # Primary indicator: pytest is running
        if 'pytest' in sys.modules or os.getenv('PYTEST_CURRENT_TEST'):
            return True
        
        # Secondary indicator: explicit testing flag
        if os.getenv('TESTING') == 'true':
            return True
        
        # Tertiary indicator: running in a test directory
        current_file = __file__
        if 'test' in current_file.lower() and ('tests' in current_file or 'test_' in current_file):
            return True
        
        # Check if we're running pytest directly
        if any('pytest' in arg for arg in sys.argv):
            return True
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Only disable logging in confirmed test environments
            if not self.is_test_environment:
                # Log the exception but let FastAPI handle the response
                ErrorLogger.log_exception(e, {
                    'operation': f"{request.method} {request.url.path}",
                    'method': request.method,
                    'path': request.url.path,
                    'query_params': dict(request.query_params),
                    'middleware': 'error_logging'
                })
            # Always re-raise the exception to maintain FastAPI's error handling
            raise 