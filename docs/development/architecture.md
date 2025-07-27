# System Architecture

## Overview

The RAG LLM API follows a **Domain-Driven Design (DDD)** architecture with clear separation of concerns, enabling scalability, maintainability, and testability.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   FastAPI   │  │   Routes    │  │ Middleware  │      │
│  │ Application │  │   (API)     │  │   (CORS)    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │  Entities   │  │   Models    │  │  Services   │      │
│  │ (Business)  │  │ (Pydantic)  │  │   (RAG)    │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                Infrastructure Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ Document    │  │   Vector    │  │  External   │      │
│  │ Processing  │  │   Store     │  │    APIs     │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    External Services                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   OpenAI    │  │   Qdrant    │  │   Other     │      │
│  │    APIs     │  │    Cloud    │  │  Services   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Layer Details

### 1. Presentation Layer

#### FastAPI Application
- **Framework**: FastAPI with automatic OpenAPI documentation
- **Middleware**: CORS, error handling, request validation
- **Configuration**: Externalized via environment variables

#### API Routes
```python
# Route Structure
app/
├── api/
│   ├── routes/
│   │   ├── health.py      # Health check endpoints
│   │   ├── documents.py   # Document management
│   │   ├── questions.py   # Question answering
│   │   └── chat.py        # RAG-enhanced chat
│   └── middleware/        # CORS and security
```

#### Request/Response Flow
```
Client Request → FastAPI Router → Route Handler → Domain Service → Infrastructure → External API
                ↓
Response ← Domain Model ← Business Logic ← Data Processing ← External Response
```

### 2. Domain Layer

#### Business Entities
- **Document**: Represents uploaded documents with metadata
- **Question**: Represents user questions with context
- **Answer**: Represents generated responses with sources
- **ChatMessage**: Represents multi-agentic chat messages

#### Domain Services
```python
# RAG Service (Core Business Logic)
class RAGService:
    - add_document(file_path)      # Document ingestion
    - add_text(text, source_name)  # Text ingestion
    - ask_question(question, top_k) # Question answering
    - get_stats()                  # System statistics
    - clear_knowledge_base()       # Data cleanup
```

#### Domain Models (Pydantic)
```python
# Request Models
class TextInputRequest(BaseModel):
    text: str
    source_name: Optional[str]

class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int]

# Response Models
class DocumentResponse(BaseModel):
    success: bool
    message: str
    chunks_processed: Optional[int]

class QuestionResponse(BaseModel):
    success: bool
    answer: str
    sources: List[Dict]
    context_used: str
```

### 3. Infrastructure Layer

#### Document Processing
```python
# Document Loader
class DocumentLoader:
    - load_pdf(file_path)    # PDF processing
    - load_txt(file_path)    # Text processing
    - load_docx(file_path)   # Word processing
    - chunk_document(text)   # Text chunking
```

#### Vector Store Integration
```python
# Vector Store Service
class VectorStore:
    - create_collection()     # Collection setup
    - insert_vectors()        # Vector insertion
    - search_vectors()        # Semantic search
    - get_stats()            # Collection stats
    - clear_collection()     # Data cleanup
```

#### External API Service
```python
# External API Integration
class ExternalAPIService:
    - call_openai_embeddings()    # Embedding generation
    - call_openai_completions()   # Chat completions
    - handle_ssl_config()         # SSL/TLS handling
    - retry_with_backoff()        # Error handling
```

## Data Flow

### Document Processing Flow
```
1. File Upload → 2. Validation → 3. Document Loading → 4. Text Extraction
                                                           ↓
8. Response ← 7. Success Response ← 6. Vector Storage ← 5. Chunking & Embedding
```

### Question Answering Flow
```
1. Question Input → 2. Embedding → 3. Vector Search → 4. Context Retrieval
                                                           ↓
7. Response ← 6. Answer Generation ← 5. Prompt Construction
```

### Chat Completion Flow
```
1. Chat Request → 2. Message Validation → 3. RAG Context → 4. Message Enhancement
                                                              ↓
7. Response ← 6. OpenAI Call ← 5. Agent Persona Preservation
```

## Component Interactions

