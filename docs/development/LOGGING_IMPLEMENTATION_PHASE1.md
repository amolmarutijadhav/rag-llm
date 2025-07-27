# Phase 1 Logging Implementation - Core Infrastructure

## Overview

Phase 1 of the logging enhancement implements a comprehensive, production-ready logging infrastructure with structured logging, correlation IDs, and external API debugging capabilities. This implementation follows SRE best practices and provides excellent observability for debugging and monitoring.

## Features Implemented

### 1. Structured JSON Logging
- **JSON-formatted logs** for easy parsing by log aggregation systems
- **Correlation IDs** for request tracing across the entire application
- **Structured data** with consistent field names and types
- **Environment-specific formatting** (JSON for production, human-readable for development)

### 2. External API Observability
- **Comprehensive external API call logging** with request/response details
- **Automatic curl command generation** for debugging external API issues
- **Retry tracking** with exponential backoff
- **Request/response size tracking** for performance monitoring
- **Error categorization** (HTTP errors, network errors, unexpected errors)

### 3. Security & Data Protection
- **Automatic sensitive data redaction** (API keys, passwords, tokens)
- **Configurable redaction rules** for headers and request bodies
- **Secure logging** that doesn't expose sensitive information

### 4. Environment Configuration
- **Environment-specific settings** (development, staging, production)
- **Configurable log levels** per environment
- **File rotation** with size limits and backup counts
- **Console and file logging** options

### 5. Request Tracing
- **Correlation ID middleware** for all HTTP requests
- **Request duration tracking** for performance monitoring
- **Client information logging** (IP, user agent)
- **Response status tracking**

## Files Created/Modified

### New Files
- `app/core/logging_config.py` - Core logging configuration and utilities
- `app/infrastructure/providers/enhanced_base_provider.py` - Enhanced base provider with logging
- `tests/unit/test_logging_config.py` - Unit tests for logging functionality
- `scripts/test_logging.py` - Test script to verify logging features

### Modified Files
- `app/main.py` - Added correlation ID middleware and logging setup
- `app/infrastructure/providers/openai_provider.py` - Updated to use enhanced logging

## Configuration

### Environment Variables

```bash
# Logging Configuration
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
ENVIRONMENT=development           # development, staging, production
ENABLE_STRUCTURED_LOGGING=true   # Enable JSON structured logging
ENABLE_EXTERNAL_API_LOGGING=true # Enable external API call logging
ENABLE_CURL_DEBUGGING=true       # Enable curl command generation
LOG_FILE_PATH=logs/app.log       # Path to log file (optional)
MAX_LOG_FILE_SIZE_MB=100         # Maximum log file size in MB
LOG_FILE_BACKUP_COUNT=5          # Number of backup log files
```

### Environment-Specific Settings

#### Development
```bash
ENVIRONMENT=development
LOG_LEVEL=DEBUG
ENABLE_STRUCTURED_LOGGING=false  # Human-readable logs
ENABLE_CURL_DEBUGGING=true
```

#### Production
```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
ENABLE_STRUCTURED_LOGGING=true   # JSON logs for aggregation
ENABLE_CURL_DEBUGGING=false      # Security
LOG_FILE_PATH=/var/log/rag-llm/app.log
```

## Usage Examples

### Basic Logging

```python
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# Basic logging
logger.info("Application started")
logger.warning("Resource usage high")
logger.error("Database connection failed")

# Structured logging with extra fields
logger.info("User action", extra={
    'extra_fields': {
        'event_type': 'user_login',
        'user_id': '12345',
        'ip_address': '192.168.1.1'
    }
})
```

### Correlation ID Management

```python
from app.core.logging_config import set_correlation_id, get_correlation_id, generate_correlation_id

# Generate and set correlation ID
correlation_id = generate_correlation_id()
set_correlation_id(correlation_id)

# All subsequent logs will include this correlation ID
logger.info("Processing request")
logger.info("External API call")
logger.info("Request completed")

# Get current correlation ID
current_id = get_correlation_id()
```

### Data Sanitization

```python
from app.core.logging_config import sanitize_for_logging

sensitive_data = {
    "api_key": "sk-secret-key",
    "password": "secret-password",
    "normal_field": "public-data"
}

sanitized = sanitize_for_logging(sensitive_data)
# Result: {"api_key": "[REDACTED]", "password": "[REDACTED]", "normal_field": "public-data"}
```

### Provider Logging

The enhanced base provider automatically logs all external API calls:

