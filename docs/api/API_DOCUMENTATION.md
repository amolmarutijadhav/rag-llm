# RAG LLM API – API Documentation

## Overview
A production-ready Retrieval-Augmented Generation (RAG) API built with FastAPI, LangChain, and Qdrant Cloud. This API enables document upload, text ingestion, semantic search, question answering, and **conversation-aware enhanced chat completions** using configurable LLM providers and Qdrant vector database with robust field handling.

---

## Key Features

- **Externalized API Configuration**: All external API endpoints are fully configurable via environment variables
- **Robust Field Handling**: Compatible with different field naming conventions (`content` and `page_content`)
- **Complete URL Support**: No path appending - URLs are used directly as configured
- **Collection Management**: Dedicated collection URL for operations like stats and deletion
- **Error Resilience**: Graceful handling of missing or malformed payloads
- **🧠 Conversation-Aware Enhanced Chat Completions**: Advanced conversation analysis with strategy patterns and plugin architecture
- **🎯 Dynamic Strategy Selection**: Automatic selection of optimal processing strategies
- **🔍 Multi-Query RAG**: Enhanced document retrieval through multiple query generation
- **🔌 Plugin Architecture**: Extensible processing pipeline with priority-based execution

---

## Enhanced Chat Completion Architecture

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

### Processing Flow

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

---

## Configuration

### Environment Variables

```bash
# External API Endpoints - Complete URLs (no path appending)
EMBEDDING_API_URL=https://api.openai.com/v1/embeddings
VECTOR_COLLECTION_URL=https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io:6333/collections/documents
VECTOR_INSERT_API_URL=https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io:6333/collections/documents/points
VECTOR_SEARCH_API_URL=https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io:6333/collections/documents/points/search
LLM_API_URL=https://api.openai.com/v1/chat/completions

# API Authentication
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here

# Certificate Configuration
CERT_FILE_PATH=/path/to/your/certificate.cer
VERIFY_SSL=True
CERT_VERIFY_MODE=auto

# Vector Database Configuration
QDRANT_COLLECTION_NAME=documents

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Document Processing Configuration
CHUNK_ID_SEPARATOR=_
DEFAULT_SOURCE_NAME=text_input

# RAG Configuration
RAG_PROMPT_TEMPLATE=You are a helpful AI assistant that answers questions based on the provided context. Use only the information from the context to answer the question. If the context doesn't contain enough information to answer the question, say "I don't have enough information to answer this question."\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:
CONTENT_PREVIEW_LENGTH=200
DEFAULT_TOP_K=3

# AI Model Configuration
EMBEDDING_MODEL=text-embedding-ada-002
LLM_MODEL=gpt-3.5-turbo
VECTOR_SIZE=1536
VECTOR_DISTANCE_METRIC=Cosine

# LLM Parameters
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1000

# Enhanced Chat Configuration
ENHANCED_CHAT_ENABLED=true
DEFAULT_STRATEGY=topic_tracking
PLUGIN_TIMEOUT=30
MAX_ENHANCED_QUERIES=5

# FastAPI Application Configuration
API_TITLE=RAG LLM API
API_DESCRIPTION=A simple RAG (Retrieval-Augmented Generation) API for document Q&A with enhanced chat completions
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

---

## Endpoints

### 1. Health Check
- **GET /**
  - Returns API health and version info.
- **GET /health**
  - Returns a simple health status.

**Response Example:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-05-01T12:00:00"
}
```

### 2. Document Management

#### Upload Document
- **POST /documents/upload**
  - Upload and process documents (PDF, TXT, DOCX) with OCR support.