### RAG Service Orchestration
```python
class RAGService:
    def __init__(self):
        self.vector_store = VectorStore()
        self.api_service = ExternalAPIService()
        self.document_loader = DocumentLoader()

    async def add_document(self, file_path: str):
        # 1. Load document
        text = self.document_loader.load_document(file_path)
        
        # 2. Chunk text
        chunks = self.document_loader.chunk_document(text)
        
        # 3. Generate embeddings
        embeddings = await self.api_service.call_openai_embeddings(chunks)
        
        # 4. Store vectors
        await self.vector_store.insert_vectors(embeddings)
        
        return {"success": True, "chunks_processed": len(chunks)}

    async def ask_question(self, question: str, top_k: int = 3):
        # 1. Generate question embedding
        question_embedding = await self.api_service.call_openai_embeddings([question])
        
        # 2. Search similar vectors
        similar_docs = await self.vector_store.search_vectors(question_embedding[0], top_k)
        
        # 3. Construct context
        context = self._build_context(similar_docs)
        
        # 4. Generate answer
        answer = await self.api_service.call_openai_completions(question, context)
        
        return {
            "success": True,
            "answer": answer,
            "sources": similar_docs,
            "context_used": context
        }
```

## Configuration Management

### Centralized Configuration
```python
class Config:
    # External API Endpoints
    EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL")
    VECTOR_COLLECTION_URL = os.getenv("VECTOR_COLLECTION_URL")
    LLM_API_URL = os.getenv("LLM_API_URL")
    
    # Authentication
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    # Processing Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 3
    
    # Model Configuration
    EMBEDDING_MODEL = "text-embedding-ada-002"
    LLM_MODEL = "gpt-3.5-turbo"
    VECTOR_SIZE = 1536
```

### Environment Variable Structure
```bash
# API Configuration
EMBEDDING_API_URL=https://api.openai.com/v1/embeddings
VECTOR_COLLECTION_URL=https://your-cluster.qdrant.io:6333/collections/documents
LLM_API_URL=https://api.openai.com/v1/chat/completions

# Authentication
OPENAI_API_KEY=sk-your-api-key
QDRANT_API_KEY=your-qdrant-api-key

# Processing Settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=3

# Model Settings
EMBEDDING_MODEL=text-embedding-ada-002
LLM_MODEL=gpt-3.5-turbo
VECTOR_SIZE=1536
```

## Security Architecture

### Authentication & Authorization
- **API Key Validation**: Required for all external API calls
- **SSL/TLS Support**: Configurable certificate handling
- **CORS Configuration**: Cross-origin resource sharing
- **Input Validation**: Pydantic model validation

### Security Layers
```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │   CORS      │  │   SSL/TLS   │  │   Input     │      │
│  │ Middleware  │  │   Config    │  │ Validation  │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling

### Error Hierarchy
```python
# Error Handling Strategy
try:
    # Business logic
    result = await service.process_request()
    return result
except ValidationError as e:
    # Input validation errors
    raise HTTPException(status_code=422, detail=str(e))
except ExternalAPIError as e:
    # External service errors
    raise HTTPException(status_code=503, detail=str(e))
except Exception as e:
    # Unexpected errors
    raise HTTPException(status_code=500, detail=str(e))
```

### Error Response Format
```json
{
  "detail": "Error message description",
  "status_code": 400,
  "timestamp": "2024-05-01T12:00:00"
}
```

## Performance Considerations

### Asynchronous Processing
- **Non-blocking Operations**: All external API calls are async
- **Concurrent Processing**: Multiple requests handled simultaneously
- **Connection Pooling**: Reusable HTTP connections

### Caching Strategy
- **Vector Cache**: Embedding results cached for reuse
- **Response Cache**: Frequently asked questions cached
- **Configuration Cache**: Environment variables cached

### Scalability Features
- **Stateless Design**: No server-side state
- **Horizontal Scaling**: Multiple instances supported
- **Load Balancing**: Ready for load balancer deployment

## Testing Architecture

### Test Pyramid
```
┌─────────────────────────────────────────────────────────────┐
│                    E2E Tests (Few)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ API Tests   │  │ Integration │  │ Performance │      │
│  │ (Complete)  │  │   Tests     │  │   Tests     │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                Unit Tests (Many)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ Service     │  │   Model     │  │  Utility    │      │
│  │   Tests     │  │   Tests     │  │   Tests     │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Complete workflow testing
- **Performance Tests**: Load and stress testing

## Deployment Architecture

### Containerization
```dockerfile
# Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configurations
- **Development**: Local development with hot reload
- **Staging**: Pre-production testing environment
- **Production**: Live deployment with monitoring

### Monitoring & Observability
- **Health Checks**: `/health` endpoint for monitoring
- **Metrics**: System statistics via `/stats` endpoint
- **Logging**: Structured logging for debugging
- **Error Tracking**: Comprehensive error handling

## Future Architecture Considerations

### Scalability Improvements
- **Microservices**: Split into smaller services
- **Message Queues**: Async processing with queues
- **Database**: Add persistent storage layer
- **Caching**: Redis for response caching

### Feature Enhancements
- **Multi-tenancy**: Support multiple organizations
- **User Management**: Authentication and authorization
- **Rate Limiting**: API usage limits
- **Analytics**: Usage tracking and insights 