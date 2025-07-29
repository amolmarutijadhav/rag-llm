# Test Assets

This directory contains test assets used by various test suites.

## Directory Structure

```
tests/assets/
├── images/           # Test images (PNG, JPG, etc.)
├── documents/        # Test documents (PDF, DOCX, TXT, etc.)
├── data/            # Test data files (JSON, CSV, etc.)
└── README.md        # This file
```

## Asset Categories

### Images
**Location**: `images/`
- **test_ocr.png**: Test image for OCR functionality testing
- Other test images for image processing and OCR tests

### Documents
**Location**: `documents/`
- Sample PDF files for document processing tests
- DOCX files for document upload testing
- Text files for content analysis tests

### Data
**Location**: `data/`
- JSON test data for API testing
- CSV files for data processing tests
- Sample datasets for RAG testing

## File Naming Convention

Test assets follow descriptive naming conventions:
- **Images**: `test_*.png`, `test_*.jpg`
- **Documents**: `sample_*.pdf`, `test_*.docx`
- **Data**: `test_data_*.json`, `sample_*.csv`

## Usage

Test assets are used by:
- Unit tests for file processing functionality
- Integration tests for document upload and processing
- E2E tests for complete workflow validation
- OCR tests for image processing validation

## Maintenance

- Keep test assets small and focused
- Use realistic but minimal test data
- Update assets when test requirements change
- Document any special requirements for specific assets

## Related Tests

- OCR workflow tests use images
- Document processing tests use documents
- API tests use JSON data files
- RAG tests use sample documents and data 