```python
# This is handled automatically by the enhanced base provider
provider = OpenAIEmbeddingProvider(config)
embeddings = await provider.get_embeddings(["test text"])

# Logs will include:
# - Request details (URL, method, headers)
# - Response details (status, size, duration)
# - Retry information
# - Curl command for debugging (if enabled)
```

## Log Output Examples

### Structured JSON Log (Production)
```json
{
  "timestamp": "2025-07-27T17:17:27.285350",
  "level": "INFO",
  "logger": "app.infrastructure.providers.openai_provider",
  "message": "OpenAI Embedding Provider initialized",
  "correlation_id": "00bf4a02-931e-4163-a044-3019c20b62bd",
  "module": "openai_provider",
  "function": "__init__",
  "line": 36,
  "pid": 4580,
  "thread_id": 19296,
  "event_type": "provider_initialized",
  "provider": "openai_embeddings",
  "model": "text-embedding-ada-002",
  "api_url": "https://api.openai.com/v1/embeddings"
}
```

### External API Call Log
```json
{
  "timestamp": "2025-07-27T17:17:27.290908",
  "level": "INFO",
  "logger": "api_calls",
  "message": "External API call successful",
  "correlation_id": "00bf4a02-931e-4163-a044-3019c20b62bd",
  "event_type": "external_api_success",
  "api_call": {
    "correlation_id": "00bf4a02-931e-4163-a044-3019c20b62bd",
    "provider": "openai_embeddings",
    "endpoint": "https://api.openai.com/v1/embeddings",
    "method": "POST",
    "request_size_bytes": 89,
    "response_size_bytes": 2048,
    "status_code": 200,
    "duration_ms": 1250.5,
    "success": true,
    "error_type": null,
    "error_message": null,
    "timestamp": "2025-07-27 17:17:27",
    "curl_command": "curl -X POST 'https://api.openai.com/v1/embeddings' \\\n  -H 'Content-Type: application/json' \\\n  -H 'Authorization: [REDACTED]' \\\n  -d '{\"input\": [\"test text\"], \"model\": \"text-embedding-ada-002\"}'",
    "retry_count": 0
  }
}
```

## Testing

### Run Unit Tests
```bash
python -m pytest tests/unit/test_logging_config.py -v
```

### Run Test Script
```bash
python scripts/test_logging.py
```

### Test External API Logging
```bash
# Start the application
python scripts/run.py

# Make API calls and check logs for external API details
curl -X POST "http://localhost:8000/documents/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@test_document.pdf"
```

## Benefits

### For Developers
- **Easy debugging** with correlation IDs and structured logs
- **Automatic curl commands** for testing external APIs
- **Clear error messages** with context and stack traces
- **Development-friendly** logging with human-readable format

### For SRE/Operations
- **Production-ready** structured logging for log aggregation
- **Comprehensive observability** of external API calls
- **Performance monitoring** with request duration tracking
- **Security compliance** with automatic data redaction
- **Easy troubleshooting** with correlation ID tracing

### For Monitoring
- **Structured data** for easy parsing and alerting
- **Consistent log format** across all components
- **Rich metadata** for filtering and analysis
- **External API metrics** for SLA monitoring

## Next Steps (Phase 2)

Phase 2 will focus on:
1. **Request/Response Middleware** - Enhanced HTTP request logging
2. **Metrics Collection** - Performance and business metrics
3. **Integration Testing** - End-to-end logging verification
4. **Documentation** - User guides and troubleshooting guides

## Troubleshooting

### Common Issues

1. **Logs not appearing in JSON format**
   - Check `ENABLE_STRUCTURED_LOGGING=true`
   - Verify `ENVIRONMENT` is set correctly

2. **Sensitive data in logs**
   - Check redaction configuration
   - Verify sensitive field names are in `redact_sensitive_fields`

3. **Missing correlation IDs**
   - Ensure middleware is properly configured
   - Check that `set_correlation_id()` is called

4. **External API logs not appearing**
   - Check `ENABLE_EXTERNAL_API_LOGGING=true`
   - Verify provider is using `EnhancedBaseProvider`

### Debug Commands

```bash
# Test logging configuration
python scripts/test_logging.py

# Check log file (if configured)
tail -f logs/app.log

# Test correlation ID functionality
python -c "
from app.core.logging_config import *
logging_config.setup_logging()
logger = get_logger('test')
set_correlation_id('test-id')
logger.info('Test message')
"
``` 