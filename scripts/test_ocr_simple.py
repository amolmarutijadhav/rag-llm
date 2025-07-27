#!/usr/bin/env python3
"""
Simple OCR Test Script
Tests OCR functionality with current dependencies and provides status report.
"""

import sys
import os
from pathlib import Path

def test_python_dependencies():
    """Test Python OCR dependencies."""
    print("🔍 Testing Python OCR Dependencies...")
    print("=" * 50)
    
    dependencies = {
        "pytesseract": "Python wrapper for Tesseract OCR",
        "PIL": "Image processing library",
        "pdf2image": "PDF to image conversion",
        "docx": "DOCX processing"
    }
    
    results = {}
    
    for dep, description in dependencies.items():
        try:
            if dep == "PIL":
                from PIL import Image
                version = Image.__version__
                results[dep] = {"status": "✅", "version": version, "description": description}
            else:
                module = __import__(dep)
                version = getattr(module, '__version__', 'unknown')
                results[dep] = {"status": "✅", "version": version, "description": description}
        except ImportError as e:
            results[dep] = {"status": "❌", "version": "not installed", "description": description, "error": str(e)}
    
    for dep, info in results.items():
        print(f"{info['status']} {dep} ({info['description']}) - Version: {info['version']}")
        if "error" in info:
            print(f"    Error: {info['error']}")
    
    return results

def test_system_dependencies():
    """Test system-level OCR dependencies."""
    print("\n🔍 Testing System OCR Dependencies...")
    print("=" * 50)
    
    try:
        import pytesseract
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract OCR Engine - Version: {version}")
            return True
        except Exception as e:
            print(f"❌ Tesseract OCR Engine - Not found or not in PATH")
            print(f"   Error: {e}")
            print(f"   Solution: Install Tesseract OCR engine")
            print(f"   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            print(f"   Linux: sudo apt-get install tesseract-ocr")
            print(f"   macOS: brew install tesseract")
            return False
    except ImportError:
        print("❌ pytesseract not installed")
        return False

def test_image_processing():
    """Test image processing capabilities."""
    print("\n🔍 Testing Image Processing...")
    print("=" * 50)
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a test image
        image = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(image)
        
        # Try to use a font
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 50), "Test OCR Text", fill='black', font=font)
        
        # Save test image
        test_image_path = "test_ocr_image.png"
        image.save(test_image_path)
        
        print(f"✅ Image creation and processing - Test image saved as {test_image_path}")
        
        # Test OCR if Tesseract is available
        if test_system_dependencies():
            try:
                import pytesseract
                text = pytesseract.image_to_string(test_image_path)
                print(f"✅ OCR text extraction - Extracted: '{text.strip()}'")
            except Exception as e:
                print(f"⚠️  OCR text extraction - Failed: {e}")
        else:
            print("⚠️  OCR text extraction - Skipped (Tesseract not available)")
        
        # Clean up
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            
        return True
        
    except Exception as e:
        print(f"❌ Image processing - Failed: {e}")
        return False

def test_pdf_processing():
    """Test PDF processing capabilities."""
    print("\n🔍 Testing PDF Processing...")
    print("=" * 50)
    
    try:
        import pdf2image
        print("✅ pdf2image library - Available")
        
        # Test if poppler is available
        try:
            from pdf2image.pdf2image import check_poppler_version
            version = check_poppler_version()
            print(f"✅ Poppler utilities - Version: {version}")
            return True
        except Exception as e:
            print(f"⚠️  Poppler utilities - Not found or not in PATH")
            print(f"   Error: {e}")
            print(f"   Solution: Install Poppler utilities")
            print(f"   Windows: https://github.com/oschwartz10612/poppler-windows/releases")
            print(f"   Linux: sudo apt-get install poppler-utils")
            print(f"   macOS: brew install poppler")
            return False
            
    except ImportError:
        print("❌ pdf2image not installed")
        return False

