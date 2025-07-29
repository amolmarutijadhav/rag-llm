"""
FastAPI middleware for logging unhandled exceptions.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.error_logging import ErrorLogger

class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs unhandled exceptions without interfering with FastAPI."""
    
    def __init__(self, app):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the exception but let FastAPI handle the response
            ErrorLogger.log_exception(e, {
                'operation': f"{request.method} {request.url.path}",
                'method': request.method,
                'path': request.url.path,
                'query_params': dict(request.query_params),
                'middleware': 'error_logging'
            })
            raise 