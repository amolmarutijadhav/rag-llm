# Clear Endpoint Security Enhancements

## Overview

The `/clear` endpoint has been enhanced with multiple security layers to prevent accidental or unauthorized clearing of the knowledge base. This document outlines the security measures implemented and how to use them.

## Security Measures Implemented

### 1. **API Key Authentication**
- **Requirement**: Valid API key in the `Authorization` header
- **Format**: `Bearer <api-key>`
- **Configuration**: Set via `CLEAR_ENDPOINT_API_KEY` environment variable
- **Default**: `admin-secret-key-change-me` (MUST be changed in production)

### 2. **Confirmation Token**
- **Requirement**: Specific confirmation token in request body
- **Purpose**: Forces intentional confirmation of destructive operation
- **Configuration**: Set via `CLEAR_ENDPOINT_CONFIRMATION_TOKEN` environment variable
- **Default**: `CONFIRM_DELETE_ALL_DATA` (MUST be changed in production)

### 3. **Rate Limiting**
- **Limit**: Maximum 5 calls per hour per IP address
- **Configuration**: Set via `CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR` environment variable
- **Purpose**: Prevents rapid successive calls and abuse

### 4. **Audit Logging**
- **Feature**: Comprehensive logging of all clear operations
- **Configuration**: Enable/disable via `ENABLE_CLEAR_ENDPOINT_AUDIT_LOGGING` environment variable
- **Logs**: Include timestamp, client IP, user agent, success status, and details

### 5. **Endpoint Deprecation**
- **Old Endpoint**: `/documents/clear` (returns 410 Gone)
- **New Endpoint**: `/documents/clear-secure` (with all security measures)

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Security Configuration for Critical Endpoints
# IMPORTANT: Change these values in production!
CLEAR_ENDPOINT_API_KEY=your-secure-api-key-here
CLEAR_ENDPOINT_CONFIRMATION_TOKEN=your-confirmation-token-here
CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR=5
ENABLE_CLEAR_ENDPOINT_AUDIT_LOGGING=True
```

### Production Security Checklist

- [ ] Change `CLEAR_ENDPOINT_API_KEY` to a strong, unique value
- [ ] Change `CLEAR_ENDPOINT_CONFIRMATION_TOKEN` to a secure token
- [ ] Consider reducing `CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR` for stricter control
- [ ] Ensure `ENABLE_CLEAR_ENDPOINT_AUDIT_LOGGING=True` for compliance
- [ ] Configure log rotation and monitoring for audit logs
- [ ] Use HTTPS in production
- [ ] Consider implementing additional authentication (OAuth, JWT, etc.)

## Usage Examples

### Basic Usage

```bash
curl -X DELETE "http://localhost:8000/documents/clear-secure" \
     -H "Authorization: Bearer your-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "confirmation_token": "CONFIRM_DELETE_ALL_DATA",
       "reason": "Data cleanup after testing"
     }'
```

### Python Example

```python
import requests

def clear_knowledge_base(api_key: str, confirmation_token: str, reason: str = None):
    """Clear the knowledge base with security measures"""
    
    url = "http://localhost:8000/documents/clear-secure"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "confirmation_token": confirmation_token
    }
    if reason:
        data["reason"] = reason
    
    response = requests.delete(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("Knowledge base cleared successfully")
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Usage
result = clear_knowledge_base(
    api_key="your-api-key",
    confirmation_token="CONFIRM_DELETE_ALL_DATA",
    reason="Monthly data cleanup"
)
```

### JavaScript/Node.js Example

```javascript
async function clearKnowledgeBase(apiKey, confirmationToken, reason = null) {
    const url = 'http://localhost:8000/documents/clear-secure';
    const headers = {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
    };
    const data = {
        confirmation_token: confirmationToken
    };
    if (reason) {
        data.reason = reason;
    }
    
    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: headers,
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Knowledge base cleared successfully');
            return result;
        } else {
            console.error(`Error: ${response.status} - ${await response.text()}`);
            return null;
        }
    } catch (error) {
        console.error('Network error:', error);
        return null;
    }
}

// Usage
clearKnowledgeBase(
    'your-api-key',
    'CONFIRM_DELETE_ALL_DATA',
    'Monthly data cleanup'
);
```

## Error Responses

### Authentication Errors

```json
{
    "detail": "Not authenticated"
}
```
**Status**: 403 - Missing or invalid API key

### Authorization Errors

```json
{
    "detail": "Invalid API key"
}
```
**Status**: 403 - Invalid API key provided

### Validation Errors

```json
{
    "detail": [
        {
            "loc": ["body", "confirmation_token"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```
**Status**: 422 - Missing required fields

### Confirmation Token Errors

```json
{
    "detail": "Invalid confirmation token"
}
```
**Status**: 400 - Invalid confirmation token

### Rate Limit Errors

```json
{
    "detail": "Rate limit exceeded. Maximum 5 calls per hour."
}
```
**Status**: 429 - Rate limit exceeded

## Audit Logging

When audit logging is enabled, all clear operations are logged with the following information:

```
AUDIT: {
    "timestamp": 1703123456.789,
    "operation": "clear_knowledge_base_attempt",
    "client_ip": "192.168.1.100",
    "user_agent": "curl/7.68.0",
    "success": true,
    "details": "Reason: Data cleanup after testing"
}
```

### Log Events

- `clear_knowledge_base_attempt` - When a clear operation is initiated
- `clear_knowledge_base_result` - When a clear operation completes
- `clear_knowledge_base_failed` - When a clear operation fails due to validation
- `clear_knowledge_base_error` - When a clear operation fails due to system error

## Security Best Practices

### 1. **Strong API Keys**
- Use cryptographically secure random strings
- Minimum 32 characters recommended
- Store securely (environment variables, secret management systems)

### 2. **Secure Confirmation Tokens**
- Use long, random strings
- Make them difficult to guess
- Consider using UUIDs or similar

### 3. **Network Security**
- Use HTTPS in production
- Implement IP whitelisting if possible
- Use VPN or private networks for admin access

### 4. **Monitoring and Alerting**
- Monitor audit logs for suspicious activity
- Set up alerts for clear operations
- Implement log aggregation and analysis

### 5. **Access Control**
- Limit access to API keys
- Use different keys for different environments
- Rotate keys regularly

## Migration Guide

### From Old Endpoint

**Before:**
```bash
curl -X DELETE "http://localhost:8000/documents/clear"
```

**After:**
```bash
curl -X DELETE "http://localhost:8000/documents/clear-secure" \
     -H "Authorization: Bearer your-api-key" \
     -H "Content-Type: application/json" \
     -d '{"confirmation_token": "CONFIRM_DELETE_ALL_DATA"}'
```

### Testing the New Endpoint

1. **Set up environment variables**
2. **Test with valid credentials**
3. **Test with invalid credentials**
4. **Test rate limiting**
5. **Verify audit logging**

## Troubleshooting

### Common Issues

1. **403 Forbidden**: Check API key configuration
2. **400 Bad Request**: Verify confirmation token
3. **429 Too Many Requests**: Wait for rate limit reset
4. **422 Unprocessable Entity**: Check request body format

### Debug Mode

Enable debug logging by setting `DEBUG=True` in your environment variables to get more detailed error messages.

## Compliance and Governance

### Audit Requirements

- All clear operations are logged with full context
- Logs include client information and timestamps
- Failed attempts are also logged for security analysis

### Data Protection

- Clear operations are irreversible
- No backup is created automatically
- Consider implementing backup procedures before clearing

### Access Control

- API keys should be managed securely
- Consider implementing role-based access control
- Regular key rotation is recommended 