**Request:**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"
```

**Response:**
```json
{
  "success": true,
  "message": "Document 'document.pdf' added successfully",
  "chunks_processed": 5
}
```

#### Add Text
- **POST /documents/add-text**
  - Add raw text to the knowledge base.

**Request:**
```json
{
  "text": "Your text content here",
  "source_name": "my_text"
}
```

#### Clear Documents
- **DELETE /documents/clear**
  - Clear all documents from the knowledge base.

### 3. Question Answering

#### Ask Question
- **POST /questions/ask**
  - Ask questions and get RAG-enhanced answers.

**Request:**
```json
{
  "question": "What is the main topic?",
  "top_k": 3
}
```

**Response:**
```json
{
  "success": true,
  "answer": "The main topic is...",
  "sources": [
    {
      "content": "Relevant content snippet",
      "metadata": {"source": "document_name"},
      "score": 0.8670988
    }
  ],
  "context_used": "Combined context from retrieved documents"
}
```

### 4. Chat Completions

#### Basic Chat Completions
- **POST /chat/completions**
  - RAG-enhanced chat completions for multi-agentic systems.

**Request:**
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful customer service agent."
    },
    {
      "role": "user",
      "content": "What are the product specifications?"
    }
  ],
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Response:**
```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on our product database..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 45,
    "total_tokens": 195
  },
  "sources": [
    {
      "content": "Product specifications from documentation",
      "metadata": {"source": "product_manual.pdf"},
      "score": 0.95
    }
  ]
}
```

### 5. Enhanced Chat Completions

#### Conversation-Aware Chat Completions
- **POST /enhanced-chat/completions**
  - **Conversation-aware RAG-enhanced chat completions** with advanced features.

**Request:**
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "system",
      "content": "You are a technical support specialist for software products."
    },
    {
      "role": "user",
      "content": "I am having trouble installing the software."
    },
    {
      "role": "assistant",
      "content": "I can help you with the installation. What operating system are you using?"
    },
    {
      "role": "user",
      "content": "Windows 10. I get a permission error."
    }
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
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
        "content": "Based on your Windows 10 system and the permission error you're experiencing, here are the steps to resolve this issue..."
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

#### Get Available Strategies
- **GET /enhanced-chat/strategies**
  - Get available conversation analysis strategies.

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

#### Get Available Plugins
- **GET /enhanced-chat/plugins**
  - Get available processing plugins.

**Response:**
```json
{
  "plugins": [
    {
      "name": "conversation_context",
      "description": "Analyzes conversation context and extracts relevant information",
      "priority": "HIGH"
    },
    {
      "name": "multi_query_rag",
      "description": "Generates multiple enhanced queries for improved document retrieval",
      "priority": "NORMAL"
    },
    {
      "name": "response_enhancement",
      "description": "Enhances final response with context and metadata",
      "priority": "LOW"
    }
  ]
}
```

### 6. System Statistics

#### Get Statistics
- **GET /stats**
  - Get system and vector store statistics.

**Response:**
```json
{
  "success": true,
  "vector_store": {
    "total_documents": 2,
    "collection_name": "documents",
    "vector_size": 1536
  },
  "supported_formats": [".pdf", ".txt", ".docx"],
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

---

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request (validation errors)
- `422`: Unprocessable Entity (invalid data)
- `500`: Internal Server Error

### Common Error Scenarios
- **File Upload Errors**: Invalid format, file too large
- **Processing Errors**: Document processing failures
- **API Errors**: External service failures
- **Validation Errors**: Invalid request data
- **Enhanced Chat Errors**: Missing messages, no user message, strategy selection failures

---

## Performance and Monitoring

### Enhanced Chat Completion Performance

- **Average Response Time**: 10-20 seconds (depending on conversation complexity)
- **Strategy Selection Time**: < 1 second
- **Plugin Processing Time**: 5-15 seconds
- **Enhanced Queries Generated**: 3-5 per request
- **Context Analysis**: Full conversation history

### Monitoring Features

- **Rich Metadata**: Detailed processing information for each request
- **Structured Logging**: JSON format logs with correlation IDs
- **Performance Metrics**: Response times and processing durations
- **Strategy Analytics**: Strategy selection patterns and effectiveness
- **Plugin Performance**: Individual plugin processing times and success rates

---

## Getting Started

### Quick Start Example

```python
import requests

# Enhanced Chat Completion
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

result = response.json()
print(f"Response: {result['choices'][0]['message']['content']}")
print(f"Strategy Used: {result['metadata']['strategy_used']}")
print(f"Enhanced Queries: {result['metadata']['enhanced_queries_count']}")
```

### Multi-Turn Conversation Example

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
print(f"Topics: {second_response['metadata']['conversation_context']['topics']}")
```

---

## Additional Resources

- [API Endpoints Reference](endpoints.md) - Complete endpoint documentation
- [Request/Response Models](models.md) - Data model specifications
- [Usage Examples](examples.md) - Comprehensive examples
- [Enhanced Chat Completion Implementation](../implementation/ENHANCED_CHAT_COMPLETION_IMPLEMENTATION.md) - Technical details
