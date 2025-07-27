# API Overview

The RAG LLM API provides a comprehensive set of endpoints for document processing, question answering, and knowledge management with **full OCR support** and **optimized performance**.

## 🚀 Quick Start

### Base URL
```
http://localhost:8000
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 API Endpoints

### Health & Status

| **Endpoint** | **Method** | **Description** | **Authentication** |
|--------------|------------|-----------------|-------------------|
| `/` | GET | Health check with API info | None |
| `/health` | GET | Simple health check | None |

### Document Management

| **Endpoint** | **Method** | **Description** | **Authentication** |
|--------------|------------|-----------------|-------------------|
| `/documents/upload` | POST | Upload and process documents (with OCR) | None |
| `/documents/add-text` | POST | Add raw text to knowledge base | None |
| `/documents/clear-secure` | DELETE | Clear knowledge base (secure) | API Key + Token |
| `/documents/stats` | GET | Get collection statistics | None |

### Question Answering

| **Endpoint** | **Method** | **Description** | **Authentication** |
|--------------|------------|-----------------|-------------------|
| `/questions/ask` | POST | Ask questions with RAG-enhanced answers | None |
| `/chat/completions` | POST | RAG-enhanced chat completions | None |

## 🔒 Security

### Secure Endpoints

The `/documents/clear-secure` endpoint requires:

1. **API Key**: `X-API-Key` header
2. **Confirmation Token**: In request body
3. **Rate Limiting**: Per-IP hourly limits
4. **Audit Logging**: All operations logged

### Deprecated Endpoints

- `DELETE /documents/clear` - Returns 410 Gone (use `/documents/clear-secure`)

## 📖 Request/Response Examples

### 1. Upload Document with OCR

**Request:**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document_with_images.pdf"
```

**Response:**
```json
{
  "success": true,
  "message": "Document 'document_with_images.pdf' added successfully",
  "chunks_processed": 5,
  "extracted_text": "Invoice #12345\nCustomer: John Doe\nAmount: $1,234.56\n..."
}
```

### 2. Add Text

**Request:**
```bash
curl -X POST "http://localhost:8000/documents/add-text" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Python is a programming language created by Guido van Rossum.",
       "source_name": "python_info"
     }'
```

**Response:**
```json
{
  "success": true,
  "message": "Text added successfully",
  "chunks_processed": 1
}
```

### 3. Ask Question

**Request:**
```bash
curl -X POST "http://localhost:8000/questions/ask" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "Who created Python?",
       "top_k": 3
     }'
```

**Response:**
```json
{
  "success": true,
  "answer": "Python was created by Guido van Rossum.",
  "sources": [
    {
      "content": "Python is a programming language created by Guido van Rossum.",
      "metadata": {"source": "python_info"},
      "score": 0.95
    }
  ]
}
```

### 4. RAG-Enhanced Chat Completions

**Request:**
```bash
curl -X POST "http://localhost:8000/chat/completions" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [
         {"role": "system", "content": "You are a helpful assistant."},
         {"role": "user", "content": "What is the main topic?"}
       ],
       "temperature": 0.7,
       "max_tokens": 500
     }'
```

**Response:**
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on the available information, the main topic appears to be..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 31,
    "total_tokens": 87
  }
}
```

### 5. Secure Clear Knowledge Base

**Request:**
```bash
curl -X DELETE "http://localhost:8000/documents/clear-secure" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your_secure_api_key" \
     -d '{
       "confirmation_token": "your_confirmation_token",
       "reason": "Testing purposes"
     }'
```

**Response:**
```json
{
  "success": true,
  "message": "Knowledge base cleared successfully",
  "points_deleted": 15
}
```

### 6. Get Statistics

**Request:**
```bash
curl -X GET "http://localhost:8000/stats"
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_points": 25,
    "collection_name": "rag-llm-dev",
    "vector_size": 1536,
    "distance_metric": "Cosine"
  }
}
```

## 🔧 Configuration

### Environment Variables

The API uses externalized configuration for all settings:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-3.5-turbo

# Qdrant Configuration
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=your_qdrant_url
QDRANT_COLLECTION_NAME=rag-llm-dev
VECTOR_SIZE=1536
VECTOR_DISTANCE_METRIC=Cosine

# OCR Configuration
OCR_CONFIDENCE_THRESHOLD=60

# Security Configuration
CLEAR_ENDPOINT_API_KEY=your_secure_api_key
CLEAR_ENDPOINT_CONFIRMATION_TOKEN=your_confirmation_token
CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR=10
ENABLE_CLEAR_ENDPOINT_AUDIT_LOGGING=true
```

## 📊 Performance

### Test Performance

| **Test Configuration** | **Duration** | **Tests** | **Use Case** |
|------------------------|--------------|-----------|--------------|
| **Fast Tests** | 64.21s (1:04) | 84 passed | Development cycles |
| **Full Suite** | 153.40s (2:33) | 87 passed | Complete coverage |
| **Unit Tests** | ~10-15s | All unit tests | Quick validation |

### Production Performance

- **OCR Processing**: Real-time image text extraction
- **Vector Search**: Sub-second response times
- **Document Upload**: Support for files up to 10MB
- **Concurrent Requests**: Async processing for multiple users

## 🧪 Testing

### Test Strategy

- **Real OCR Testing**: Tesseract OCR functionality tested
- **Real Business Logic**: RAG service and document processing tested
- **Mocked External APIs**: OpenAI and Qdrant calls mocked for speed
- **Comprehensive Coverage**: 87 tests covering all functionality

### Running Tests

```bash
# Fast tests (recommended for development)
pytest -m "not slow"

# Complete test coverage
pytest

# Integration tests only
pytest tests/integration/
```

## 🔍 Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid request format"
}
```

#### 401 Unauthorized
```json
{
  "detail": "Invalid API key"
}
```

#### 403 Forbidden
```json
{
  "detail": "Rate limit exceeded"
}
```

#### 404 Not Found
```json
{
  "detail": "No relevant documents found"
}
```

#### 410 Gone
```json
{
  "detail": "Endpoint deprecated. Use /documents/clear-secure"
}
```

#### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## 📈 Monitoring

### Health Checks

- **Basic Health**: `GET /health` - Returns 200 OK if service is running
- **Detailed Health**: `GET /` - Returns API version and configuration info

### Audit Logging

Security-sensitive operations are logged with:

```json
{
  "timestamp": 1753614133.0647714,
  "operation": "clear_knowledge_base_attempt",
  "client_ip": "127.0.0.1",
  "user_agent": "Mozilla/5.0...",
  "success": true,
  "details": "Reason: Test verification"
}
```

## 🔄 Rate Limiting

### Clear Endpoint Rate Limits

- **Default**: 10 requests per hour per IP
- **Configurable**: Via `CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR`
- **Response**: 429 Too Many Requests when exceeded

### Rate Limit Headers

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 5
X-RateLimit-Reset: 1753617733
```

## 📚 Additional Resources

- [Testing Guide](../development/testing.md) - Testing strategy and performance
- [Security Guide](../development/CLEAR_ENDPOINT_SECURITY.md) - Security features
- [OCR Setup Guide](../development/OCR_SETUP_GUIDE.md) - OCR configuration
- [Architecture Guide](../development/architecture.md) - System architecture
- [Models Documentation](models.md) - Request/response models
- [Examples](examples.md) - More usage examples 