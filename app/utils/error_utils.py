"""
Error handling utilities for consistent error logging across the application.
"""

import logging
from typing import Any, Dict, Optional, Callable, TypeVar
from functools import wraps

from app.core.error_logging import ErrorLogger, log_errors
from app.core.logging_config import get_logger, get_correlation_id

T = TypeVar('T')

def handle_api_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator for API endpoints to provide consistent error handling and logging.
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> T:
        correlation_id = get_correlation_id()
        logger = get_logger(f"{func.__module__}.{func.__name__}")
        
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Log detailed error information
            ErrorLogger.log_exception(e, {
                'correlation_id': correlation_id,
                'endpoint': func.__name__,
                'module': func.__module__,
                'error_source': 'api_endpoint'
            })
            
            # Re-raise for FastAPI to handle
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> T:
        correlation_id = get_correlation_id()
        logger = get_logger(f"{func.__module__}.{func.__name__}")
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log detailed error information
            ErrorLogger.log_exception(e, {
                'correlation_id': correlation_id,
                'endpoint': func.__name__,
                'module': func.__module__,
                'error_source': 'api_endpoint'
            })
            
            # Re-raise for FastAPI to handle
            raise
    
    # Return appropriate wrapper
    if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
        return async_wrapper
    return sync_wrapper

def handle_provider_errors(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator for provider methods to provide consistent error handling and logging.
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs) -> T:
        correlation_id = get_correlation_id()
        
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Log detailed error information
            ErrorLogger.log_exception(e, {
                'correlation_id': correlation_id,
                'provider_method': func.__name__,
                'module': func.__module__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys()) if kwargs else [],
                'error_source': 'provider'
            })
            
            # Re-raise the exception
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs) -> T:
        correlation_id = get_correlation_id()
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Log detailed error information
            ErrorLogger.log_exception(e, {
                'correlation_id': correlation_id,
                'provider_method': func.__name__,
                'module': func.__module__,
                'args_count': len(args),
                'kwargs_keys': list(kwargs.keys()) if kwargs else [],
                'error_source': 'provider'
            })
            
            # Re-raise the exception
            raise
    
    # Return appropriate wrapper
    if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
        return async_wrapper
    return sync_wrapper

def log_and_raise(exception: Exception, 
                  operation: str, 
                  context: Optional[Dict[str, Any]] = None,
                  log_level: str = "ERROR"):
    """
    Log an exception with full details and then raise it.
    
    Args:
        exception: The exception to log and raise
        operation: Description of the operation that failed
        context: Additional context data
        log_level: Log level for the error
    """
    ErrorLogger.log_exception(exception, {
        'operation': operation,
        **(context or {})
    })
    raise exception

def safe_log_error(exception: Exception, 
                   operation: str, 
                   context: Optional[Dict[str, Any]] = None,
                   log_level: str = "ERROR"):
    """
    Safely log an error without re-raising it.
    
    Args:
        exception: The exception to log
        operation: Description of the operation that failed
        context: Additional context data
        log_level: Log level for the error
    """
    try:
        ErrorLogger.log_exception(exception, {
            'operation': operation,
            **(context or {})
        })
    except Exception as log_error:
        # Fallback to basic logging if enhanced logging fails
        logger = get_logger("error_utils")
        logger.error(f"Failed to log exception: {log_error}. Original exception: {exception}") 