# API Overview

The RAG LLM API provides a comprehensive set of endpoints for document processing, question answering, and knowledge management with **full OCR support**, **plugin architecture for external services**, and **optimized performance**.

## 🚀 Quick Start

### Base URL
```
http://localhost:8000
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 Plugin Architecture

The API now supports a plugin architecture that allows you to easily switch between different external service providers:

### Available Providers

- **Embedding Providers**: OpenAI (default), In-house templates
- **LLM Providers**: OpenAI (default), In-house templates  
- **Vector Store Providers**: Qdrant (default), In-house templates

### Provider Configuration

Configure providers via environment variables:

```bash
# Provider Types
PROVIDER_EMBEDDING_TYPE=openai      # or "inhouse"
PROVIDER_LLM_TYPE=openai           # or "inhouse"
PROVIDER_VECTOR_STORE_TYPE=qdrant  # or "inhouse"

# Provider-specific configuration
OPENAI_API_KEY=your_openai_key
QDRANT_API_KEY=your_qdrant_key
```

For detailed provider information, see [Plugin Architecture Guide](../development/PLUGIN_ARCHITECTURE.md).

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
| `/questions/stats` | GET | Get collection statistics | None |

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
      "metadata": {
        "source": "python_info",
        "chunk_index": 0
      },
      "score": 0.95
    }
  ],
  "context_used": "Python is a programming language created by Guido van Rossum."
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
         {"role": "user", "content": "What is Python?"}
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
        "content": "Python is a high-level programming language created by Guido van Rossum..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 107,
    "completion_tokens": 73,
    "total_tokens": 180
  },
  "rag_metadata": {
    "agent_persona_preserved": true,
    "context_documents_found": 1,
    "original_message_count": 2,
    "enhanced_message_count": 2
  }
}
```

### 5. Get Statistics

**Request:**
```bash
curl -X GET "http://localhost:8000/questions/stats"
```

**Response:**
```json
{
  "success": true,
  "vector_store": {
    "total_documents": 15,
    "collection_name": "rag-llm-dev",
    "vector_size": 1536
  },
  "supported_formats": [
    ".pdf",
    ".txt",
    ".docx"
  ],
  "chunk_size": 1000,
  "chunk_overlap": 200,
  "embedding_provider": {
    "model": "text-embedding-ada-002",
    "dimensions": 1536
  },
  "llm_provider": {
    "model": "gpt-3.5-turbo",
    "max_tokens": 1000
  }
}
```

### 6. Clear Knowledge Base (Secure)

**Request:**
```bash
curl -X DELETE "http://localhost:8000/documents/clear-secure" \
     -H "accept: application/json" \
     -H "X-API-Key: your_secure_api_key" \
     -H "Content-Type: application/json" \
     -d '{
       "confirmation_token": "CONFIRM_DELETE_ALL_DATA",
       "reason": "Testing cleanup"
     }'
```

**Response:**
```json
{
  "success": true,
  "message": "Knowledge base cleared successfully",
  "chunks_processed": null,
  "extracted_text": null
}
```

## 🔄 Data Flow

### Document Processing Flow

```
1. Document Upload
   ↓
2. File Validation & Processing
   ↓
3. Text Extraction (OCR if needed)
   ↓
4. Document Chunking
   ↓
5. Embedding Generation (via Provider)
   ↓
6. Vector Storage (via Provider)
   ↓
7. Success Response
```

### Question Answering Flow

```
1. Question Input
   ↓
2. Question Embedding (via Provider)
   ↓
3. Vector Search (via Provider)
   ↓
4. Context Retrieval
   ↓
5. LLM Generation (via Provider)
   ↓
6. Response Formatting
   ↓
7. Answer with Sources
```

## 🔧 Configuration

### Environment Variables

The API uses externalized configuration with plugin architecture support:

