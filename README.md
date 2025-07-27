# RAG LLM API - Plugin Architecture

A production-ready Retrieval-Augmented Generation (RAG) API built with FastAPI, LangChain, and Qdrant Cloud with **full OCR support**, **plugin architecture for external services**, and **optimized testing**.

## 🚀 Features

- **Document Upload**: Support for PDF, TXT, and DOCX files
- **OCR Processing**: Extract text from images embedded in PDF and DOCX documents
- **Text Input**: Add raw text to the knowledge base
- **Question Answering**: Ask questions and get AI-generated answers
- **Vector Search**: Semantic search using Qdrant Cloud with robust field handling
- **RESTful API**: Clean, documented API endpoints
- **Auto-generated Docs**: Interactive API documentation
- **🔌 Plugin Architecture**: Pluggable external service providers (OpenAI, in-house, etc.)
- **🏭 Factory Pattern**: Dynamic provider selection via configuration
- **🔧 Service Locator**: Centralized provider management
- **Docker Support**: Multi-stage RHEL 9 Docker build with OCR capabilities
- **Optimized Testing**: Fast test execution with strategic external API mocking

## 📋 Prerequisites

- Python 3.8+
- **External Service Providers** (choose one or more):
  - OpenAI API key (default)
  - Qdrant Cloud account (default)
  - In-house embedding/LLM services (optional)
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
   # Edit .env and add your provider API keys and configuration
   ```

## 🏃‍♂️ Quick Start

1. **Start the server**
   ```bash
   python scripts/run.py
   ```

2. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 🧪 Testing

### Fast Development Testing
```bash
# Run fast tests (recommended for development)
pytest -m "not slow"

# Run only integration tests (fast)
pytest tests/integration/ -m "not slow"
```

### Complete Test Coverage
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app
```

### E2E Testing
```bash
# Start server first, then run E2E tests
python scripts/run.py  # In one terminal
python scripts/run_e2e_tests.py  # In another terminal
```

### Test Performance
- **Fast Tests**: 64.21s (1:04) - 84 tests
- **Full Suite**: 153.40s (2:33) - 87 tests
- **Unit Tests**: ~10-15s
- **E2E Tests**: ~4.8 minutes - 6 test categories

### Test Strategy
- **✅ Real OCR Testing**: Tesseract OCR functionality tested
- **✅ Real Business Logic**: RAG service and document processing tested
- **✅ Mocked External APIs**: Provider calls mocked for speed
- **✅ Plugin Architecture Tests**: Provider factory and service locator tested
- **✅ Comprehensive Coverage**: 87 tests covering all functionality

For detailed testing information, see [Testing Guide](docs/development/testing.md).

## 📚 API Endpoints

### Health Check
- `GET /` - Health check and API info
- `GET /health` - Simple health check

### Document Management
- `POST /documents/upload` - Upload and process documents (with OCR support)
- `POST /documents/add-text` - Add raw text to knowledge base
- `DELETE /documents/clear-secure` - Clear knowledge base (secure endpoint)
- `GET /documents/stats` - Get collection statistics

### Question Answering
- `POST /questions/ask` - Ask questions with RAG-enhanced answers
- `POST /chat/completions` - RAG-enhanced chat completions

### Security
- API key authentication for secure endpoints
- Rate limiting and audit logging
- Confirmation tokens for destructive operations

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
│   │   └── config.py              # Centralized configuration with provider support
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities/
│   │   ├── interfaces/            # 🔌 Provider interfaces (ABCs)
│   │   │   ├── __init__.py
│   │   │   └── providers.py       # EmbeddingProvider, VectorStoreProvider, LLMProvider
│   │   ├── models/                # Pydantic models
│   │   └── services/
│   │       ├── __init__.py
│   │       └── rag_service.py     # Main RAG orchestration with provider injection
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── document_processing/
│   │   │   ├── __init__.py
│   │   │   └── loader.py          # Document processing with configurable settings
│   │   ├── providers/             # 🔌 Provider implementations
│   │   │   ├── __init__.py
│   │   │   ├── base_provider.py   # Base HTTP client and common functionality
│   │   │   ├── factory.py         # 🏭 ProviderFactory for dynamic creation
│   │   │   ├── service_locator.py # 🔧 ServiceLocator for provider management
│   │   │   ├── openai_provider.py # OpenAI embedding and LLM providers
│   │   │   ├── qdrant_provider.py # Qdrant vector store provider
│   │   │   └── inhouse_provider.py # In-house provider templates
│   │   └── vector_store/
│   │       ├── __init__.py
│   │       └── vector_store.py    # Vector database operations with provider injection
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
│       └── message_utils.py       # Message formatting utilities
├── tests/
│   ├── unit/                      # Unit tests (including provider tests)
│   ├── integration/               # Integration tests with mocked providers
│   ├── e2e/                       # End-to-end tests
│   └── fixtures/                  # Test fixtures and sample data
├── docs/                          # Comprehensive documentation
├── config/                        # Configuration files
├── scripts/                       # Utility scripts
└── requirements.txt               # Python dependencies
```

## 🔧 Configuration

### Environment Variables

The application uses externalized configuration with plugin architecture support:

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

## 🔌 Plugin Architecture

### Provider System

The API now supports a plugin architecture that allows you to easily switch between different external service providers:

#### Available Providers

1. **Embedding Providers**:
   - `OpenAIEmbeddingProvider` (default)
   - `InhouseEmbeddingProvider` (template)

2. **LLM Providers**:
   - `OpenAILLMProvider` (default)
   - `InhouseLLMProvider` (template)

3. **Vector Store Providers**:
   - `QdrantVectorStoreProvider` (default)
   - `InhouseVectorStoreProvider` (template)

#### Switching Providers

To switch providers, simply update your environment variables:

```bash
# Use OpenAI for everything (default)
PROVIDER_EMBEDDING_TYPE=openai
PROVIDER_LLM_TYPE=openai
PROVIDER_VECTOR_STORE_TYPE=qdrant

