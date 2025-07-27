# Testing Guide

This document provides a comprehensive overview of the testing strategy for the RAG LLM API, including unit tests, integration tests, end-to-end tests, and performance optimizations with the new **Plugin Architecture**.

## 🧪 Testing Strategy

### Overview

Our testing architecture follows a strategic approach to balance speed, coverage, and reliability with the new plugin architecture:

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

### What We Mock vs. What We Test

| **Component** | **Mocked** | **Real Testing** | **Rationale** |
|---------------|------------|------------------|---------------|
| **Provider APIs** | ✅ Yes | ❌ No | Speed, reliability |
| **RAG Service** | ❌ No | ✅ Yes | Business logic |
| **OCR Processing** | ❌ No | ✅ Yes | Real functionality |
| **Document Loading** | ❌ No | ✅ Yes | File processing |
| **API Endpoints** | ❌ No | ✅ Yes | Contract validation |
| **Provider Factory** | ❌ No | ✅ Yes | Provider creation logic |
| **Service Locator** | ❌ No | ✅ Yes | Provider management |

### Performance Impact

| **Test Type** | **Before Mocking** | **After Mocking** | **Improvement** |
|---------------|-------------------|-------------------|-----------------|
| **OCR Tests** | 30-60s each | 0.4-1.5s each | 95-98% faster |
| **Integration Tests** | 161.50s total | 64.21s (fast) | 60% faster |
| **Full Suite** | ~300-400s | 153.40s | 50-60% faster |
| **E2E Tests** | ~10-15 minutes | ~4.8 minutes | 50-60% faster |

## 📊 Test Categories

### 1. Unit Tests (`tests/unit/`)

**Purpose**: Test individual components in isolation
**Scope**: Single function, class, or module
**Dependencies**: Mocked external dependencies
**Speed**: Fast execution (~10-15s total)

#### Provider Unit Tests

```python
# Test provider factory
def test_provider_factory_creates_openai_embedding_provider():
    config = {"type": "openai", "api_key": "test"}
    provider = ProviderFactory.create_embedding_provider(config)
    assert isinstance(provider, OpenAIEmbeddingProvider)

# Test service locator
def test_service_locator_manages_providers():
    locator = ServiceLocator()
    provider = locator.get_embedding_provider()
    assert provider is not None
```

#### Service Unit Tests

```python
# Test RAG service with mocked providers
def test_rag_service_ask_question():
    mock_embedding = MockEmbeddingProvider()
    mock_llm = MockLLMProvider()
    mock_vector = MockVectorStoreProvider()
    
    rag_service = RAGService(
        embedding_provider=mock_embedding,
        llm_provider=mock_llm,
        vector_store_provider=mock_vector
    )
    
    result = await rag_service.ask_question("Test question")
    assert result["success"] is True
```

### 2. Integration Tests (`tests/integration/`)

**Purpose**: Test component interactions and API endpoints
**Scope**: Multiple components working together
**Dependencies**: Real business logic, mocked providers
**Speed**: Medium execution (64.21s for fast tests)

#### Provider Integration Tests

```python
# Test provider integration
def test_rag_service_with_mock_providers():
    with patch_providers_for_test():
        rag_service = RAGService()
        result = await rag_service.ask_question("Test question")
        assert result["success"] is True
```

#### API Integration Tests

```python
# Test API endpoints with mocked providers
def test_api_endpoints_with_mock_providers():
    with patch_providers_for_test():
        response = client.post("/questions/ask", json={"question": "Test"})
        assert response.status_code == 200
```

### 3. End-to-End Tests (`tests/e2e/`)

**Purpose**: Test complete user workflows
**Scope**: Full application functionality
**Dependencies**: Real external services (test environment)
**Speed**: Slow execution (included in full suite)

#### E2E Test Categories

1. **Basic API Endpoints**: Health checks, stats, basic operations
2. **File Upload Functionality**: PDF, DOCX, TXT uploads
3. **OCR Workflow Processing**: Image text extraction
4. **Document Processing Workflow**: Complete document lifecycle
5. **RAG with Knowledge Base Data**: Question answering with data
6. **RAG Chat Completions**: Chat functionality

## 🔌 Provider Testing

### Mock Provider Implementation

```python
class MockEmbeddingProvider(EmbeddingProvider):
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * 1536 for _ in texts]
    
    def get_model_info(self) -> Dict[str, Any]:
        return {"model": "mock-embedding", "dimensions": 1536}

class MockLLMProvider(LLMProvider):
    async def call_llm(self, messages: List[Dict], **kwargs) -> str:
        return "Mock response from LLM"
    
    async def call_llm_api(self, request: Dict, **kwargs) -> Dict:
        return {
            "choices": [{"message": {"content": "Mock response"}}],
            "usage": {"total_tokens": 10}
        }
    
    def get_model_info(self) -> Dict[str, Any]:
        return {"model": "mock-llm", "max_tokens": 1000}

class MockVectorStoreProvider(VectorStoreProvider):
    async def create_collection_if_not_exists(self, collection_name: str) -> bool:
        return True
    
    async def insert_vectors(self, points: List[Dict], collection_name: str) -> bool:
        return True
    
    async def search_vectors(self, query_vector: List[float], top_k: int, collection_name: str) -> List[Dict]:
        return [{"content": "Mock content", "score": 0.9}]
```

### Provider Test Helpers

