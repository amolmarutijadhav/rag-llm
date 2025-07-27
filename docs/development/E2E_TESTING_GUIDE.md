# E2E Testing Guide - RAG LLM API

## Overview

This guide covers the comprehensive end-to-end (E2E) testing suite for the RAG LLM API, including file upload functionality, OCR workflow testing, and complete document processing workflows.

## E2E Test Structure

### 📁 Test Files

```
tests/e2e/
├── test_apis.py                           # Basic API endpoint tests
├── test_file_upload.py                    # File upload functionality tests
├── test_ocr_workflow.py                   # OCR workflow processing tests
├── test_document_processing_workflow.py   # Complete document processing workflow
├── test_rag_with_data.py                  # RAG with knowledge base data
└── test_rag_chat_completions.py          # RAG chat completions testing
```

### 🚀 Test Runner

```
scripts/run_e2e_tests.py                   # Comprehensive E2E test runner
```

## Test Categories

### 1. **File Upload Tests** (`test_file_upload.py`)

Tests the complete file upload functionality:

- ✅ **PDF File Upload** - Upload and process PDF documents
- ✅ **DOCX File Upload** - Upload and process DOCX documents  
- ✅ **TXT File Upload** - Upload and process text files
- ✅ **Invalid File Handling** - Test rejection of unsupported formats
- ✅ **Large File Handling** - Test file size limits
- ✅ **Missing File Handling** - Test error handling for missing files
- ✅ **Upload & Question Workflow** - Complete upload → question workflow
- ✅ **Multiple File Uploads** - Test sequential file uploads

### 2. **OCR Workflow Tests** (`test_ocr_workflow.py`)

Tests OCR functionality and workflows:

- ✅ **OCR PDF Workflow** - PDF with embedded images
- ✅ **OCR DOCX Workflow** - DOCX with embedded images
- ✅ **OCR Chat Completions** - OCR with chat functionality
- ✅ **OCR Performance** - Multiple document processing
- ✅ **OCR Error Handling** - Corrupted file handling
- ✅ **OCR Statistics** - System statistics verification

### 3. **Document Processing Workflow** (`test_document_processing_workflow.py`)

Tests complete document processing workflows:

- ✅ **Complete Document Workflow** - End-to-end processing
- ✅ **Multiple Document Types** - Cross-document functionality
- ✅ **Document Chunking** - Large document processing
- ✅ **Document Retrieval Accuracy** - Accuracy verification

### 4. **Existing Tests**

- ✅ **Basic API Endpoints** (`test_apis.py`) - Health, stats, add-text, ask, clear
- ✅ **RAG with Data** (`test_rag_with_data.py`) - Knowledge base testing
- ✅ **RAG Chat Completions** (`test_rag_chat_completions.py`) - Chat functionality

## Running E2E Tests

### Prerequisites

1. **Start the API Server**:
   ```bash
   python run.py
   ```

2. **Verify Server is Running**:
   ```bash
   curl http://localhost:8000/health
   ```

### Running All E2E Tests

```bash
# Run complete E2E test suite
python scripts/run_e2e_tests.py
```

### Running Individual Test Files

```bash
# File upload tests
python tests/e2e/test_file_upload.py

# OCR workflow tests
python tests/e2e/test_ocr_workflow.py

# Document processing workflow tests
python tests/e2e/test_document_processing_workflow.py

# Basic API tests
python tests/e2e/test_apis.py

# RAG with data tests
python tests/e2e/test_rag_with_data.py

# RAG chat completions tests
python tests/e2e/test_rag_chat_completions.py
```

### Running with Pytest

```bash
# Run all e2e tests
pytest tests/e2e/ -v

# Run specific test categories
pytest tests/e2e/ -v -m file_upload
pytest tests/e2e/ -v -m ocr_workflow
pytest tests/e2e/ -v -m document_processing
pytest tests/e2e/ -v -m workflow
```

## Test Dependencies

### Python Dependencies

The E2E tests require additional dependencies for creating test files:

