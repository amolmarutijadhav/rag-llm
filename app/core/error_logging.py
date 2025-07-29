"""
Clean error logging utilities with proper separation of concerns.
Provides enhanced error logging with full stack traces and context.
"""

import logging
import traceback
import functools
from typing import Any, Callable, Optional, Union, Awaitable
from contextlib import contextmanager

from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger("error_logging")

class ErrorLogger:
    """Centralized error logging with consistent formatting."""
    
    @staticmethod
    def log_exception(exception: Exception, context: dict) -> None:
        """
        Log exception with full traceback and context.
        
        Args:
            exception: The exception to log
            context: Additional context information
        """
        correlation_id = get_correlation_id()
        
        exc_type, exc_value, exc_traceback = type(exception), exception, exception.__traceback__
        formatted_traceback = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        logger.error(f"Exception in {context.get('operation', 'unknown')}", extra={
            'extra_fields': {
                'event_type': 'exception_logged',
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'traceback': formatted_traceback,
                'correlation_id': correlation_id,
                **context
            }
        })

def log_errors(operation_name: Optional[str] = None) -> Callable[[Callable], Callable]:
    """
    Decorator that logs errors with full stack traces.
    
    Args:
        operation_name: Custom name for the operation. If None, uses function name.
    
    Returns:
        Decorated function with error logging.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                result = func(*args, **kwargs)
                # Handle async functions
                if isinstance(result, Awaitable):
                    return _async_wrapper(result)
                return result
            except Exception as e:
                ErrorLogger.log_exception(e, {
                    'operation': operation_name or func.__name__,
                    'module': func.__module__,
                    'function': func.__name__
                })
                raise
        
        async def _async_wrapper(coro: Awaitable[Any]) -> Any:
            try:
                return await coro
            except Exception as e:
                ErrorLogger.log_exception(e, {
                    'operation': operation_name or func.__name__,
                    'module': func.__module__,
                    'function': func.__name__
                })
                raise
        
        return wrapper
    
    return decorator

@contextmanager
def error_logging_context(operation: str, **context):
    """
    Context manager for error logging.
    
    Args:
        operation: Name of the operation being performed
        **context: Additional context information
    """
    try:
        yield
    except Exception as e:
        ErrorLogger.log_exception(e, {
            'operation': operation,
            **context
        })
        raise 