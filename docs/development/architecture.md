# Architecture Documentation

This document provides a comprehensive overview of the RAG LLM API architecture, including system design, component interactions, and performance considerations.

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   FastAPI App   │    │  External APIs  │
│                 │    │                 │    │                 │
│ • Web Apps      │◄──►│ • API Routes    │◄──►│ • OpenAI        │
│ • Mobile Apps   │    │ • Middleware    │    │ • Qdrant Cloud  │
│ • CLI Tools     │    │ • Services      │    │ • Tesseract OCR │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   File System   │
                       │                 │
                       │ • Temp Files    │
                       │ • Logs          │
                       └─────────────────┘
```

### Core Components

#### 1. API Layer (`app/api/`)
- **Routes**: HTTP endpoint handlers
- **Middleware**: Security, rate limiting, audit logging
- **Validation**: Request/response validation using Pydantic

#### 2. Domain Layer (`app/domain/`)
- **Services**: Business logic (RAG service)
- **Models**: Data models and validation
- **Entities**: Core business entities

#### 3. Infrastructure Layer (`app/infrastructure/`)
- **External APIs**: OpenAI, Qdrant integration
- **Document Processing**: File handling and OCR
- **Vector Store**: Vector database operations

#### 4. Core Layer (`app/core/`)
- **Configuration**: Centralized configuration management
- **Utilities**: Common utilities and helpers

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
5. Embedding Generation (OpenAI)
   ↓
6. Vector Storage (Qdrant)
   ↓
7. Success Response
```

### Question Answering Flow

```
1. Question Input
   ↓
2. Question Embedding (OpenAI)
   ↓
3. Vector Search (Qdrant)
   ↓
4. Context Retrieval
   ↓
5. LLM Generation (OpenAI)
   ↓
6. Response Formatting
   ↓
7. Answer with Sources
```

## 🧪 Testing Architecture

### Testing Strategy

Our testing architecture follows a strategic approach to balance speed, coverage, and reliability:

#### Mocking Strategy

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Client   │    │   FastAPI App   │    │   Mocked APIs   │
│                 │    │                 │    │                 │
│ • HTTP Requests │◄──►│ • Real Business │◄──►│ • Mock OpenAI   │
│ • Response      │    │ • Real OCR      │    │ • Mock Qdrant   │
│ • Validation    │    │ • Real Logic    │    │ • Instant       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### What We Mock vs. What We Test

| **Component** | **Mocked** | **Real Testing** | **Rationale** |
|---------------|------------|------------------|---------------|
| **OpenAI APIs** | ✅ Yes | ❌ No | Speed, reliability |
| **Qdrant APIs** | ✅ Yes | ❌ No | Speed, reliability |
| **RAG Service** | ❌ No | ✅ Yes | Business logic |
| **OCR Processing** | ❌ No | ✅ Yes | Real functionality |
| **Document Loading** | ❌ No | ✅ Yes | File processing |
| **API Endpoints** | ❌ No | ✅ Yes | Contract validation |

#### Performance Impact

| **Test Type** | **Before Mocking** | **After Mocking** | **Improvement** |
|---------------|-------------------|-------------------|-----------------|
| **OCR Tests** | 30-60s each | 0.4-1.5s each | 95-98% faster |
| **Integration Tests** | 161.50s total | 64.21s (fast) | 60% faster |
| **Full Suite** | ~300-400s | 153.40s | 50-60% faster |

### Test Categories

#### 1. Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single function, class, or module
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast execution (~10-15s total)

#### 2. Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and API endpoints
- **Scope**: Multiple components working together
- **Dependencies**: Real business logic, mocked external APIs
- **Speed**: Medium execution (64.21s for fast tests)

#### 3. End-to-End Tests (`tests/e2e/`)
- **Purpose**: Test complete user workflows
- **Scope**: Full application functionality
- **Dependencies**: Real external services (test environment)
- **Speed**: Slow execution (included in full suite)

