"""
FastAPI middleware for logging unhandled exceptions.
"""

from fastapi import Request
from app.core.error_logging import ErrorLogger

class ErrorLoggingMiddleware:
    """Middleware that logs unhandled exceptions without interfering with FastAPI."""
    
    async def __call__(self, request: Request, call_next):
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