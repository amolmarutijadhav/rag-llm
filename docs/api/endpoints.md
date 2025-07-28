# API Endpoints Reference

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints require proper API key configuration:
- `OPENAI_API_KEY` for OpenAI services
- `QDRANT_API_KEY` for Qdrant Cloud operations

## Endpoints

### Health Check

#### GET /
Returns API health and version information.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-05-01T12:00:00"
}
```

#### GET /health
Returns a simple health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-05-01T12:00:00"
}
```

### Document Management

#### POST /documents/upload
Upload and process a document (PDF, TXT, DOCX).

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (file upload)

**Response:**
```json
{
  "success": true,
  "message": "Document 'example.pdf' added successfully",
  "chunks_processed": 5
}
```

**Error Responses:**
- `400`: File too large or unsupported format
- `500`: Processing error

#### POST /documents/add-text
Add raw text to the knowledge base.

**Request Body:**
```json
{
  "text": "Your text content here",
  "source_name": "my_text"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Text from 'my_text' added successfully",
  "chunks_processed": 1
}
```

#### DELETE /documents/clear
Clear all documents from the knowledge base.

**Response:**
```json
{
  "success": true,
  "message": "Knowledge base cleared successfully"
}
```

### Question Answering

#### POST /questions/ask
Ask a question and get an answer using RAG.

**Request Body:**
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
      "metadata": {"source": "document_name", "chunk_index": 0},
      "score": 0.8670988
    }
  ],
  "context_used": "Combined context from retrieved documents"
}
```

### System Statistics

#### GET /stats
Get system and vector store statistics.

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

### Chat Completions

#### POST /chat/completions
RAG-enhanced chat completions for multi-agentic systems.

**Request Body:**
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

### Enhanced Chat Completions

#### POST /enhanced-chat/completions
**Conversation-aware RAG-enhanced chat completions** with advanced features including:
- **Conversation Context Analysis**: Analyzes full conversation history
- **Dynamic Strategy Selection**: Automatically selects optimal processing strategy
- **Multi-Query RAG**: Generates multiple enhanced queries for better retrieval
- **Plugin Architecture**: Extensible processing pipeline
- **Rich Metadata**: Detailed processing information

**Request Body:**
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
      "content": "I'm having trouble installing the software."
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

#### GET /enhanced-chat/strategies
Get available conversation analysis strategies.

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

#### GET /enhanced-chat/plugins
Get available processing plugins.

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