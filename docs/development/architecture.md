# Architecture Documentation

This document provides a comprehensive overview of the RAG LLM API architecture, including system design, component interactions, and performance considerations with the new **Plugin Architecture**.

## 🏗️ System Architecture

### High-Level Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │    │   FastAPI App   │    │  Provider APIs  │
│                 │    │                 │    │                 │
│ • Web Apps      │◄──►│ • API Routes    │◄──►│ • OpenAI        │
│ • Mobile Apps   │    │ • Middleware    │    │ • Qdrant Cloud  │
│ • CLI Tools     │    │ • Services      │    │ • In-House APIs │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Plugin System  │
                       │                 │
                       │ • Provider      │
                       │ • Factory       │
                       │ • Service       │
                       │   Locator       │
                       └─────────────────┘
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
- **🔌 Interfaces**: Provider contracts (ABCs)

#### 3. Infrastructure Layer (`app/infrastructure/`)
- **🔌 Providers**: Plugin-based external service implementations
- **🏭 Factory**: Dynamic provider creation
- **🔧 Service Locator**: Provider instance management
- **Document Processing**: File handling and OCR
- **Vector Store**: Vector database operations

#### 4. Core Layer (`app/core/`)
- **Configuration**: Centralized configuration management with provider support
- **Utilities**: Common utilities and helpers

## 🔌 Plugin Architecture

### Provider System Overview

The plugin architecture allows seamless switching between different external service providers:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   RAG Service   │    │  Service Locator│    │  Provider Types │
│                 │    │                 │    │                 │
│ • ask_question  │◄──►│ • get_provider  │◄──►│ • OpenAI        │
│ • add_document  │    │ • register      │    │ • In-House      │
│ • get_stats     │    │ • reset         │    │ • Custom        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Provider      │
                       │   Factory       │
                       │                 │
                       │ • create_*      │
                       │ • config_based  │
                       │ • dynamic       │
                       └─────────────────┘
```

### Provider Interfaces

#### 1. EmbeddingProvider Interface
```python
class EmbeddingProvider(ABC):
    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]
```

#### 2. LLMProvider Interface
```python
class LLMProvider(ABC):
    @abstractmethod
    async def call_llm(self, messages: List[Dict], **kwargs) -> str
    
    @abstractmethod
    async def call_llm_api(self, request: Dict, **kwargs) -> Dict
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]
```

#### 3. VectorStoreProvider Interface
```python
class VectorStoreProvider(ABC):
    @abstractmethod
    async def create_collection_if_not_exists(self, collection_name: str) -> bool
    
    @abstractmethod
    async def insert_vectors(self, points: List[Dict], collection_name: str) -> bool
    
    @abstractmethod
    async def search_vectors(self, query_vector: List[float], top_k: int, collection_name: str) -> List[Dict]
```

### Provider Implementations

#### OpenAI Providers
- **OpenAIEmbeddingProvider**: Uses OpenAI's embedding API
- **OpenAILLMProvider**: Uses OpenAI's chat completions API

#### Qdrant Provider
- **QdrantVectorStoreProvider**: Uses Qdrant Cloud for vector storage

#### In-House Providers (Templates)
- **InhouseEmbeddingProvider**: Template for custom embedding services
- **InhouseLLMProvider**: Template for custom LLM services
- **InhouseVectorStoreProvider**: Template for custom vector stores

### Factory Pattern

The `ProviderFactory` creates provider instances based on configuration:

```python
class ProviderFactory:
    @staticmethod
    def create_embedding_provider(config: Dict[str, Any]) -> EmbeddingProvider:
        provider_type = config.get("type", "openai")
        if provider_type == "openai":
            return OpenAIEmbeddingProvider(config)
        elif provider_type == "inhouse":
            return InhouseEmbeddingProvider(config)
        # Add more providers here
```

### Service Locator

The `ServiceLocator` manages provider instances and provides dependency injection:

```python
class ServiceLocator:
    def __init__(self):
        self._embedding_provider = None
        self._llm_provider = None
        self._vector_store_provider = None
    
    def get_embedding_provider(self) -> EmbeddingProvider:
        if not self._embedding_provider:
            config = Config.get_embedding_provider_config()
            self._embedding_provider = ProviderFactory.create_embedding_provider(config)
        return self._embedding_provider
```

## 🔄 Data Flow

### Document Processing Flow (with Plugin Architecture)

```
1. Document Upload
   ↓
2. File Validation & Processing
   ↓
3. Text Extraction (OCR if needed)
   ↓
4. Document Chunking
   ↓
5. Embedding Generation (via Provider)
   ↓
6. Vector Storage (via Provider)
   ↓
7. Success Response
```

### Question Answering Flow (with Plugin Architecture)

```
1. Question Input
   ↓
2. Question Embedding (via Provider)
   ↓
3. Vector Search (via Provider)
   ↓
4. Context Retrieval
   ↓
5. LLM Generation (via Provider)
   ↓
6. Response Formatting
   ↓
7. Answer with Sources
```

### Provider Selection Flow

```
1. Service Request
   ↓
2. Service Locator Lookup
   ↓
3. Provider Factory Creation
   ↓
4. Configuration-Based Selection
   ↓
5. Provider Instance Return
   ↓
