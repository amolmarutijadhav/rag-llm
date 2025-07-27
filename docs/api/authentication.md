# Authentication & Security

## Overview

The RAG LLM API uses API key-based authentication for external services and includes comprehensive security features for production deployment.

## API Key Authentication

### Required API Keys

#### OpenAI API Key
- **Environment Variable**: `OPENAI_API_KEY`
- **Usage**: Embedding generation and chat completions
- **Format**: `sk-...` (OpenAI API key format)
- **Permissions**: Requires access to embedding and chat completion endpoints

**Setup:**
```bash
export OPENAI_API_KEY="sk-your-openai-api-key-here"
```

#### Qdrant API Key
- **Environment Variable**: `QDRANT_API_KEY`
- **Usage**: Vector database operations
- **Format**: Varies by Qdrant Cloud configuration
- **Permissions**: Requires access to collection operations

**Setup:**
```bash
export QDRANT_API_KEY="your-qdrant-api-key-here"
```

### API Key Validation

The system validates API keys on startup and during operations:

```python
# Validation occurs in external_api_service.py
if not Config.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required")

if not Config.QDRANT_API_KEY:
    raise ValueError("QDRANT_API_KEY is required")
```

## SSL/TLS Configuration

### Certificate Management

The API supports custom SSL certificates for secure connections:

#### Environment Variables
```bash
# Certificate Configuration
CERT_FILE_PATH=/path/to/your/certificate.cer
VERIFY_SSL=True
CERT_VERIFY_MODE=auto
```

#### Certificate Verification Modes
- **`auto`**: Automatic certificate verification
- **`verify`**: Strict certificate verification
- **`none`**: No certificate verification (not recommended for production)

#### SSL Configuration Example
```python
# From cert_utils.py
ssl_config = CertificateManager.get_httpx_ssl_config(
    cert_path=Config.CERT_FILE_PATH,
    verify_ssl=Config.VERIFY_SSL
)
```

## CORS Configuration

### Cross-Origin Resource Sharing

Configurable CORS settings for web application integration:

```bash
# CORS Configuration
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*
```

#### Production CORS Settings
For production, use specific origins instead of wildcards:

```bash
CORS_ALLOW_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,Authorization
```

## Request Security

### File Upload Security

#### File Size Limits
- **Maximum File Size**: 10MB (configurable)
- **Environment Variable**: `MAX_FILE_SIZE`

#### Supported File Formats
- **PDF**: `.pdf`
- **Text**: `.txt`
- **Word**: `.docx`

#### File Validation
```python
# File size validation
if file.size and file.size > Config.MAX_FILE_SIZE:
    raise HTTPException(
        status_code=400, 
        detail=f"File too large. Maximum size is {Config.MAX_FILE_SIZE} bytes"
    )

# File format validation
file_extension = os.path.splitext(file.filename)[1].lower()
if file_extension not in Config.SUPPORTED_FORMATS:
    raise HTTPException(
        status_code=400,
        detail=f"Unsupported file format. Supported formats: {Config.SUPPORTED_FORMATS}"
    )
```

### Input Validation

#### Request Validation
All requests are validated using Pydantic models:

```python
class TextInputRequest(BaseModel):
    text: str
    source_name: Optional[str] = "text_input"

class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3
```

#### Message Validation
Multi-agentic message structure validation:

```python
def validate_multi_agent_messages(messages: List[Dict[str, str]]) -> bool:
    """Validate multi-agentic message structure"""
    if not messages:
        return False
    
    # First message must be system role
    if messages[0].get("role") != "system":
        return False
    
    # Must contain at least one user message
    user_messages = [msg for msg in messages if msg.get("role") == "user"]
    return len(user_messages) > 0
```

## Error Handling

### Authentication Errors

#### Missing API Keys
```json
{
    "detail": "OPENAI_API_KEY is required"
}
```

#### Invalid API Keys
```json
{
    "detail": "Invalid API key provided"
}
```

#### SSL Certificate Errors
```json
{
    "detail": "SSL certificate verification failed"
}
```

### Security Headers

The API includes security headers for production deployment:

```python
# Recommended security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
}
```

## Production Security Checklist

### ✅ Required Security Measures
- [ ] Use HTTPS in production
- [ ] Configure specific CORS origins
- [ ] Set up proper SSL certificates
- [ ] Use strong API keys
- [ ] Implement rate limiting
- [ ] Set up monitoring and logging
- [ ] Regular security updates

### ✅ Environment Security
- [ ] Secure environment variable storage
- [ ] Use secrets management
- [ ] Regular API key rotation
- [ ] Monitor API usage

### ✅ Network Security
- [ ] Firewall configuration
- [ ] Network segmentation
- [ ] DDoS protection
- [ ] Load balancer security

## Rate Limiting

### Request Timeouts
```bash
# HTTP Configuration
REQUEST_TIMEOUT=30
MAX_RETRIES=3
```

### Implementation
```python
# Timeout configuration in external API calls
timeout = httpx.Timeout(Config.REQUEST_TIMEOUT)
client = httpx.AsyncClient(timeout=timeout)
```

## Monitoring & Logging

### Security Events
Monitor the following security events:
- Failed authentication attempts
- Invalid file uploads
- SSL certificate errors
- API rate limit violations

### Logging Configuration
```python
import logging

# Security logging
security_logger = logging.getLogger("security")
security_logger.info("Authentication successful")
security_logger.warning("Invalid API key attempt")
```

## Best Practices

### API Key Management
1. **Never commit API keys** to version control
2. **Use environment variables** for configuration
3. **Rotate keys regularly** for security
4. **Monitor usage** for unusual activity

### File Upload Security
1. **Validate file types** before processing
2. **Limit file sizes** to prevent abuse
3. **Scan uploaded files** for malware
4. **Use temporary storage** for processing

### Network Security
1. **Use HTTPS** for all communications
2. **Configure firewalls** appropriately
3. **Monitor network traffic** for anomalies
4. **Implement rate limiting** to prevent abuse 