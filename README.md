# RAG LLM API - Phase 1 MVP

A production-ready Retrieval-Augmented Generation (RAG) API built with FastAPI, LangChain, and Qdrant Cloud with **full OCR support**.

## 🚀 Features

- **Document Upload**: Support for PDF, TXT, and DOCX files
- **OCR Processing**: Extract text from images embedded in PDF and DOCX documents
- **Text Input**: Add raw text to the knowledge base
- **Question Answering**: Ask questions and get AI-generated answers
- **Vector Search**: Semantic search using Qdrant Cloud with robust field handling
- **RESTful API**: Clean, documented API endpoints
- **Auto-generated Docs**: Interactive API documentation
- **Externalized APIs**: Complete URL configuration for all external services
- **Docker Support**: Multi-stage RHEL 9 Docker build with OCR capabilities

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Qdrant Cloud account (free tier available)
- **OCR Dependencies** (optional but recommended):
  - Tesseract OCR Engine
  - Poppler utilities (for PDF processing)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd rag-llm
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install OCR dependencies** (optional)
   ```bash
   # Windows
   # Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
   # Download Poppler from: https://github.com/oschwartz10612/poppler-windows/releases
   
   # Linux
   sudo apt-get install tesseract-ocr poppler-utils
   
   # macOS
   brew install tesseract poppler
   ```

4. **Set up environment variables**
   ```bash
   cp config/env.example .env
   # Edit .env and add your OpenAI API key and Qdrant Cloud credentials
   ```

## 🏃‍♂️ Quick Start

1. **Start the server**
   ```bash
   python run.py
   ```

2. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 📚 API Endpoints

### Health Check
- `GET /` - Health check and API info
- `GET /health` - Simple health check

### Document Management
- `POST /documents/upload` - Upload and process documents (with OCR support)
- `POST /documents/add-text` - Add raw text to knowledge base
- `DELETE /documents/clear` - Clear all documents

### Question Answering
- `POST /questions/ask` - Ask questions and get answers
- `POST /chat/completions` - RAG-enhanced chat completions (OpenAI-compatible)

### System Info
- `GET /stats` - Get system statistics

## 🔧 Configuration

Edit `app/core/config.py` or set environment variables:

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

# Document Processing
MAX_FILE_SIZE=10485760  # 10MB
SUPPORTED_FORMATS=[".pdf", ".txt", ".docx"]

# Document Processing Configuration
CHUNK_ID_SEPARATOR=_
DEFAULT_SOURCE_NAME=text_input

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=3

# RAG Prompt Templates
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

# OCR Configuration
TESSERACT_LANG=eng
OCR_CONFIDENCE_THRESHOLD=60

# FastAPI Application Configuration
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

## 📖 Usage Examples

