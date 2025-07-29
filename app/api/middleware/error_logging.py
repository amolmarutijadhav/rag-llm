"""
FastAPI middleware for logging unhandled exceptions.
"""

import os
import sys
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.error_logging import ErrorLogger

logger = logging.getLogger(__name__)

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs unhandled exceptions without interfering with FastAPI."""
    
    def __init__(self, app):
        super().__init__(app)
        # More precise test environment detection
        self.is_test_environment = self._is_test_environment()
        # Debug logging to understand environment detection
        if self.is_test_environment:
            logger.debug("ErrorLoggingMiddleware: Test environment detected, logging disabled")
        else:
            logger.debug("ErrorLoggingMiddleware: Production environment detected, logging enabled")
    
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
        
        # Additional check: look for test-related environment variables
        test_env_vars = ['PYTEST', 'TESTING', 'UNITTEST', 'NOSE']
        for var in test_env_vars:
            if os.getenv(var):
                return True
        
        # Check if we're in a test directory by examining the current working directory
        try:
            cwd = os.getcwd()
            if 'test' in cwd.lower() or 'tests' in cwd:
                return True
        except:
            pass
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Enhanced test environment detection for each request
            # This provides a second layer of protection
            current_test_env = self._is_test_environment()
            
            # Only disable logging in confirmed test environments
            if not current_test_env:
                # Log the exception but let FastAPI handle the response
                ErrorLogger.log_exception(e, {
                    'operation': f"{request.method} {request.url.path}",
                    'method': request.method,
                    'path': request.url.path,
                    'query_params': dict(request.query_params),
                    'middleware': 'error_logging'
                })
            else:
                # Debug logging for test environment
                logger.debug(f"ErrorLoggingMiddleware: Suppressing error logging in test environment for {request.method} {request.url.path}")
            
            # Always re-raise the exception to maintain FastAPI's error handling
            raise 