# Use in-house services
PROVIDER_EMBEDDING_TYPE=inhouse
PROVIDER_LLM_TYPE=inhouse
PROVIDER_VECTOR_STORE_TYPE=inhouse
```

#### Adding New Providers

To add a new provider:

1. Implement the interface in `app/domain/interfaces/providers.py`
2. Create the provider class in `app/infrastructure/providers/`
3. Update the factory in `app/infrastructure/providers/factory.py`
4. Add configuration support in `app/core/config.py`

For detailed information, see [Plugin Architecture Guide](docs/development/PLUGIN_ARCHITECTURE.md).

## 🚀 Performance

### Test Performance Optimizations

| **Test Configuration** | **Duration** | **Tests** | **Use Case** |
|------------------------|--------------|-----------|--------------|
| **Fast Tests** | 64.21s (1:04) | 84 passed | Development cycles |
| **Full Suite** | 153.40s (2:33) | 87 passed | Complete coverage |
| **Unit Tests** | ~10-15s | All unit tests | Quick validation |
| **E2E Tests** | ~4.8 minutes | 6 categories | Production validation |

### Key Optimizations

- **Provider Mocking**: External service calls mocked for fast testing
- **Real OCR Testing**: Tesseract OCR functionality tested with mocked providers
- **Selective Test Execution**: Mark slow tests for optional execution
- **Comprehensive Coverage**: 87 tests covering all functionality
- **Plugin Architecture Testing**: Provider factory and service locator tested

## 🔒 Security Features

### Secure Clear Endpoint

The `/documents/clear-secure` endpoint includes multiple security measures:

- **API Key Authentication**: Requires valid API key
- **Confirmation Token**: Requires specific confirmation token
- **Rate Limiting**: Limits requests per hour per IP
- **Audit Logging**: Logs all clear operations
- **Deprecated Old Endpoint**: Old `/documents/clear` returns 410 Gone

### Security Configuration

```bash
# Required for secure clear endpoint
CLEAR_ENDPOINT_API_KEY=your_secure_api_key
CLEAR_ENDPOINT_CONFIRMATION_TOKEN=your_confirmation_token
CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR=10
ENABLE_CLEAR_ENDPOINT_AUDIT_LOGGING=true
```

## 📊 Monitoring and Logging

### Audit Logging

The application includes comprehensive audit logging for security-sensitive operations:

```python
# Example audit log entry
{
    'timestamp': 1753614133.0647714,
    'operation': 'clear_knowledge_base_attempt',
    'client_ip': '127.0.0.1',
    'user_agent': 'Mozilla/5.0...',
    'success': True,
    'details': 'Reason: Test verification'
}
```

### Health Checks

- `GET /health` - Basic health check
- `GET /` - Detailed health check with version info

## 🐳 Docker Deployment

### Build and Run

```bash
# Build the Docker image
docker build -t rag-llm-api .

# Run the container
docker run -p 8000:8000 --env-file .env rag-llm-api
```

### Docker Compose

```bash
# Start with Docker Compose
docker-compose up -d
```

## 📚 Documentation

- [API Documentation](docs/api/overview.md) - Complete API reference
- [Plugin Architecture Guide](docs/development/PLUGIN_ARCHITECTURE.md) - Provider system documentation
- [Testing Guide](docs/development/testing.md) - Testing strategy and performance
- [Security Guide](docs/development/CLEAR_ENDPOINT_SECURITY.md) - Security features
- [OCR Setup Guide](docs/development/OCR_SETUP_GUIDE.md) - OCR configuration
- [Architecture Guide](docs/development/architecture.md) - System architecture
- [Deployment Guide](docs/deployment/DOCKER_DEPLOYMENT_GUIDE.md) - Deployment instructions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `pytest -m "not slow"`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

1. Check the [documentation](docs/)
2. Review [troubleshooting guide](docs/tutorials/troubleshooting.md)
3. Open an issue on GitHub
4. Contact the development team

---

**Built with ❤️ using FastAPI, LangChain, and Plugin Architecture** 