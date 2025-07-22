# Testing Guide

This guide covers the comprehensive testing strategy for the RAG LLM API, including test organization, best practices, and running tests.

## 🏗️ Test Structure

The project uses a well-organized testing structure:

```
tests/
├── unit/              # Unit tests - test individual components
├── integration/       # Integration tests - test component interactions
├── e2e/              # End-to-end tests - test complete workflows
├── fixtures/         # Test fixtures and reusable data
├── utils/            # Test utilities and helpers
└── conftest.py       # Pytest configuration and shared fixtures
```

## 🧪 Test Categories

### **Unit Tests** (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Single function, class, or module
- **Dependencies**: Mocked external dependencies
- **Speed**: Fast execution
- **Examples**:
  - `test_rag_service.py` - Test RAG service logic
  - `test_external_api_service.py` - Test external API calls
  - `test_utils.py` - Test utility functions

### **Integration Tests** (`tests/integration/`)
- **Purpose**: Test component interactions
- **Scope**: Multiple components working together
- **Dependencies**: Real or mocked external services
- **Speed**: Medium execution time
- **Examples**:
  - `test_api_endpoints.py` - Test API endpoints
  - `test_document_workflow.py` - Test document processing workflow
  - `test_rag_workflow.py` - Test RAG pipeline

### **End-to-End Tests** (`tests/e2e/`)
- **Purpose**: Test complete user workflows
- **Scope**: Full application functionality
- **Dependencies**: Real external services (test environment)
- **Speed**: Slow execution
- **Examples**:
  - `test_full_rag_pipeline.py` - Complete RAG workflow
  - `test_multi_agent_chat.py` - Multi-agentic chat scenarios
  - `test_performance.py` - Performance benchmarks

## 🎯 Test Markers

The project uses pytest markers for test categorization:

```python
@pytest.mark.unit
def test_rag_service_function():
    """Unit test for RAG service"""
    pass

@pytest.mark.integration
def test_api_endpoint():
    """Integration test for API endpoint"""
    pass

@pytest.mark.e2e
def test_full_workflow():
    """End-to-end test for complete workflow"""
    pass

@pytest.mark.slow
def test_performance():
    """Slow running performance test"""
    pass
```

## 🛠️ Running Tests

### **Run All Tests**
```bash
python -m pytest
```

### **Run by Category**
```bash
# Unit tests only
python -m pytest -m unit

# Integration tests only
python -m pytest -m integration

# End-to-end tests only
python -m pytest -m e2e

# Fast tests (exclude slow)
python -m pytest -m "not slow"
```

### **Run with Coverage**
```bash
python -m pytest --cov=app --cov-report=html
```

### **Run Specific Test File**
```bash
python -m pytest tests/unit/test_rag_service.py
```

### **Run with Verbose Output**
```bash
python -m pytest -v
```

## 📊 Test Fixtures

### **Sample Data Fixtures**
```python
@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        {
            "id": "doc1",
            "content": "Python is a programming language...",
            "metadata": {"source": "test.txt"}
        }
    ]

@pytest.fixture
def sample_question_request():
    """Sample question request"""
    return {
        "question": "Who created Python?",
        "top_k": 3
    }
```

### **Mock Service Fixtures**
```python
@pytest.fixture
def mock_external_api_service():
    """Mock external API service"""
    mock_service = MockExternalAPIService()
    mock_service.get_embeddings.return_value = [[0.1] * 1536]
    return mock_service

@pytest.fixture
def mock_vector_store():
    """Mock vector store"""
    mock_store = MockVectorStore()
    mock_store.search.return_value = []
    return mock_store
```

## 🔧 Test Utilities

### **Response Assertions**
```python
from tests.utils.test_helpers import (
    assert_success_response,
    assert_error_response,
    assert_response_structure
)

def test_api_response():
    response = client.post("/questions/ask", json=request_data)
    data = response.json()
    
    assert_success_response(data)
    assert_response_structure(data, ["success", "answer", "sources"])
```

### **Temporary File Management**
```python
@pytest.fixture
def temp_file_factory():
    """Create temporary files for testing"""
    files = []
    
    def create_file(content, extension=".txt"):
        file_path = create_temp_file(content, extension)
        files.append(file_path)
        return file_path
    
    yield create_file
    
    # Cleanup
    for file_path in files:
        cleanup_temp_file(file_path)
```

## 📈 Coverage Requirements

### **Minimum Coverage Targets**
- **Overall Coverage**: 90%
- **Unit Tests**: 95%
- **Integration Tests**: 85%
- **Critical Paths**: 100%

### **Coverage Reports**
```bash
# Generate HTML coverage report
python -m pytest --cov=app --cov-report=html

# Generate XML coverage report (for CI/CD)
python -m pytest --cov=app --cov-report=xml

# Generate terminal coverage report
python -m pytest --cov=app --cov-report=term-missing
```

## 🚀 Continuous Integration

### **GitHub Actions Workflow**
```yaml
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
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 📝 Best Practices

### **Test Naming**
- Use descriptive test names
- Follow pattern: `test_<function>_<scenario>_<expected_result>`
- Example: `test_ask_question_with_valid_input_returns_answer`

### **Test Organization**
- Group related tests in classes
- Use fixtures for common setup
- Keep tests independent and isolated

### **Mocking Strategy**
- Mock external dependencies
- Use realistic mock data
- Test error scenarios with mocks

### **Assertions**
- Use specific assertions
- Test both success and failure cases
- Verify response structure and content

### **Performance Testing**
- Use `@pytest.mark.slow` for performance tests
- Set reasonable timeouts
- Test with realistic data volumes

## 🔍 Debugging Tests

### **Running Tests in Debug Mode**
```bash
# Run with detailed output
python -m pytest -v -s

# Run single test with debugger
python -m pytest tests/unit/test_rag_service.py::test_specific_function -s

# Run with print statements
python -m pytest -s
```

### **Common Issues**
1. **Import Errors**: Ensure test paths are correct
2. **Mock Issues**: Verify mock setup and return values
3. **Async Issues**: Use `pytest-asyncio` for async tests
4. **Fixture Issues**: Check fixture scope and dependencies

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html) 