## 🔧 Component Details

### RAG Service (`app/domain/services/rag_service.py`)

The RAG service orchestrates the entire retrieval-augmented generation process:

```python
class RAGService:
    def __init__(self):
        self.document_loader = DocumentLoader()
        self.vector_store = VectorStore()
        self.external_api_service = ExternalAPIService()
    
    async def add_document(self, file_path: str) -> Dict[str, Any]:
        # 1. Load and process document
        # 2. Extract text (with OCR if needed)
        # 3. Generate embeddings
        # 4. Store in vector database
        # 5. Return success response
    
    async def ask_question(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        # 1. Generate question embedding
        # 2. Search similar documents
        # 3. Retrieve context
        # 4. Generate answer with LLM
        # 5. Return answer with sources
```

### Document Loader (`app/infrastructure/document_processing/loader.py`)

Handles document processing and OCR functionality:

```python
class DocumentLoader:
    def load_document(self, file_path: str) -> Tuple[List[Dict], Optional[str]]:
        # 1. Detect file type
        # 2. Extract text content
        # 3. Process images with OCR (if present)
        # 4. Chunk document into segments
        # 5. Return chunks and OCR text
```

### External API Service (`app/infrastructure/external/external_api_service.py`)

Manages all external API interactions:

```python
class ExternalAPIService:
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Call OpenAI embeddings API
    
    async def insert_vectors(self, points: List[Dict]) -> bool:
        # Call Qdrant insert API
    
    async def search_vectors(self, query_vector: List[float], top_k: int) -> List[Dict]:
        # Call Qdrant search API
    
    async def call_llm(self, messages: List[Dict]) -> str:
        # Call OpenAI chat completions API
```

### Vector Store (`app/infrastructure/vector_store/vector_store.py`)

Manages vector database operations:

```python
class VectorStore:
    async def add_documents(self, documents: List[Dict]) -> bool:
        # 1. Generate embeddings
        # 2. Format points for Qdrant
        # 3. Insert into vector database
    
    async def search(self, query: str, top_k: int = 3) -> List[Dict]:
        # 1. Generate query embedding
        # 2. Search vector database
        # 3. Return relevant documents
```

## 🔒 Security Architecture

### Security Middleware (`app/api/middleware/security.py`)

Implements comprehensive security measures:

```python
class SecurityMiddleware:
    def verify_api_key(self, api_key: str) -> bool:
        # Verify API key for secure endpoints
    
    def verify_confirmation_token(self, token: str) -> bool:
        # Verify confirmation token for destructive operations
    
    def check_rate_limit(self, client_ip: str) -> bool:
        # Check rate limiting per IP
    
    def log_audit_event(self, event_data: Dict) -> None:
        # Log security events for audit trail
```

### Security Features

1. **API Key Authentication**: Required for secure endpoints
2. **Confirmation Tokens**: Required for destructive operations
3. **Rate Limiting**: Per-IP rate limiting for sensitive operations
4. **Audit Logging**: Comprehensive logging of security events
5. **Input Validation**: Pydantic models for request validation

## 📊 Performance Considerations

### Test Performance Optimizations

#### 1. External API Mocking
- **Strategy**: Mock OpenAI and Qdrant calls
- **Benefit**: 95-98% faster OCR tests
- **Implementation**: `@patch` decorators in integration tests

#### 2. Selective Test Execution
- **Strategy**: Mark slow tests with `@pytest.mark.slow`
- **Benefit**: Fast development cycles (64s vs 153s)
- **Implementation**: `pytest -m "not slow"`

#### 3. Real OCR Testing
- **Strategy**: Test real Tesseract OCR with mocked external calls
- **Benefit**: Verify OCR functionality without network delays
- **Implementation**: Real OCR processing, mocked embeddings

### Production Performance

#### 1. Vector Search Optimization
- **Indexing**: Qdrant handles vector indexing automatically
- **Caching**: Consider Redis for frequently accessed data
- **Batch Operations**: Use batch inserts for multiple documents

