# RAG LLM API – API Documentation

## Overview
A production-ready Retrieval-Augmented Generation (RAG) API built with FastAPI, LangChain, and Qdrant Cloud. This API enables document upload, text ingestion, semantic search, and question answering using configurable LLM providers and Qdrant vector database.

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

---

### 2. Question Answering
- **POST /ask**
  - Ask a question and get an answer using RAG.

**Request Body:**
```json
{
  "question": "Who created Python?",
  "top_k": 3
}
```

**Response Example:**
```json
{
  "success": true,
  "answer": "Python was created by Guido van Rossum.",
  "sources": [
    {
      "content": "Python is a programming language created by Guido van Rossum.",
      "metadata": {"source": "test.txt"},
      "score": 0.95
    }
  ],
  "context_used": "Python is a programming language created by Guido van Rossum."
}
```

---

### 3. Document Upload
- **POST /upload**
  - Upload and process a document (PDF, TXT, DOCX).

**Form Data:**
- `file`: The document file to upload.

**Response Example:**
```json
{
  "success": true,
  "message": "Document 'test.txt' added successfully",
  "chunks_processed": 2
}
```

---

### 4. Add Raw Text
- **POST /add-text**
  - Add raw text to the knowledge base.

**Request Body:**
```json
{
  "text": "Python is a programming language created by Guido van Rossum.",
  "source_name": "python_info"
}
```

**Response Example:**
```json
{
  "success": true,
  "message": "Text from 'python_info' added successfully",
  "chunks_processed": 1
}
```

---

### 5. System Statistics
- **GET /stats**
  - Get system and vector store statistics.

**Response Example:**
```json
{
  "success": true,
  "vector_store": {
    "total_documents": 10,
    "collection_name": "documents",
    "vector_size": 1536
  },
  "supported_formats": [".pdf", ".txt", ".docx"],
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

---

### 6. Clear Knowledge Base
- **DELETE /clear**
  - Delete all documents from the knowledge base.

**Response Example:**
```json
{
  "success": true,
  "message": "Knowledge base cleared successfully"
}
```

---

## Error Handling
- All endpoints return appropriate HTTP status codes and error messages.
- Validation errors return 422.
- Internal errors return 500 with a `detail` field.

---

## Usage Examples

### Upload a Document
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_document.pdf"
```

### Add Text
```bash
curl -X POST "http://localhost:8000/add-text" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your text content here", "source_name": "my_text"}'
```

### Ask a Question
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the main topic?", "top_k": 3}'
```

### Get Statistics
```bash
curl -X GET "http://localhost:8000/stats"
```

---

## Models

### QuestionRequest
- `question`: str (required)
- `top_k`: int (optional, default 3)

### TextInputRequest
- `text`: str (required)
- `source_name`: str (optional, default "text_input")

### QuestionResponse
- `success`: bool
- `answer`: str
- `sources`: list
- `context_used`: str (optional)

### DocumentResponse
- `success`: bool
- `message`: str
- `chunks_processed`: int (optional)

### StatsResponse
- `success`: bool
- `vector_store`: dict
- `supported_formats`: list
- `chunk_size`: int
- `chunk_overlap`: int

### HealthResponse
- `status`: str
- `version`: str
- `timestamp`: str

---

## Interactive Docs
- Visit [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.
- Visit [http://localhost:8000/redoc](http://localhost:8000/redoc) for ReDoc. 