```bash
# Provider Type Configuration
PROVIDER_EMBEDDING_TYPE=openai      # or "inhouse", "cohere"
PROVIDER_LLM_TYPE=openai           # or "inhouse", "anthropic"
PROVIDER_VECTOR_STORE_TYPE=qdrant  # or "inhouse", "pinecone"

# OpenAI Provider Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-3.5-turbo

# Qdrant Provider Configuration
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=your_qdrant_url
QDRANT_COLLECTION_NAME=rag-llm-dev
VECTOR_SIZE=1536
VECTOR_DISTANCE_METRIC=Cosine

# In-House Provider Configuration (optional)
INHOUSE_EMBEDDING_API_URL=https://your-inhouse-embedding-api.com
INHOUSE_LLM_API_URL=https://your-inhouse-llm-api.com
INHOUSE_VECTOR_STORE_URL=https://your-inhouse-vector-store.com
INHOUSE_API_KEY=your_inhouse_key

# OCR Configuration
OCR_CONFIDENCE_THRESHOLD=60

# Security Configuration
CLEAR_ENDPOINT_API_KEY=your_secure_api_key
CLEAR_ENDPOINT_CONFIRMATION_TOKEN=your_confirmation_token
CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR=10
ENABLE_CLEAR_ENDPOINT_AUDIT_LOGGING=true

# FastAPI Configuration
API_TITLE=RAG LLM API
API_DESCRIPTION=A simple RAG (Retrieval-Augmented Generation) API for document Q&A
API_VERSION=1.0.0

# CORS Configuration
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# HTTP Configuration
REQUEST_TIMEOUT=30
MAX_RETRIES=3
```

## 🚀 Performance

### Response Times

| **Operation** | **Typical Response Time** | **Provider Impact** |
|---------------|---------------------------|-------------------|
| **Health Check** | < 100ms | None |
| **Document Upload** | 2-5s | Embedding + Vector Store |
| **Text Addition** | 1-3s | Embedding + Vector Store |
| **Question Answering** | 2-4s | Embedding + Vector Store + LLM |
| **Chat Completions** | 3-6s | Embedding + Vector Store + LLM |

### Provider Performance

The plugin architecture allows for provider-specific optimizations:

- **OpenAI Providers**: Optimized for OpenAI API patterns
- **In-House Providers**: Custom optimizations for internal services
- **Qdrant Provider**: Optimized for Qdrant Cloud operations

## 🔒 Security Features

### Authentication

- **API Key Authentication**: Required for secure endpoints
- **Provider-Specific Auth**: Each provider can have different auth methods
- **Token Rotation**: Support for token refresh mechanisms

### Rate Limiting

- **Per-IP Limits**: Configurable rate limits per IP address
- **Provider Limits**: Respect provider-specific rate limits
- **Endpoint Limits**: Different limits for different endpoints

### Audit Logging

All security-sensitive operations are logged:

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

## 📊 Monitoring

### Health Checks

- **Basic Health**: `GET /health` - Application status
- **Detailed Health**: `GET /` - Version and configuration info
- **Provider Health**: Provider status included in stats endpoint

### Metrics

- **API Performance**: Response times, throughput
- **Provider Performance**: Provider response times, error rates
- **OCR Performance**: Processing time, accuracy
- **Vector Search**: Search latency, result quality

## 🔄 Error Handling

### Standard Error Responses

```json
{
  "detail": "Error message description"
}
```

### Provider-Specific Errors

```json
{
  "detail": "Provider error: OpenAI API error: Invalid API key",
  "provider": "openai",
  "operation": "get_embeddings"
}
```

### Common Error Codes

| **Status Code** | **Description** | **Common Causes** |
|----------------|-----------------|------------------|
| **400** | Bad Request | Invalid input data |
| **401** | Unauthorized | Missing or invalid API key |
| **403** | Forbidden | Rate limit exceeded |
| **404** | Not Found | Resource not found |
| **422** | Validation Error | Invalid request format |
| **500** | Internal Server Error | Provider or system error |

## 📚 Related Documentation

- [Plugin Architecture Guide](../development/PLUGIN_ARCHITECTURE.md) - Provider system documentation
- [API Models](models.md) - Request/response models
- [API Examples](examples.md) - Detailed usage examples
- [Authentication](authentication.md) - Security and authentication
- [Endpoints](endpoints.md) - Detailed endpoint documentation 