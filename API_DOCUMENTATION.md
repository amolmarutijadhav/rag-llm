# RAG LLM API – API Documentation

## Overview
A production-ready Retrieval-Augmented Generation (RAG) API built with FastAPI, LangChain, and Qdrant Cloud. This API enables document upload, text ingestion, semantic search, and question answering using configurable LLM providers and Qdrant vector database with robust field handling.

---

## Key Features

- **Externalized API Configuration**: All external API endpoints are fully configurable via environment variables
- **Robust Field Handling**: Compatible with different field naming conventions (`content` and `page_content`)
- **Complete URL Support**: No path appending - URLs are used directly as configured
- **Collection Management**: Dedicated collection URL for operations like stats and deletion
- **Error Resilience**: Graceful handling of missing or malformed payloads

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

# Vector Database Configuration
QDRANT_COLLECTION_NAME=documents

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

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

---

### 2. Question Answering
- **POST /ask**
  - Ask a question and get an answer using RAG with robust field handling.

**Request Body:**
```json
{
  "question": "Who created Java?",
  "top_k": 3
}
```

**Response Example:**
```json
{
  "success": true,
  "answer": "Java was created by James Gosling at Sun Microsystems in 1995.",
  "sources": [
    {
      "content": "Java is a high-level, class-based, object-oriented programming language developed by James Gosling at Sun Microsystems in 1995.",
      "metadata": {"source": "java_info", "chunk_index": 0},
      "score": 0.8670988
    },
    {
      "content": "The Python programming language was created by Guido van Rossum and was first released in 1991.",
      "metadata": {"source": "python_info", "chunk_index": 0},
      "score": 0.81351507
    }
  ],
  "context_used": "Java is a high-level, class-based, object-oriented programming language developed by James Gosling at Sun Microsystems in 1995. The Python programming language was created by Guido van Rossum and was first released in 1991."
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
  "text": "Java is a high-level, class-based, object-oriented programming language developed by James Gosling at Sun Microsystems in 1995.",
  "source_name": "java_info"
}
```

**Response Example:**
```json
{
  "success": true,
  "message": "Text from 'java_info' added successfully",
  "chunks_processed": 1
}
```

---

### 5. System Statistics
- **GET /stats**
  - Get system and vector store statistics using dedicated collection URL.

**Response Example:**
```json
{
  "success": true,
  "vector_store": {
    "total_documents": 2,
    "collection_name": "rag-llm-dev",
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
  "message": "Knowledge base cleared successfully",
  "chunks_processed": null
}
```

---

## Error Handling
- All endpoints return appropriate HTTP status codes and error messages.
- Validation errors return 422.
- Internal errors return 500 with a `detail` field.
- Robust error handling for missing or malformed payloads in search results.

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

### Clear Knowledge Base
```bash
curl -X DELETE "http://localhost:8000/clear"
```

---

## Technical Details

### Field Handling
The API now handles inconsistent field names in vector database payloads:
- **Primary Field**: `"content"` - Standard field name for document content
- **Fallback Field**: `"page_content"` - Alternative field name for compatibility
- **Error Handling**: Graceful handling of missing or malformed payloads
- **Backward Compatibility**: Works with existing data that uses different field names

### External API Configuration
- **Complete URLs**: All external API endpoints are fully configurable
- **No Path Appending**: URLs are used directly without modification
- **Flexible Provider Support**: Easy switching between different service providers
- **Collection Management**: Dedicated `VECTOR_COLLECTION_URL` for collection operations

### Vector Database Operations
- **Collection Creation**: Automatic collection creation if it doesn't exist
- **Vector Insertion**: Batch insertion of document vectors with metadata
- **Semantic Search**: Cosine similarity search with configurable top-k results
- **Collection Statistics**: Real-time statistics about stored documents
- **Collection Management**: Full collection lifecycle management

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

## Testing

### Automated Testing
```bash
# Run comprehensive API tests
python test_apis.py

# Run unit tests
python run_tests.py

# Run specific test types
python run_tests.py --type api
python run_tests.py --type rag
```

### Debug Tools
- **test_apis.py**: Comprehensive API testing script
- **debug_search.py**: Debug script for search functionality
- **Interactive Documentation**: Available at `/docs` for manual testing

---

## Interactive Docs
- Visit [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.
- Visit [http://localhost:8000/redoc](http://localhost:8000/redoc) for ReDoc.

---

## Recent Updates

### Search Functionality Fix (Latest)
- **Issue**: Search was failing due to inconsistent field names (`"content"` vs `"page_content"`)
- **Solution**: Added robust field handling in `VectorStore.search()` method
- **Result**: Search now works with both field naming conventions
- **Impact**: Improved compatibility with existing data and different document sources

### External API Externalization
- **Complete URL Configuration**: All external API endpoints are now fully configurable
- **No Path Appending**: URLs are used directly without modification
- **Flexible Provider Support**: Easy switching between different service providers
- **Collection Management**: Dedicated `VECTOR_COLLECTION_URL` for collection operations 