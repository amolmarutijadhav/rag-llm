# Enhanced Error Logging System

## Overview

The enhanced error logging system provides comprehensive exception tracking with full stack traces, context information, and structured logging for better debugging and monitoring. This system follows clean code principles and provides multiple usage patterns to fit different scenarios.

## Features

- **Full Stack Traces**: Captures complete exception information including traceback
- **Context Preservation**: Maintains correlation IDs and request context across error boundaries
- **Structured Logging**: JSON-formatted logs with consistent structure
- **Multiple Usage Patterns**: Decorators, context managers, and direct logging
- **Security**: Automatic sanitization of sensitive data
- **Performance**: Efficient logging with configurable verbosity

## Architecture

### Core Components

1. **ErrorLogger**: Centralized error logging with consistent formatting
2. **Decorators**: `@log_errors`, `@handle_api_errors`, `@handle_provider_errors`
3. **Context Manager**: `error_logging_context`
4. **FastAPI Middleware**: `ErrorLoggingMiddleware`

### File Structure

```
app/
├── core/
│   ├── error_logging.py          # Core error logging functionality
│   └── logging_config.py         # Enhanced logging configuration
├── api/
│   └── middleware/
│       └── error_logging.py      # FastAPI error logging middleware
└── utils/
    └── error_utils.py            # Error handling utilities
```

## Usage Patterns

### 1. Decorator-based Error Logging

#### Basic Decorator
```python
from app.core.error_logging import log_errors

@log_errors("data_processing")
def process_data(data: dict):
    # Your code here
    result = data.get("value", 0) / data.get("divisor", 1)
    return result
```

#### Async Function Decorator
```python
@log_errors("async_operation")
async def async_process_data(data: dict):
    await asyncio.sleep(0.1)  # Simulate async work
    result = data.get("value", 0) / data.get("divisor", 1)
    return result
```

### 2. API Endpoint Error Handling

```python
from app.utils.error_utils import handle_api_errors

@router.post("/completions")
@handle_api_errors
async def chat_completions(request: ChatCompletionRequest):
    # Your API code here
    # All exceptions will be logged with full context
    return response
```

### 3. Provider Error Handling

```python
from app.utils.error_utils import handle_provider_errors

@handle_provider_errors
async def make_api_call(self, endpoint: str, data: dict):
    # Provider code here
    # All exceptions will be logged with provider context
    return response
```

### 4. Context Manager

```python
from app.core.error_logging import error_logging_context

with error_logging_context("critical_operation", user_id=123):
    # Your code here
    risky_operation()
```

### 5. Direct Error Logging

```python
from app.core.error_logging import ErrorLogger

try:
    # Your code here
    result = risky_operation()
except Exception as e:
    ErrorLogger.log_exception(e, {
        'operation': 'risky_operation',
        'user_id': 123,
        'additional_context': 'value'
    })
    raise
```

## Configuration

### Environment Variables

```bash
# Logging level
LOG_LEVEL=ERROR

# Enable structured logging
ENABLE_STRUCTURED_LOGGING=true

# Include local variables in error logs (default: true)
ENABLE_LOCAL_VARIABLES_IN_ERRORS=true

# Maximum local variable value length
MAX_LOCAL_VARIABLE_LENGTH=200
```

### FastAPI Integration

The error logging middleware is automatically added to the FastAPI application:

```python
# In app/main.py
from app.api.middleware.error_logging import ErrorLoggingMiddleware

app.add_middleware(ErrorLoggingMiddleware)
```

## Log Output Format

The enhanced error logging produces structured JSON logs with the following format:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "level": "ERROR",
  "logger": "error_logging",
  "message": "Exception in data_processing",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
  "module": "app.api.routes.chat",
  "function": "chat_completions",
  "line": 154,
  "pid": 12345,
  "thread_id": 140234567890,
  "extra_fields": {
    "event_type": "exception_logged",
    "exception_type": "ValueError",
    "exception_message": "Data cannot be empty",
    "traceback": "Traceback (most recent call last):\n  File \"app/api/routes/chat.py\", line 154, in chat_completions\n    raise ValueError(\"Data cannot be empty\")\nValueError: Data cannot be empty",
    "correlation_id": "550e8400-e29b-41d4-a716-446655440000",
    "operation": "data_processing",
    "module": "app.api.routes.chat",
    "function": "chat_completions"
  }
}
```

## Migration Guide

### Before (Basic Error Logging)

```python
try:
    result = await some_operation()