### 1. Upload a Document
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_document.pdf"
```

### 2. Add Text
```bash
curl -X POST "http://localhost:8000/documents/add-text" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your text content here", "source_name": "my_text"}'
```

### 3. Ask a Question
```bash
curl -X POST "http://localhost:8000/questions/ask" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the main topic?", "top_k": 3}'
```

### 4. RAG-Enhanced Chat Completions
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

### 5. Get Statistics
```bash
curl -X GET "http://localhost:8000/stats"
```

## 🏗️ Project Structure

```
rag-llm/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application with configurable settings
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # Centralized configuration with 15+ externalized constants
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   ├── models/                # Pydantic models
│   │   └── services/
│   │       ├── __init__.py
│   │       └── rag_service.py     # Main RAG orchestration with configurable prompts
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── document_processing/
│   │   │   ├── __init__.py
│   │   │   └── loader.py          # Document processing with configurable settings
│   │   ├── external/
│   │   │   ├── __init__.py
│   │   │   └── external_api_service.py # External API calls with configurable models
│   │   └── vector_store/
│   │       ├── __init__.py
│   │       └── vector_store.py    # Vector database operations
│   ├── api/
│   │   ├── __init__.py
│   │   ├── middleware/
│   │   └── routes/                # API route handlers
│   │       ├── __init__.py
│   │       ├── chat.py            # RAG-enhanced chat completions
│   │       ├── documents.py       # Document management endpoints
│   │       ├── health.py          # Health check endpoints
│   │       └── questions.py       # Question answering endpoints
│   └── utils/
│       ├── __init__.py
│       ├── cert_utils.py          # Certificate management
│       └── message_utils.py       # Message processing utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Test configuration and fixtures
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end tests
├── config/
│   └── env.example                # Environment template with all configuration options
├── docs/                          # Comprehensive documentation
├── requirements.txt               # Python dependencies
├── scripts/                       # Utility scripts
└── README.md                      # This file
```

## 🔍 How It Works

1. **Document Processing**: Documents are loaded, chunked, and embedded using OpenAI embeddings
2. **Vector Storage**: Chunks are stored in Qdrant Cloud with 1536-dimensional vectors
3. **Question Processing**: User questions are embedded and searched using cosine similarity
4. **Context Retrieval**: Most relevant document chunks are retrieved based on semantic similarity
5. **Answer Generation**: GPT-3.5-turbo generates answers using retrieved context

## 🏛️ Technical Architecture

### Core Components
- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: Framework for developing applications with LLMs
- **Qdrant Cloud**: Vector database for storing and searching embeddings
- **Configurable LLM**: Supports OpenAI-compatible endpoints (embeddings and chat completion)

### Data Flow
1. **Document Upload** → Text extraction → Chunking → Embedding → Qdrant storage
2. **Question Input** → Embedding → Vector search → Context retrieval → LLM generation
3. **Response** → Formatted answer with source citations

### Performance Characteristics
- **Embedding Dimension**: 1536 (OpenAI text-embedding-ada-002)
- **Chunk Size**: 1000 characters with 200 character overlap
- **Search Results**: Configurable top-k (default: 3)
- **File Size Limit**: 10MB per upload
- **Supported Formats**: PDF, TXT, DOCX

### External API Configuration
The API now uses completely externalized API endpoints:
- **Embedding API**: `EMBEDDING_API_URL` - Complete URL for text embeddings
- **Vector Collection API**: `VECTOR_COLLECTION_URL` - Complete URL for collection management
- **Vector Insert API**: `VECTOR_INSERT_API_URL` - Complete URL for inserting vectors
- **Vector Search API**: `VECTOR_SEARCH_API_URL` - Complete URL for searching vectors
- **LLM API**: `LLM_API_URL` - Complete URL for LLM completions
- **No Path Appending**: URLs are used directly without any modification
- **Flexibility**: Easy to switch between different providers by changing URLs

### Robust Field Handling
The vector store now handles inconsistent field names in the payload:
- **Primary Field**: `"content"` - Standard field name for document content
- **Fallback Field**: `"page_content"` - Alternative field name for compatibility
- **Error Handling**: Graceful handling of missing or malformed payloads
- **Backward Compatibility**: Works with existing data that uses different field names

## 🧪 Testing

The API includes comprehensive testing with pytest:

### Running Tests
```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type unit      # Unit tests only
python run_tests.py --type api       # API endpoint tests
python run_tests.py --type rag       # RAG functionality tests
python run_tests.py --type fast      # Fast tests (no slow tests)

# Run without coverage
python run_tests.py --no-coverage

# Run quietly
python run_tests.py --quiet
```

### Test Coverage
- **Unit Tests**: RAG service, vector store, document loader
- **API Tests**: All endpoints with validation and error handling
- **Integration Tests**: End-to-end workflows
- **Coverage**: HTML reports generated in `htmlcov/`

### Debug Tools
- **test_apis.py**: Comprehensive API testing script
- **debug_search.py**: Debug script for search functionality
- **Interactive Documentation**: Available at `/docs` for manual testing

### Test the API
Use the interactive documentation at `/docs` to test endpoints manually.

## 🔄 Recent Updates

### Configuration Externalization (Latest)
- **15+ New Configuration Constants**: Externalized all hardcoded values to environment variables
- **RAG Prompt Templates**: Configurable prompt templates via `RAG_PROMPT_TEMPLATE`
- **AI Model Configuration**: Configurable models, parameters, and vector settings
- **FastAPI Application Settings**: Configurable API metadata and CORS settings
- **Document Processing**: Configurable chunk separators and source names
- **Maintainability**: No more magic numbers, centralized configuration management

### Search Functionality Fix
- **Issue**: Search was failing due to inconsistent field names (`"content"` vs `"page_content"`)
- **Solution**: Added robust field handling in `VectorStore.search()` method
- **Result**: Search now works with both field naming conventions
- **Impact**: Improved compatibility with existing data and different document sources

### External API Externalization
- **Complete URL Configuration**: All external API endpoints are now fully configurable
- **No Path Appending**: URLs are used directly without modification
- **Flexible Provider Support**: Easy switching between different service providers
- **Collection Management**: Dedicated `VECTOR_COLLECTION_URL` for collection operations

### RAG-Enhanced Chat Completions
- **New Endpoint**: `/chat/completions` - OpenAI-compatible RAG-enhanced chat
- **Multi-Agentic Support**: Preserves agent personas while adding RAG context
- **Backward Compatibility**: Works with existing OpenAI chat completions clients
- **Context Enhancement**: Automatically enhances responses with relevant knowledge base content

## 🔄 Next Phases

This is Phase 1 MVP. Future phases will include:
- **Phase 2**: Enhanced document processing, better chunking strategies, document metadata
- **Phase 3**: Advanced RAG techniques, hybrid search, multiple LLM support
- **Phase 4**: Microservices architecture, advanced monitoring, caching
- **Phase 5**: Production features, scaling, advanced analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 