```python
# Provider test utilities
def patch_providers_for_test():
    """Context manager to patch global provider functions"""
    mock_embedding = MockEmbeddingProvider()
    mock_llm = MockLLMProvider()
    mock_vector = MockVectorStoreProvider()
    
    with patch('app.infrastructure.providers.get_embedding_provider', return_value=mock_embedding), \
         patch('app.infrastructure.providers.get_llm_provider', return_value=mock_llm), \
         patch('app.infrastructure.providers.get_vector_store_provider', return_value=mock_vector):
        yield {
            'embedding': mock_embedding,
            'llm': mock_llm,
            'vector': mock_vector
        }
```

## 🚀 Test Performance Optimizations

### 1. Provider Mocking

**Strategy**: Mock all provider calls
**Benefit**: 95-98% faster provider-dependent tests
**Implementation**: Mock provider interfaces and service locator calls

### 2. Selective Test Execution

**Strategy**: Mark slow tests with `@pytest.mark.slow`
**Benefit**: Fast development cycles (64s vs 153s)
**Implementation**: `pytest -m "not slow"`

### 3. Real OCR Testing

**Strategy**: Test real Tesseract OCR with mocked providers
**Benefit**: Verify OCR functionality without network delays
**Implementation**: Real OCR processing, mocked embeddings

### 4. E2E Test Optimization

**Strategy**: Run E2E tests with real providers but optimized data
**Benefit**: Validate complete workflows efficiently
**Implementation**: Smaller test documents, optimized provider calls

## 📋 Test Execution

### Fast Development Testing

```bash
# Run fast tests (recommended for development)
pytest -m "not slow"

# Run only integration tests (fast)
pytest tests/integration/ -m "not slow"

# Run only unit tests
pytest tests/unit/
```

### Complete Test Coverage

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run with verbose output
pytest -v
```

### E2E Testing

```bash
# Start server first
python scripts/run.py

# In another terminal, run E2E tests
python scripts/run_e2e_tests.py
```

### Provider-Specific Testing

```bash
# Test provider factory
pytest tests/unit/test_providers.py

# Test service locator
pytest tests/unit/test_providers.py::TestServiceLocator

# Test provider integration
pytest tests/integration/test_plugin_architecture_integration.py
```

## 📊 Test Results

### Current Test Performance

| **Test Configuration** | **Duration** | **Tests** | **Use Case** |
|------------------------|--------------|-----------|--------------|
| **Fast Tests** | 64.21s (1:04) | 84 passed | Development cycles |
| **Full Suite** | 153.40s (2:33) | 87 passed | Complete coverage |
| **Unit Tests** | ~10-15s | All unit tests | Quick validation |
| **E2E Tests** | ~4.8 minutes | 6 categories | Production validation |

### Test Coverage

- **Unit Tests**: 58 tests covering individual components
- **Integration Tests**: 29 tests covering component interactions
- **E2E Tests**: 6 test categories covering complete workflows
- **Provider Tests**: Comprehensive provider system testing

## 🔧 Test Configuration

### pytest Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    unit: marks tests as unit tests
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    ocr: marks tests as OCR-related
    providers: marks tests as provider-related
```

### Test Environment Variables

```bash
# Test-specific environment variables
TESTING=true
MOCK_PROVIDERS=true
OCR_CONFIDENCE_THRESHOLD=60
CLEAR_ENDPOINT_API_KEY=test-api-key
CLEAR_ENDPOINT_CONFIRMATION_TOKEN=test-token
```

## 🐛 Debugging Tests

### Common Test Issues

#### 1. Provider Mocking Issues

```python
# Problem: Provider not being mocked correctly
# Solution: Use proper patching
with patch('app.infrastructure.providers.get_embedding_provider') as mock:
    mock.return_value = MockEmbeddingProvider()
    # Test code here
```

#### 2. Async Test Issues

```python
# Problem: Async test not running
# Solution: Add @pytest.mark.asyncio decorator
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

#### 3. E2E Test Issues

```python
# Problem: E2E test failing
# Solution: Check server is running and providers are configured
# Ensure .env file has correct test configuration
```

### Debug Commands

```bash
# Run specific test with verbose output
pytest tests/unit/test_providers.py::test_specific_function -v -s

# Run tests with coverage and show missing lines
pytest --cov=app --cov-report=term-missing

# Run tests and stop on first failure
pytest -x

# Run tests and show local variables on failure
pytest -l
```

## 📈 Continuous Integration

### CI/CD Pipeline

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run fast tests
        run: pytest -m "not slow"
      - name: Run full test suite
        run: pytest
```

### Test Quality Gates

- **Unit Tests**: Must pass 100%
- **Integration Tests**: Must pass 100%
- **Code Coverage**: Minimum 80%
- **Provider Tests**: Must pass 100%

## 🔮 Future Testing Enhancements

### Planned Improvements

1. **Performance Testing**: Load testing with multiple providers
2. **Provider Compatibility Testing**: Test provider switching
3. **Security Testing**: Provider authentication testing
4. **Contract Testing**: Provider API contract validation

### Test Automation

1. **Automated Provider Testing**: Test new provider implementations
2. **Performance Regression Testing**: Monitor test performance over time
3. **Provider Health Monitoring**: Monitor provider availability in tests

## 📚 Related Documentation

- [Plugin Architecture Guide](PLUGIN_ARCHITECTURE.md) - Provider system documentation
- [Architecture Guide](architecture.md) - System architecture overview
- [API Documentation](../api/overview.md) - API testing examples
- [Security Guide](CLEAR_ENDPOINT_SECURITY.md) - Security testing
- [OCR Setup Guide](OCR_SETUP_GUIDE.md) - OCR testing configuration 