# RAG LLM API - Phase 1 MVP

A production-ready Retrieval-Augmented Generation (RAG) API built with FastAPI, LangChain, and Qdrant Cloud.

## 🚀 Features

- **Document Upload**: Support for PDF, TXT, and DOCX files
- **Text Input**: Add raw text to the knowledge base
- **Question Answering**: Ask questions and get AI-generated answers
- **Vector Search**: Semantic search using Qdrant Cloud
- **RESTful API**: Clean, documented API endpoints
- **Auto-generated Docs**: Interactive API documentation

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Qdrant Cloud account (free tier available)

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

3. **Set up environment variables**
   ```bash
   cp env.example .env
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
- `POST /upload` - Upload and process documents
- `POST /add-text` - Add raw text to knowledge base
- `DELETE /clear` - Clear all documents

### Question Answering
- `POST /ask` - Ask questions and get answers

### System Info
- `GET /stats` - Get system statistics

## 🔧 Configuration

Edit `src/config.py` or set environment variables:

```python
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Vector Database Configuration - Qdrant Cloud
QDRANT_HOST=https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io
QDRANT_PORT=6333
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=documents

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Document Processing
MAX_FILE_SIZE=10485760  # 10MB
SUPPORTED_FORMATS=[".pdf", ".txt", ".docx"]

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=3
```

## 📖 Usage Examples

### 1. Upload a Document
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_document.pdf"
```

### 2. Add Text
```bash
curl -X POST "http://localhost:8000/add-text" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your text content here", "source_name": "my_text"}'
```

### 3. Ask a Question
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the main topic?", "top_k": 3}'
```

### 4. Get Statistics
```bash
curl -X GET "http://localhost:8000/stats"
```

## 🏗️ Project Structure

```
rag-llm/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── document_loader.py # Document processing
│   ├── vector_store.py    # Qdrant vector database operations
│   ├── rag_service.py     # Main RAG orchestration
│   ├── models.py          # Pydantic models
│   └── main.py           # FastAPI application
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Test configuration and fixtures
│   ├── test_api_endpoints.py      # API endpoint tests
│   ├── test_api_endpoints_sync.py # Synchronous API tests
│   └── test_rag_service.py        # RAG service unit tests
├── requirements.txt       # Python dependencies
├── env.example           # Environment template
├── run.py               # Application runner
├── run_tests.py         # Test runner script
├── pytest.ini          # Pytest configuration
└── README.md            # This file
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
- **OpenAI**: Embeddings (text-embedding-ada-002) and chat completion (gpt-3.5-turbo)

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

### Test the API
Use the interactive documentation at `/docs` to test endpoints manually.

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

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Ensure your OpenAI API key is valid
4. Verify your Qdrant Cloud credentials are correct
5. Check that document formats are supported
6. Run tests to verify your setup: `python run_tests.py`

### Common Issues
- **Qdrant Connection**: Ensure your Qdrant Cloud cluster is active and credentials are correct
- **OpenAI API**: Verify your API key has sufficient credits and is valid
- **File Uploads**: Check file size (max 10MB) and format (PDF, TXT, DOCX) 