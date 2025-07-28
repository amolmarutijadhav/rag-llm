# API Overview

The RAG LLM API provides a comprehensive set of endpoints for document processing, question answering, and knowledge management with **full OCR support**, **plugin architecture for external services**, **conversation-aware enhanced chat completions**, and **optimized performance**.

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

## 🧠 Enhanced Chat Completion Architecture

The API now features **conversation-aware enhanced chat completions** with advanced capabilities:

### Key Features

- **🎯 Conversation Context Analysis**: Analyzes full conversation history for better understanding
- **🔄 Dynamic Strategy Selection**: Automatically selects optimal processing strategy
- **🔍 Multi-Query RAG**: Generates multiple enhanced queries for improved document retrieval
- **🔌 Plugin Architecture**: Extensible processing pipeline with priority-based execution
- **📊 Rich Metadata**: Detailed processing information and analytics

### Available Strategies

| **Strategy** | **Description** | **Use Case** |
|--------------|-----------------|--------------|
| `topic_tracking` | Tracks conversation topics and generates topic-aware queries | General conversations, support scenarios |
| `entity_extraction` | Extracts entities and relationships for enhanced query generation | Data analysis, entity-focused queries |

### Processing Plugins

| **Plugin** | **Priority** | **Description** |
|------------|--------------|-----------------|
| `conversation_context` | HIGH | Analyzes conversation context and extracts relevant information |
| `multi_query_rag` | NORMAL | Generates multiple enhanced queries for improved document retrieval |
| `response_enhancement` | LOW | Enhances final response with context and metadata |

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

### Enhanced Chat Completions

| **Endpoint** | **Method** | **Description** | **Authentication** |
|--------------|------------|-----------------|-------------------|
| `/enhanced-chat/completions` | POST | Conversation-aware RAG-enhanced chat completions | None |
| `/enhanced-chat/strategies` | GET | Get available conversation analysis strategies | None |
| `/enhanced-chat/plugins` | GET | Get available processing plugins | None |

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
  "ocr_processed": true
}
```

### 2. Enhanced Chat Completion with Conversation Context

**Request:**
```bash
curl -X POST "http://localhost:8000/enhanced-chat/completions" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [
         {
           "role": "system",
           "content": "You are a technical support specialist."
         },
         {
           "role": "user",
           "content": "I am having trouble installing the software."
         },
         {
           "role": "assistant",
           "content": "I can help you. What operating system are you using?"
         },
         {
           "role": "user",
           "content": "Windows 10. I get a permission error."
         }
       ],
       "temperature": 0.7,
       "max_tokens": 1000
     }'
```

**Response:**
```json
{
  "id": "chatcmpl-enhanced-1234567890",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on your Windows 10 system and the permission error..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 250,
    "completion_tokens": 120,
    "total_tokens": 370
  },
  "sources": [
    {
      "content": "Windows 10 installation troubleshooting guide",
      "metadata": {"source": "installation_guide.pdf"},
      "score": 0.92
    }
  ],
  "metadata": {
    "conversation_aware": true,
    "strategy_used": "topic_tracking",
    "enhanced_queries_count": 4,
    "conversation_context": {
      "topics": ["software", "installation", "permission", "error", "windows"],
      "entities": ["Windows 10", "permission error"],
      "conversation_length": 4
    },
    "processing_plugins": ["conversation_context", "multi_query_rag", "response_enhancement"]
  }
}
```

### 3. Get Available Strategies

**Request:**
```bash
curl -X GET "http://localhost:8000/enhanced-chat/strategies"
```

**Response:**
```json
{
  "strategies": [
    {
      "name": "topic_tracking",
      "description": "Tracks conversation topics and generates topic-aware queries",
      "features": ["topic_extraction", "context_awareness", "conversation_flow"]
    },
    {
      "name": "entity_extraction",
      "description": "Extracts entities and relationships for enhanced query generation",
      "features": ["entity_recognition", "relationship_mapping", "semantic_analysis"]
    }
  ]
}
```

## 🏗️ Architecture Overview

### Enhanced Chat Completion Flow

```
1. Request Validation
   ↓
