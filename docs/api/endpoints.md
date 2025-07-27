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
  "rag_metadata": {
    "agent_persona_preserved": true,
    "context_documents_found": 2,
    "original_message_count": 2,
    "enhanced_message_count": 2
  }
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