```bash
# For PDF creation
pip install reportlab

# For DOCX creation
pip install python-docx

# For image creation
pip install Pillow
```

### System Dependencies

For OCR functionality tests:
- Tesseract OCR engine
- Poppler utilities

## Test Output

### Sample Output

```
🚀 Starting File Upload E2E Tests
============================================================
📄 Testing PDF file upload...
✅ PDF Upload - Status: 200
   Success: True
   Message: Document 'test_document.pdf' added successfully
   Chunks Processed: 3

📝 Testing DOCX file upload...
✅ DOCX Upload - Status: 200
   Success: True
   Message: Document 'test_document.docx' added successfully
   Chunks Processed: 2

📄 Testing TXT file upload...
✅ TXT Upload - Status: 200
   Success: True
   Message: Document 'test_document.txt' added successfully
   Chunks Processed: 1

============================================================
📊 File Upload E2E Test Results:
============================================================
✅ PASS PDF Upload
✅ PASS DOCX Upload
✅ PASS TXT Upload
✅ PASS Invalid File
✅ PASS Large File
✅ PASS Missing File
✅ PASS Upload & Question Workflow
✅ PASS Multiple File Uploads
============================================================
🎯 Results: 8/8 tests passed
🎉 All file upload e2e tests passed!
============================================================
```

## Test Configuration

### Environment Variables

Ensure these environment variables are set for E2E tests:

```bash
# API Configuration
OPENAI_API_KEY=your_openai_api_key
QDRANT_API_KEY=your_qdrant_api_key

# OCR Configuration
TESSERACT_LANG=eng
OCR_CONFIDENCE_THRESHOLD=60
```

### Test Data

The E2E tests create temporary test files:
- PDF documents with sample text
- DOCX documents with sample content
- TXT files with test data
- Images with embedded text for OCR testing

All temporary files are automatically cleaned up after tests.

## Troubleshooting

### Common Issues

1. **Server Not Running**:
   ```
   ❌ API server is not running
   💡 Please start the server with: python run.py
   ```

2. **Missing Dependencies**:
   ```
   ⚠️ reportlab not available, skipping PDF creation
   ⚠️ python-docx not available, skipping DOCX creation
   ```

3. **OCR Dependencies Missing**:
   ```
   ❌ Tesseract not found
   💡 Install Tesseract OCR engine
   ```

### Debug Mode

Run tests with verbose output:

```bash
# Verbose pytest output
pytest tests/e2e/ -v -s

# Individual test with debug
python tests/e2e/test_file_upload.py --debug
```

## Continuous Integration

### GitHub Actions Integration

Add to your CI pipeline:

```yaml
- name: Run E2E Tests
  run: |
    python run.py &
    sleep 10
    python scripts/run_e2e_tests.py
```

### Docker Testing

Test with Docker deployment:

```bash
# Build and run with Docker
docker-compose up -d

# Run E2E tests against Docker container
python scripts/run_e2e_tests.py
```

## Performance Testing

### Load Testing

For performance validation:

```bash
# Run performance tests
python tests/e2e/test_ocr_workflow.py  # Includes performance tests
```

### Metrics

E2E tests provide performance metrics:
- Upload duration per file type
- Processing time for large documents
- OCR processing performance
- End-to-end workflow timing

## Best Practices

1. **Always Start Server First**: Ensure API server is running before tests
2. **Clean Environment**: Tests clean up temporary files automatically
3. **Check Dependencies**: Verify all required packages are installed
4. **Monitor Resources**: E2E tests can be resource-intensive
5. **Review Logs**: Check server logs for detailed error information

## Summary

The E2E test suite provides comprehensive coverage of:
- ✅ File upload functionality
- ✅ OCR workflow processing
- ✅ Document processing workflows
- ✅ API endpoint functionality
- ✅ RAG functionality
- ✅ Chat completions
- ✅ Error handling
- ✅ Performance validation

This ensures the RAG LLM API works correctly end-to-end in real-world scenarios. 