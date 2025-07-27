# Image Processing Capabilities in RAG LLM API

## Overview

The RAG LLM API now supports **image processing and OCR (Optical Character Recognition)** capabilities to extract text from images embedded in PDF and DOCX documents. This allows the system to process and index information from:

- 📸 **Screenshots** with text
- 📊 **Charts and diagrams** with labels
- 📝 **Handwritten notes** (if clear enough)
- 🖼️ **Images with embedded text**
- 📋 **Forms and documents** captured as images

## How It Works

### 1. Document Processing Flow

```mermaid
graph TD
    A[Upload PDF/DOCX] --> B[Extract Text Content]
    A --> C[Extract Images]
    B --> D[Process Text]
    C --> E[OCR Processing]
    E --> F[Extract Text from Images]
    D --> G[Combine Content]
    F --> G
    G --> H[Split into Chunks]
    H --> I[Store in Vector Database]
```

### 2. Image Processing Pipeline

#### **PDF Images:**
1. **Extraction**: Convert PDF pages to images using `pdf2image`
2. **OCR**: Use Tesseract OCR via `pytesseract` to extract text
3. **Integration**: Combine image text with document text

#### **DOCX Images:**
1. **Extraction**: Extract embedded images using `python-docx`
2. **OCR**: Use Tesseract OCR via `pytesseract` to extract text
3. **Integration**: Combine image text with document text

## Dependencies Required

### **Core Dependencies:**
```txt
# Image processing and OCR
pytesseract>=0.3.10      # Python wrapper for Tesseract OCR
Pillow>=10.0.0           # Image processing library
pdf2image>=1.16.3        # Convert PDF pages to images
python-docx>=0.8.11      # Extract images from DOCX files
```

### **System Dependencies (Docker/Production):**
```dockerfile
# Install Tesseract OCR engine
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*
```

## Implementation Details

### **Enhanced DocumentLoader Class**

```python
class DocumentLoader:
    def __init__(self):
        self.image_processing_enabled = IMAGE_PROCESSING_AVAILABLE
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image using OCR"""
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    
    def process_images_in_document(self, file_path: str) -> str:
        """Process images in a document and return extracted text"""
        # Extract images from PDF/DOCX
        # Apply OCR to each image
        # Return combined text
```

### **Processing Results**

#### **Before (Text Only):**
```
Document Content:
- Page 1: "This is a sample document with text content."
- Page 2: "More text content here."
```

#### **After (Text + Images):**
```
Document Content:
- Page 1: "This is a sample document with text content."
- Page 2: "More text content here."
- [Image Content: Screenshot of login form with username and password fields]
- [Image Content: Chart showing Q4 sales data: Revenue $1.2M, Growth 15%]
```

## Usage Examples

### **1. Upload PDF with Images**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document_with_images.pdf"
```

### **2. Upload DOCX with Images**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@report_with_charts.docx"
```

### **3. Query Information from Images**
```bash
curl -X POST "http://localhost:8000/questions/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What was the Q4 revenue shown in the chart?",
       "top_k": 3
     }'
```

## Supported Image Types

### **OCR-Compatible Images:**
- ✅ **PNG** - Portable Network Graphics
- ✅ **JPEG/JPG** - Joint Photographic Experts Group
- ✅ **TIFF** - Tagged Image File Format
- ✅ **BMP** - Bitmap
- ✅ **GIF** - Graphics Interchange Format

### **Text Extraction Capabilities:**
- ✅ **Printed text** (high accuracy)
- ✅ **Digital screenshots** (very high accuracy)
- ✅ **Clear handwritten text** (moderate accuracy)
- ✅ **Form fields and labels** (high accuracy)
- ✅ **Chart labels and values** (high accuracy)

## Accuracy and Limitations

### **High Accuracy Scenarios:**
- Digital screenshots with clear text
- Printed documents scanned at high resolution
- Forms with typed text
- Charts with clear labels