2. Strategy Selection (Topic Tracking / Entity Extraction)
   ↓
3. Conversation Context Analysis
   ↓
4. Enhanced Query Generation
   ↓
5. Multi-Query RAG Processing
   ↓
6. Response Enhancement
   ↓
7. Metadata Generation
   ↓
8. Response Delivery
```

### Plugin Processing Pipeline

```
HIGH Priority: Conversation Context Plugin
    ↓
NORMAL Priority: Multi-Query RAG Plugin
    ↓
LOW Priority: Response Enhancement Plugin
```

## 🔧 Configuration

### Environment Variables

```bash
# Enhanced Chat Configuration
ENHANCED_CHAT_ENABLED=true
DEFAULT_STRATEGY=topic_tracking
PLUGIN_TIMEOUT=30
MAX_ENHANCED_QUERIES=5

# Provider Configuration
PROVIDER_EMBEDDING_TYPE=openai
PROVIDER_LLM_TYPE=openai
PROVIDER_VECTOR_STORE_TYPE=qdrant

# API Keys
OPENAI_API_KEY=your_openai_key
QDRANT_API_KEY=your_qdrant_key

# Processing Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=3
```

## 📊 Performance Metrics

### Enhanced Chat Completion Performance

- **Average Response Time**: 10-20 seconds (depending on conversation complexity)
- **Strategy Selection Time**: < 1 second
- **Plugin Processing Time**: 5-15 seconds
- **Enhanced Queries Generated**: 3-5 per request
- **Context Analysis**: Full conversation history

### Scalability Features

- **Concurrent Processing**: Supports multiple simultaneous requests
- **Plugin Timeout**: Configurable timeout for plugin processing
- **Memory Management**: Efficient context handling
- **Caching**: Strategy and plugin result caching

## 🚀 Getting Started

### 1. Basic Enhanced Chat Completion

```python
import requests

data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the weather like today?"}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

response = requests.post(
    "http://localhost:8000/enhanced-chat/completions",
    json=data
)

print(f"Response: {response.json()['choices'][0]['message']['content']}")
print(f"Strategy Used: {response.json()['metadata']['strategy_used']}")
```

### 2. Multi-Turn Conversation

```python
import requests

conversation = [
    {"role": "system", "content": "You are a customer service agent."},
    {"role": "user", "content": "I want to return a product."}
]

# First turn
response = requests.post(
    "http://localhost:8000/enhanced-chat/completions",
    json={"model": "gpt-3.5-turbo", "messages": conversation}
)
first_response = response.json()

# Add assistant response
conversation.append({
    "role": "assistant",
    "content": first_response["choices"][0]["message"]["content"]
})

# Second turn - system remembers context
conversation.append({
    "role": "user",
    "content": "The order number is ORD-12345."
})

response = requests.post(
    "http://localhost:8000/enhanced-chat/completions",
    json={"model": "gpt-3.5-turbo", "messages": conversation}
)
second_response = response.json()

print(f"Enhanced Queries: {second_response['metadata']['enhanced_queries_count']}")
```

## 🔍 Monitoring and Analytics

### Metadata Insights

The enhanced chat completion provides rich metadata for monitoring:

- **Strategy Selection**: Which strategy was used and why
- **Query Generation**: Number and types of enhanced queries
- **Context Analysis**: Topics, entities, and conversation length
- **Plugin Performance**: Processing time and success rates
- **Source Relevance**: Document retrieval scores and sources

### Logging

All enhanced chat completion operations are logged with:

- **Correlation IDs**: For request tracing
- **Structured Logging**: JSON format for easy parsing
- **Performance Metrics**: Response times and processing durations
- **Error Tracking**: Detailed error information

## 📚 Additional Resources

- [API Endpoints Reference](endpoints.md) - Complete endpoint documentation
- [Request/Response Models](models.md) - Data model specifications
- [Usage Examples](examples.md) - Comprehensive examples
- [Enhanced Chat Completion Implementation](../implementation/ENHANCED_CHAT_COMPLETION_IMPLEMENTATION.md) - Technical details
- [Plugin Architecture Guide](../development/PLUGIN_ARCHITECTURE.md) - Plugin development 