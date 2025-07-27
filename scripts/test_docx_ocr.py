#!/usr/bin/env python3
"""
Test script for DOCX OCR functionality
"""

import requests
import json
import os
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_docx_ocr_upload():
    """Test uploading a DOCX file with images for OCR processing"""
    print("📄 Testing DOCX OCR Upload...")
    
    # Create a simple test DOCX file with text
    test_content = """
    This is a test document for OCR processing.
    
    Key points about Java programming:
    1. Java was created by James Gosling at Sun Microsystems
    2. It follows the "Write Once, Run Anywhere" principle
    3. Java is object-oriented and platform-independent
    4. It has automatic memory management through garbage collection
    
    This document should be processed by the RAG system and made searchable.
    """
    
    # Create a temporary text file first
    test_file_path = "test_docx_content.txt"
    with open(test_file_path, "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        # Upload the text file
        with open(test_file_path, "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            response = requests.post(f"{BASE_URL}/documents/upload", files=files)
        
        print(f"✅ Upload Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Message: {result.get('message', 'N/A')}")
            print(f"   Chunks Processed: {result.get('chunks_processed', 'N/A')}")
            print(f"   Source Name: {result.get('source_name', 'N/A')}")
            
            # Now test asking a question about the uploaded content
            print("\n🔍 Testing question about uploaded content...")
            question_data = {
                "question": "Who created Java and what is its main principle?",
                "top_k": 3
            }
            
            question_response = requests.post(
                f"{BASE_URL}/questions/ask",
                json=question_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"✅ Question Status: {question_response.status_code}")
            
            if question_response.status_code == 200:
                question_result = question_response.json()
                print(f"   Answer: {question_result.get('answer', 'N/A')}")
                print(f"   Sources: {question_result.get('sources', [])}")
            else:
                print(f"   Error: {question_response.text}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_docx_ocr_with_real_file():
    """Test with a real DOCX file if available"""
    print("\n📋 Testing with real DOCX file...")
    
    # Check if we have any DOCX files in the project
    docx_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".docx"):
                docx_files.append(os.path.join(root, file))
    
    if docx_files:
        test_file = docx_files[0]
        print(f"   Found DOCX file: {test_file}")
        
        try:
            with open(test_file, "rb") as f:
                files = {"file": (os.path.basename(test_file), f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                response = requests.post(f"{BASE_URL}/documents/upload", files=files)
            
            print(f"✅ Real DOCX Upload Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Message: {result.get('message', 'N/A')}")
                print(f"   Chunks Processed: {result.get('chunks_processed', 'N/A')}")
                print(f"   Source Name: {result.get('source_name', 'N/A')}")
            else:
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("   No DOCX files found in project directory")

def test_ocr_dependencies():
    """Test if OCR dependencies are available"""
    print("\n🔧 Testing OCR Dependencies...")
    
    try:
        import pytesseract
        print("✅ pytesseract is available")
        
        # Check if tesseract is installed
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract version: {version}")
        except Exception as e:
            print(f"❌ Tesseract not found: {e}")
            
    except ImportError:
        print("❌ pytesseract not available")
    
    try:
        from PIL import Image
        print("✅ PIL/Pillow is available")
    except ImportError:
        print("❌ PIL/Pillow not available")
    
    try:
        import pdf2image
        print("✅ pdf2image is available")
    except ImportError:
        print("❌ pdf2image not available")
    
    try:
        import docx
        print("✅ python-docx is available")
    except ImportError:
        print("❌ python-docx not available")

def main():
    """Run all DOCX OCR tests"""
    print("🚀 Starting DOCX OCR Tests")
    print("=" * 50)
    
    # Test OCR dependencies first
    test_ocr_dependencies()
    
    # Test basic upload and question
    test_docx_ocr_upload()
    
    # Test with real DOCX file if available
    test_docx_ocr_with_real_file()
    
    print("\n" + "=" * 50)
    print("✅ DOCX OCR testing completed!")

if __name__ == "__main__":
    main() 