except Exception as e:
    logger.error(f"Operation failed: {str(e)}")
    raise
```

### After (Enhanced Error Logging)

```python
from app.core.error_logging import log_errors

@log_errors("some_operation")
async def some_operation():
    # Your code here
    pass
```

Or using direct logging:

```python
from app.core.error_logging import ErrorLogger

try:
    result = await some_operation()
except Exception as e:
    ErrorLogger.log_exception(e, {
        'operation': 'some_operation',
        'additional_context': 'value'
    })
    raise
```

## Best Practices

### 1. Use Appropriate Decorators

- **`@log_errors`**: For general functions that might raise exceptions
- **`@handle_api_errors`**: For API endpoints
- **`@handle_provider_errors`**: For provider methods

### 2. Provide Meaningful Context

```python
ErrorLogger.log_exception(e, {
    'operation': 'user_authentication',
    'user_id': user_id,
    'auth_method': 'jwt',
    'ip_address': request.client.host
})
```

### 3. Use Context Managers for Critical Operations

```python
with error_logging_context("database_transaction", transaction_id=tx_id):
    # Critical database operations
    pass
```

### 4. Preserve Correlation IDs

The system automatically preserves correlation IDs across error boundaries, but you can add additional context:

```python
from app.core.logging_config import get_correlation_id

correlation_id = get_correlation_id()
ErrorLogger.log_exception(e, {
    'operation': 'operation_name',
    'correlation_id': correlation_id
})
```

### 5. Handle Sensitive Data

The system automatically sanitizes sensitive fields, but be mindful of what you include in context:

```python
# Good - no sensitive data
ErrorLogger.log_exception(e, {
    'operation': 'user_login',
    'user_id': user_id,
    'login_method': 'password'
})

# Bad - includes sensitive data
ErrorLogger.log_exception(e, {
    'operation': 'user_login',
    'password': 'secret123',  # This will be redacted
    'token': 'jwt_token'      # This will be redacted
})
```

## Testing

### Running the Test Suite

```bash
# Run the enhanced error logging tests
python scripts/test_enhanced_error_logging.py
```

### Test Coverage

The test suite covers:
- Basic error logging functionality
- Decorator-based error logging (sync and async)
- API error handling
- Provider error handling
- Context manager usage
- Correlation ID preservation

## Monitoring and Alerting

The structured error logs can be easily parsed by log aggregation systems like ELK Stack, Splunk, or CloudWatch for:

- Error rate monitoring
- Exception type analysis
- Performance impact assessment
- Root cause analysis
- Alert generation

### Example Queries

```json
// Count errors by operation
{
  "query": {
    "bool": {
      "must": [
        {"match": {"extra_fields.event_type": "exception_logged"}},
        {"range": {"timestamp": {"gte": "now-1h"}}}
      ]
    }
  },
  "aggs": {
    "operations": {
      "terms": {"field": "extra_fields.operation"}
    }
  }
}

// Find most common exception types
{
  "query": {
    "match": {"extra_fields.event_type": "exception_logged"}
  },
  "aggs": {
    "exception_types": {
      "terms": {"field": "extra_fields.exception_type"}
    }
  }
}
```

## Troubleshooting

### Common Issues

1. **Missing Correlation ID**: Ensure correlation ID is set in request middleware
2. **Large Log Files**: Configure log rotation and retention policies
3. **Performance Impact**: Use appropriate log levels and avoid logging in hot paths

### Debug Mode

Enable debug logging to see detailed error logging information:

```bash
LOG_LEVEL=DEBUG
```

## Future Enhancements

- **Error Metrics**: Integration with metrics collection systems
- **Error Grouping**: Automatic grouping of similar errors
- **Error Recovery**: Automatic retry mechanisms for transient errors
- **Error Visualization**: Dashboard for error analysis and trends 