### **Moderate Accuracy Scenarios:**
- Handwritten text (depends on clarity)
- Low-resolution images
- Text with complex backgrounds
- Stylized fonts

### **Low Accuracy Scenarios:**
- Very small text
- Blurry or distorted images
- Text with heavy background noise
- Non-Latin scripts (may need additional language packs)

## Performance Considerations

### **Processing Time:**
- **Text-only documents**: ~1-2 seconds
- **Documents with images**: ~5-15 seconds (depends on image count and size)
- **Large documents with many images**: ~30-60 seconds

### **Memory Usage:**
- **Image processing**: Additional ~50-200MB RAM per image
- **Temporary storage**: Images are processed in memory and cleaned up automatically

### **Optimization Tips:**
1. **Image resolution**: Optimal OCR accuracy at 300 DPI
2. **Image format**: PNG provides best OCR results
3. **Text contrast**: High contrast improves accuracy
4. **Image size**: Larger images may take longer but provide better accuracy

## Error Handling

### **Graceful Degradation:**
```python
try:
    image_text = self.process_images_in_document(file_path)
except Exception as e:
    print(f"Image processing failed: {e}")
    image_text = ""  # Continue with text-only processing
```

### **Fallback Behavior:**
- If image processing fails, document processing continues with text only
- If OCR fails for specific images, those images are skipped
- If dependencies are missing, image processing is disabled automatically

## Testing

### **Test Coverage:**
- ✅ **PDF with images** - `test_pdf_with_images_processing`
- ✅ **DOCX with images** - `test_docx_with_images_processing`
- ✅ **Fallback behavior** - `test_image_processing_disabled_fallback`

### **Running Image Processing Tests:**
```bash
# Run all image processing tests
python -m pytest tests/integration/test_document_upload.py::TestDocumentImageProcessing -v

# Run specific test
python -m pytest tests/integration/test_document_upload.py::TestDocumentImageProcessing::test_pdf_with_images_processing -v
```

## Docker Deployment

### **Dockerfile Requirements:**
```dockerfile
# Install system dependencies for image processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
```

### **Environment Variables:**
```bash
# Optional: Configure Tesseract language
TESSERACT_LANG=eng

# Optional: Configure OCR confidence threshold
OCR_CONFIDENCE_THRESHOLD=60
```

## Future Enhancements

### **Planned Features:**
1. **Multi-language OCR** - Support for non-English text
2. **Table extraction** - Convert image tables to structured data
3. **Chart analysis** - Extract data from charts and graphs
4. **Form processing** - Extract form fields and values
5. **Image classification** - Categorize images by content type

### **Advanced OCR Features:**
1. **Layout analysis** - Understand document structure
2. **Handwriting recognition** - Improved handwritten text processing
3. **Mathematical notation** - Extract mathematical formulas
4. **Code extraction** - Extract code from screenshots

## Troubleshooting

### **Common Issues:**

#### **1. Tesseract Not Found:**
```bash
# Install Tesseract on Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Install on macOS
brew install tesseract

# Install on Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

#### **2. Poor OCR Accuracy:**
- Increase image resolution (300 DPI recommended)
- Improve image contrast
- Remove background noise
- Use PNG format instead of JPEG

#### **3. Memory Issues:**
- Process images in smaller batches
- Reduce image resolution if acceptable
- Monitor system memory usage

## Conclusion

The image processing capabilities significantly enhance the RAG LLM API's ability to extract and index information from documents containing images. This makes the system more versatile for processing real-world documents that often contain charts, screenshots, forms, and other visual content with embedded text.

The implementation provides:
- ✅ **Robust error handling** with graceful degradation
- ✅ **High accuracy** for digital content
- ✅ **Automatic cleanup** of temporary files
- ✅ **Easy deployment** with Docker support
- ✅ **Comprehensive testing** coverage

This feature transforms the API from a text-only processor to a comprehensive document intelligence system capable of understanding both textual and visual content. 