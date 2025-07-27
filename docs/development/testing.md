# Testing Guide

This document provides comprehensive guidance for testing the RAG LLM API, including unit tests, integration tests, and end-to-end tests.

## 🏗️ Test Architecture

### Test Categories

1. **Unit Tests** (`tests/unit/`): Test individual components in isolation
2. **Integration Tests** (`tests/integration/`): Test component interactions and API endpoints
3. **End-to-End Tests** (`tests/e2e/`): Test complete workflows
4. **Performance Tests**: Test system performance and resource usage

### Mocking Strategy

#### External API Mocking
We use a strategic mocking approach to balance test speed and coverage:

- **✅ Mock External APIs**: OpenAI embeddings, Qdrant operations, OpenAI completions
- **✅ Test Real Business Logic**: RAG service, OCR processing, document handling
- **✅ Test Real OCR**: Tesseract OCR functionality with mocked external calls

#### Mocking Configuration
```python
# Example: Mocking external APIs in integration tests
@patch('app.infrastructure.external.external_api_service.ExternalAPIService.get_embeddings')
@patch('app.infrastructure.external.external_api_service.ExternalAPIService.insert_vectors')
@patch('app.infrastructure.external.external_api_service.ExternalAPIService.create_collection_if_not_exists')
def test_ocr_functionality(mock_create_collection, mock_insert_vectors, mock_get_embeddings, client):
    # Setup mocks
    mock_create_collection.return_value = True
    mock_get_embeddings.return_value = [[0.1, 0.2, 0.3] * 1536]
    mock_insert_vectors.return_value = True
    
    # Test real OCR functionality with mocked external calls
    # ... test implementation
```

## 🚀 Performance Optimizations

### Test Execution Times

| **Test Configuration** | **Duration** | **Tests** | **Use Case** |
|------------------------|--------------|-----------|--------------|
| **Full Integration Tests** | 153.40s (2:33) | 87 passed | Complete coverage |
| **Fast Tests Only** | 64.21s (1:04) | 84 passed | Development cycles |
| **Unit Tests** | ~10-15s | All unit tests | Quick validation |

### Slow Test Management

We mark slow tests with `@pytest.mark.slow` to enable selective execution:

```python
@pytest.mark.slow
def test_ocr_text_extraction_accuracy():
    # This test takes 30+ seconds
    pass
```

**Running fast tests only:**
```bash
pytest -m "not slow"  # Excludes slow tests
```

**Running all tests:**
```bash
pytest  # Includes all tests
```

## 📋 Running Tests

### Prerequisites

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install OCR dependencies** (optional but recommended):
   ```bash
   # Windows
   # Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
   
   # Linux
   sudo apt-get install tesseract-ocr poppler-utils
   
   # macOS
   brew install tesseract poppler
   ```

3. **Set up environment variables**:
   ```bash
   cp config/env.example .env
   # Edit .env with your API keys
   ```

### Test Commands

#### Run All Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app
```

#### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# End-to-end tests only
pytest tests/e2e/

# OCR tests only
pytest -m "ocr"
```

#### Run Fast Tests (Recommended for Development)
```bash
# Exclude slow tests
pytest -m "not slow"

# Fast integration tests only
pytest tests/integration/ -m "not slow"
```

#### Run Performance Tests
```bash
# Show test durations
pytest --durations=10

# Run only slow tests
pytest -m "slow"
```

## 🧪 Test Categories

### Unit Tests

Test individual components in isolation:

- **RAG Service**: Business logic testing
- **Document Loader**: File processing and OCR
- **Vector Store**: Database operations
- **External API Service**: API call handling

### Integration Tests

Test component interactions and API endpoints:

#### API Endpoint Tests
- **Health checks**: `/health`, `/`
- **Document management**: Upload, add text, clear
- **Question answering**: Ask questions with RAG
- **Security**: API key validation, rate limiting

#### OCR Functionality Tests
- **PDF OCR**: Extract text from PDF images
- **DOCX OCR**: Extract text from DOCX images
- **Form processing**: Structured data extraction
- **Performance**: Processing time and memory usage

#### Document Upload Tests
- **File formats**: PDF, TXT, DOCX support
- **Error handling**: Invalid files, size limits
- **Edge cases**: Special characters, Unicode content

### End-to-End Tests

Test complete workflows:

