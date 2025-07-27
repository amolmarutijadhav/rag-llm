# OCR Setup Guide

This guide explains how to set up OCR (Optical Character Recognition) functionality for the RAG LLM application.

## Overview

The application supports OCR to extract text from images embedded in PDF and DOCX documents. This enables the system to process documents that contain scanned text, charts, forms, and other image-based content.

## Dependencies

### Python Dependencies

The following Python packages are required and are already included in `requirements.txt`:

```bash
# Core OCR libraries
pytesseract>=0.3.10  # Python wrapper for Tesseract OCR
Pillow>=10.0.0       # Image processing library (PIL)
pdf2image>=1.16.3    # Convert PDF pages to images for OCR
python-docx>=0.8.11  # For extracting images from DOCX files
```

### System Dependencies

#### Windows

1. **Install Tesseract OCR Engine:**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Choose the latest version (e.g., tesseract-ocr-w64-setup-5.4.0.20240606.exe)
   - Install to default location (usually `C:\Program Files\Tesseract-OCR\`)
   - Add to PATH environment variable:
     ```powershell
     $env:PATH += ";C:\Program Files\Tesseract-OCR"
     ```

2. **Install Poppler (for PDF processing):**
   - Install via winget: `winget install oschwartz10612.Poppler`
   - Or download from: https://github.com/oschwartz10612/poppler-windows/releases
   - Add to PATH environment variable:
     ```powershell
     $env:PATH += ";$env:LOCALAPPDATA\Microsoft\WinGet\Packages\oschwartz10612.Poppler_Microsoft.Winget.Source_8wekyb3d8bbwe\poppler-24.08.0\Library\bin"
     ```

3. **Verify Installation:**
   ```powershell
   tesseract --version
   pdftoppm -h
   ```

#### Linux (Ubuntu/Debian)

```bash
# Install Tesseract OCR
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-eng  # English language pack
sudo apt-get install tesseract-ocr-fra  # French language pack
sudo apt-get install tesseract-ocr-deu  # German language pack
sudo apt-get install tesseract-ocr-spa  # Spanish language pack

# Install Poppler
sudo apt-get install poppler-utils
```

#### macOS

```bash
# Install Tesseract OCR
brew install tesseract
brew install tesseract-lang  # Language packs

# Install Poppler
brew install poppler
```

## Installation Steps

### 1. Install Python Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install Python packages
pip install -r requirements.txt
```

### 2. Install System Dependencies

Follow the instructions above for your operating system.

### 3. Verify Installation

```bash
# Test Tesseract installation
python -c "import pytesseract; print('Tesseract version:', pytesseract.get_tesseract_version())"

# Test other dependencies
python -c "from PIL import Image; print('Pillow version:', Image.__version__)"
python -c "import pdf2image; print('pdf2image available')"
python -c "import docx; print('python-docx available')"
```

## Testing OCR Functionality

### Run OCR Tests

```bash
# Run all OCR tests
python scripts/test_ocr.py

# Run simple OCR test
python scripts/test_ocr_simple.py

# Run document upload tests with OCR
pytest tests/integration/test_document_upload.py::TestDocumentImageProcessing -v
```

### Manual Testing

```bash
# Test OCR with a simple image
python -c "
from tests.fixtures.ocr_test_files import create_test_image_with_text
import pytesseract
from PIL import Image

# Create test image with text
img = create_test_image_with_text(['Hello OCR World', 'Testing Tesseract'])
img.save('test_ocr.png')

# Extract text using OCR
text = pytesseract.image_to_string(img)
print(f'OCR Result: {text}')
"
```

## Docker Deployment

When using Docker, all OCR dependencies are automatically included in the RHEL 9 base image:

```bash
# Build and run with Docker
docker-compose up -d

# Or build manually
docker build -t rag-llm-api .
docker run -p 8000:8000 rag-llm-api
```

## Troubleshooting

### Common Issues

1. **Tesseract not found:**
   - Ensure Tesseract is installed and in PATH
   - Windows: Restart IDE/terminal after adding to PATH
   - Linux/macOS: Verify with `which tesseract`

2. **Poppler not found:**
   - Windows: Check WinGet installation path
   - Linux: Install with `sudo apt-get install poppler-utils`
   - macOS: Install with `brew install poppler`

3. **Python dependencies missing:**
   - Activate virtual environment
   - Run `pip install -r requirements.txt`

4. **OCR accuracy issues:**
   - Ensure good image quality
   - Check Tesseract language packs
   - Adjust OCR confidence threshold in config

### Performance Optimization

- **Memory**: OCR processing can be memory-intensive
- **CPU**: Multi-core processing for batch operations
- **Storage**: Temporary files are created during processing
- **Network**: Large documents may take time to upload

## Configuration

### Environment Variables

```bash
# OCR Configuration
TESSERACT_LANG=eng                    # Language for OCR
OCR_CONFIDENCE_THRESHOLD=60           # Minimum confidence for text extraction
```

### Application Settings

The OCR functionality is automatically enabled when dependencies are available. The system will:

1. **Detect images** in PDF and DOCX documents
2. **Extract images** to temporary files
3. **Process with OCR** using Tesseract
4. **Combine text** from document and images
5. **Clean up** temporary files

## Support

For issues with OCR functionality:

1. Check the troubleshooting section above
2. Run `python scripts/test_ocr_simple.py` for diagnostics
3. Review logs for specific error messages
4. Ensure all dependencies are properly installed 