#### 2. OCR Performance
- **Parallel Processing**: Process multiple images concurrently
- **Image Optimization**: Resize images before OCR processing
- **Caching**: Cache OCR results for repeated documents

#### 3. API Response Optimization
- **Async Operations**: Use async/await for I/O operations
- **Connection Pooling**: Reuse HTTP connections
- **Response Streaming**: Stream large responses

## 🔄 Configuration Management

### Environment-Based Configuration

All configuration is externalized to environment variables:

```python
class Config:
    # OpenAI Configuration
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-ada-002"
    CHAT_MODEL: str = "gpt-3.5-turbo"
    
    # Qdrant Configuration
    QDRANT_API_KEY: str
    QDRANT_URL: str
    QDRANT_COLLECTION_NAME: str = "rag-llm-dev"
    
    # OCR Configuration
    OCR_CONFIDENCE_THRESHOLD: int = 60
    
    # Security Configuration
    CLEAR_ENDPOINT_API_KEY: str
    CLEAR_ENDPOINT_CONFIRMATION_TOKEN: str
    CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR: int = 10
```

### Configuration Benefits

1. **Environment Flexibility**: Easy switching between dev/staging/prod
2. **Security**: Sensitive data kept out of code
3. **Maintainability**: Centralized configuration management
4. **Scalability**: Easy to adjust parameters for different environments

## 🐳 Deployment Architecture

### Docker Support

```dockerfile
# Multi-stage build for optimized image size
FROM python:3.11-slim as builder
# Install dependencies and build

FROM python:3.11-slim as runtime
# Copy built application and run
```

### Container Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   FastAPI App   │    │  External APIs  │
│                 │    │                 │    │                 │
│ • Nginx         │◄──►│ • Container     │◄──►│ • OpenAI        │
│ • SSL/TLS       │    │ • Health Checks │    │ • Qdrant Cloud  │
│ • Rate Limiting │    │ • Logging       │    │ • Tesseract OCR │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📈 Monitoring and Observability

### Health Checks

- **Basic Health**: `GET /health` - Application status
- **Detailed Health**: `GET /` - Version and configuration info

### Audit Logging

```python
# Example audit log structure
{
    'timestamp': 1753614133.0647714,
    'operation': 'clear_knowledge_base_attempt',
    'client_ip': '127.0.0.1',
    'user_agent': 'Mozilla/5.0...',
    'success': True,
    'details': 'Reason: Test verification'
}
```

### Metrics to Monitor

1. **API Performance**: Response times, throughput
2. **OCR Performance**: Processing time, accuracy
3. **Vector Search**: Search latency, result quality
4. **External APIs**: Success rates, error rates
5. **Security Events**: Failed authentications, rate limit hits

## 🔮 Future Architecture Considerations

### Phase 2 Enhancements

1. **Microservices**: Split into separate services
2. **Message Queues**: Async document processing
3. **Caching Layer**: Redis for frequently accessed data
4. **Advanced Search**: Hybrid search (vector + keyword)

### Phase 3 Enhancements

1. **Multiple LLM Support**: Support for different LLM providers
2. **Advanced RAG**: Multi-hop reasoning, graph-based retrieval
3. **Real-time Processing**: WebSocket support for streaming
4. **Advanced Analytics**: Usage analytics and insights

### Scalability Considerations

1. **Horizontal Scaling**: Multiple API instances
2. **Database Scaling**: Qdrant cluster configuration
3. **CDN Integration**: Static asset delivery
4. **Load Balancing**: Intelligent request distribution

## 📚 Additional Resources

- [Testing Guide](testing.md) - Detailed testing strategy
- [Security Guide](CLEAR_ENDPOINT_SECURITY.md) - Security implementation
- [OCR Setup Guide](OCR_SETUP_GUIDE.md) - OCR configuration
- [API Documentation](../api/overview.md) - Complete API reference 