- **Document processing workflow**: Upload → OCR → Search → Answer
- **RAG chat completions**: Full conversation flow
- **File upload workflow**: Multiple file types and sizes

## 🔧 Test Configuration

### Pytest Configuration (`pytest.ini`)

```ini
[tool:pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    unit: marks tests as unit tests
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
    api: marks tests as API tests
    rag: marks tests as RAG tests
    document_upload: marks tests as document upload tests
    ocr: marks tests as OCR tests
    ocr_integration: marks tests as OCR integration tests
    ocr_performance: marks tests as OCR performance tests
    real_ocr: marks tests as real OCR tests
    ocr_batch: marks tests as OCR batch processing tests
    ocr_accuracy: marks tests as OCR accuracy tests
```

### Environment Variables for Testing

```bash
# Required for external API mocking
OPENAI_API_KEY=your_openai_key
QDRANT_API_KEY=your_qdrant_key
QDRANT_URL=your_qdrant_url

# Optional: Adjust rate limits for testing
CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR=1000
```

## 📊 Test Performance

### Performance Benchmarks

| **Test Type** | **Before Mocking** | **After Mocking** | **Improvement** |
|---------------|-------------------|-------------------|-----------------|
| **OCR Tests** | 30-60s each | 0.4-1.5s each | 95-98% faster |
| **Integration Tests** | 161.50s total | 64.21s (fast) | 60% faster |
| **Full Suite** | ~300-400s | 153.40s | 50-60% faster |

### Performance Tips

1. **Use fast tests for development**: `pytest -m "not slow"`
2. **Run specific test files**: `pytest tests/integration/test_ocr_functionality.py`
3. **Use parallel execution**: `pytest -n auto` (requires pytest-xdist)
4. **Monitor test durations**: `pytest --durations=10`

## 🐛 Troubleshooting

### Common Issues

#### OCR Tests Failing
```bash
# Check if Tesseract is installed
tesseract --version

# Install Tesseract if missing
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
```

#### External API Errors
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $QDRANT_API_KEY

# Verify API keys are valid
# Tests should use mocked APIs, but real keys are needed for some scenarios
```

#### Test Performance Issues
```bash
# Run only fast tests
pytest -m "not slow"

# Check which tests are slow
pytest --durations=10

# Run specific test categories
pytest tests/unit/  # Fast unit tests
```

### Debug Mode

```bash
# Run tests with debug output
pytest -v -s

# Run specific test with debug
pytest tests/integration/test_ocr_functionality.py::TestOCRFunctionality::test_ocr_extraction_from_pdf_with_image -v -s
```

## 📝 Writing Tests

### Test Structure

```python
import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.integration
class TestOCRFunctionality:
    """Test OCR functionality with mocked external APIs."""
    
    @patch('app.infrastructure.external.external_api_service.ExternalAPIService.get_embeddings')
    @patch('app.infrastructure.external.external_api_service.ExternalAPIService.insert_vectors')
    def test_ocr_extraction(self, mock_insert_vectors, mock_get_embeddings, client):
        """Test OCR extraction with mocked external APIs."""
        # Setup mocks
        mock_get_embeddings.return_value = [[0.1, 0.2, 0.3] * 1536]
        mock_insert_vectors.return_value = True
        
        # Test implementation
        # ... test logic
        
        # Verify mocks were called
        mock_get_embeddings.assert_called()
        mock_insert_vectors.assert_called()
```

### Best Practices

1. **Mock external APIs**: Always mock OpenAI and Qdrant calls
2. **Test real business logic**: Let RAG service and OCR run normally
3. **Use appropriate markers**: Mark tests as `slow`, `integration`, etc.
4. **Clean up resources**: Remove temporary files in `finally` blocks
5. **Verify mock calls**: Ensure external APIs are called as expected

## 🔄 Continuous Integration

### CI/CD Pipeline

The test suite is designed to run efficiently in CI/CD environments:

```yaml
# Example GitHub Actions workflow
- name: Run Fast Tests
  run: pytest -m "not slow" --cov=app

- name: Run Full Test Suite
  run: pytest --cov=app
```

### Test Reports

Generate test reports for CI/CD:

```bash
# Generate coverage report
pytest --cov=app --cov-report=html --cov-report=xml

# Generate JUnit XML report
pytest --junitxml=test-results.xml
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [OCR Setup Guide](ocr_setup_guide.md)
- [API Documentation](api/overview.md) 