6. Service Execution
```

## 🧪 Testing Architecture

### Testing Strategy

Our testing architecture follows a strategic approach to balance speed, coverage, and reliability:

#### Mocking Strategy (Updated for Plugin Architecture)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Client   │    │   FastAPI App   │    │  Mock Providers │
│                 │    │                 │    │                 │
│ • HTTP Requests │◄──►│ • Real Business │◄──►│ • Mock Embedding│
│ • Response      │    │ • Real OCR      │    │ • Mock LLM      │
│ • Validation    │    │ • Real Logic    │    │ • Mock Vector   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Provider Testing

#### Unit Tests
- **Provider Factory Tests**: Test provider creation logic
- **Service Locator Tests**: Test provider management
- **Provider Interface Tests**: Test individual provider implementations

#### Integration Tests
- **Provider Integration**: Test provider interactions
- **Service Integration**: Test services with mocked providers
- **End-to-End**: Test complete workflows with real providers

#### Mock Providers
```python
class MockEmbeddingProvider(EmbeddingProvider):
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * 1536 for _ in texts]
    
    def get_model_info(self) -> Dict[str, Any]:
        return {"model": "mock-embedding", "dimensions": 1536}
```

## 🔧 Configuration Architecture

### Provider Configuration

The configuration system supports multiple provider types:

```python
class Config:
    @classmethod
    def get_embedding_provider_config(cls) -> Dict[str, Any]:
        return {
            "type": os.getenv("PROVIDER_EMBEDDING_TYPE", "openai"),
            "api_key": os.getenv("OPENAI_API_KEY"),
            "api_url": os.getenv("OPENAI_API_URL"),
            "model": os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
        }
    
    @classmethod
    def get_llm_provider_config(cls) -> Dict[str, Any]:
        return {
            "type": os.getenv("PROVIDER_LLM_TYPE", "openai"),
            "api_key": os.getenv("OPENAI_API_KEY"),
            "api_url": os.getenv("OPENAI_API_URL"),
            "model": os.getenv("CHAT_MODEL", "gpt-3.5-turbo")
        }
    
    @classmethod
    def get_vector_store_provider_config(cls) -> Dict[str, Any]:
        return {
            "type": os.getenv("PROVIDER_VECTOR_STORE_TYPE", "qdrant"),
            "api_key": os.getenv("QDRANT_API_KEY"),
            "base_url": os.getenv("QDRANT_URL"),
            "collection_name": os.getenv("QDRANT_COLLECTION_NAME", "rag-llm-dev")
        }
```

### Environment Variables

```bash
# Provider Type Configuration
PROVIDER_EMBEDDING_TYPE=openai      # or "inhouse", "cohere"
PROVIDER_LLM_TYPE=openai           # or "inhouse", "anthropic"
PROVIDER_VECTOR_STORE_TYPE=qdrant  # or "inhouse", "pinecone"

# Provider-specific configuration
OPENAI_API_KEY=your_openai_key
QDRANT_API_KEY=your_qdrant_key
INHOUSE_API_KEY=your_inhouse_key
```

## 🚀 Performance Considerations

### Provider Performance

#### Caching Strategy
- **Service Locator**: Caches provider instances
- **Provider Factory**: Creates providers on-demand
- **HTTP Client**: Reuses connections in BaseProvider

#### Optimization Techniques
- **Async Operations**: All provider calls are async
- **Connection Pooling**: HTTPX client with connection reuse
- **Batch Processing**: Embeddings processed in batches
- **Error Handling**: Graceful fallbacks and retries

### Scalability

#### Horizontal Scaling
- **Stateless Design**: Services can be scaled horizontally
- **Provider Independence**: Each provider can be scaled independently
- **Load Balancing**: Multiple provider instances supported

#### Vertical Scaling
- **Resource Optimization**: Efficient memory usage
- **Connection Management**: Optimized HTTP connections
- **Caching**: Provider instance caching

## 🔒 Security Architecture

### Provider Security

#### Authentication
- **API Key Management**: Secure API key handling
- **Provider-Specific Auth**: Each provider can have different auth methods
- **Token Rotation**: Support for token refresh mechanisms

#### Data Protection
- **Encryption**: All external calls use HTTPS
- **Data Validation**: Input validation at provider level
- **Audit Logging**: Provider operation logging

### Security Features

#### Secure Endpoints
- **API Key Authentication**: Required for sensitive operations
- **Rate Limiting**: Per-IP and per-provider limits
- **Audit Logging**: Comprehensive operation logging

## 📊 Monitoring and Observability

### Provider Monitoring

#### Metrics
- **Provider Response Times**: Track provider performance
- **Error Rates**: Monitor provider failures
- **Usage Patterns**: Track provider usage

#### Logging
- **Provider Operations**: Log all provider interactions
- **Error Tracking**: Detailed error logging
- **Performance Metrics**: Response time tracking

### Health Checks

#### Provider Health
- **Provider Availability**: Check provider status
- **Configuration Validation**: Validate provider configs
- **Connection Testing**: Test provider connections

## 🔄 Migration and Compatibility

### Backward Compatibility

#### Legacy Support
- **ExternalAPIService**: Deprecated but still available
- **Configuration Migration**: Automatic config migration
- **Gradual Migration**: Incremental provider adoption

#### Migration Path
1. **Update Configuration**: Add provider type variables
2. **Test Providers**: Validate new provider functionality
3. **Switch Providers**: Update environment variables
4. **Remove Legacy**: Clean up old external service code

### Future Extensibility

#### Adding New Providers
1. **Implement Interface**: Create new provider class
2. **Update Factory**: Add provider to factory
3. **Add Configuration**: Extend config system
4. **Add Tests**: Create provider-specific tests

#### Provider Ecosystem
- **Community Providers**: Support for community-contributed providers
- **Plugin Registry**: Centralized provider registry
- **Version Management**: Provider version compatibility

## 📚 Related Documentation

- [Plugin Architecture Guide](PLUGIN_ARCHITECTURE.md) - Detailed provider system documentation
- [Testing Guide](testing.md) - Testing strategy and implementation
- [Configuration Guide](CONFIGURATION_EXTERNALIZATION.md) - Configuration management
- [Security Guide](CLEAR_ENDPOINT_SECURITY.md) - Security features and implementation 