def test_docx_processing():
    """Test DOCX processing capabilities."""
    print("\n🔍 Testing DOCX Processing...")
    print("=" * 50)
    
    try:
        import docx
        print("✅ python-docx library - Available")
        
        # Test basic DOCX functionality
        from docx import Document
        doc = Document()
        doc.add_paragraph("Test document")
        print("✅ DOCX document creation - Working")
        
        return True
        
    except ImportError as e:
        print(f"❌ python-docx not installed: {e}")
        return False

def test_application_ocr():
    """Test OCR functionality in the application."""
    print("\n🔍 Testing Application OCR Integration...")
    print("=" * 50)
    
    try:
        # Test the document loader OCR functionality
        from app.infrastructure.document_processing.loader import DocumentLoader
        
        loader = DocumentLoader()
        print(f"✅ DocumentLoader OCR enabled: {loader.image_processing_enabled}")
        
        if loader.image_processing_enabled:
            print("✅ OCR functionality is available in the application")
        else:
            print("⚠️  OCR functionality is disabled (missing dependencies)")
        
        return loader.image_processing_enabled
        
    except Exception as e:
        print(f"❌ Application OCR test failed: {e}")
        return False

def generate_status_report():
    """Generate a comprehensive OCR status report."""
    print("\n📊 OCR Status Report")
    print("=" * 50)
    
    # Test all components
    python_deps = test_python_dependencies()
    system_deps = test_system_dependencies()
    image_processing = test_image_processing()
    pdf_processing = test_pdf_processing()
    docx_processing = test_docx_processing()
    app_ocr = test_application_ocr()
    
    # Summary
    print("\n🎯 Summary")
    print("=" * 50)
    
    python_ok = all(info["status"] == "✅" for info in python_deps.values())
    system_ok = system_deps
    processing_ok = image_processing and pdf_processing and docx_processing
    
    print(f"Python Dependencies: {'✅ All Available' if python_ok else '❌ Some Missing'}")
    print(f"System Dependencies: {'✅ Available' if system_ok else '❌ Missing'}")
    print(f"Processing Capabilities: {'✅ Working' if processing_ok else '❌ Issues'}")
    print(f"Application Integration: {'✅ Enabled' if app_ocr else '⚠️  Disabled'}")
    
    if python_ok and system_ok and processing_ok:
        print("\n🎉 OCR functionality is fully operational!")
        print("   You can now process documents with images and extract text via OCR.")
    elif python_ok and processing_ok:
        print("\n⚠️  OCR functionality is partially available.")
        print("   - Python dependencies: ✅")
        print("   - Processing capabilities: ✅")
        print("   - System dependencies: ❌ (Tesseract OCR engine needed)")
        print("   - The application will work but OCR will be disabled.")
    else:
        print("\n❌ OCR functionality is not available.")
        print("   Please install missing dependencies to enable OCR.")
    
    return python_ok and system_ok and processing_ok

def main():
    """Main function."""
    print("🔍 OCR Functionality Status Check")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("app") or not os.path.exists("requirements.txt"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Generate status report
    ocr_fully_available = generate_status_report()
    
    # Provide next steps
    print("\n🚀 Next Steps")
    print("=" * 50)
    
    if ocr_fully_available:
        print("✅ OCR is fully functional!")
        print("   - Run: python scripts/test_ocr.py")
        print("   - Test with real documents containing images")
        print("   - Check the API documentation for usage")
    else:
        print("📋 To enable full OCR functionality:")
        print("   1. Install system dependencies (see OCR_SETUP_GUIDE.md)")
        print("   2. Run: python scripts/test_ocr.py")
        print("   3. Test with sample documents")
    
    print("\n📚 Documentation:")
    print("   - OCR Setup Guide: docs/development/OCR_SETUP_GUIDE.md")
    print("   - API Documentation: docs/api/")
    print("   - Docker Deployment: docs/deployment/DOCKER_DEPLOYMENT_GUIDE.md")
    
    sys.exit(0 if ocr_fully_available else 1)

if __name__ == "__main__":
    main() 