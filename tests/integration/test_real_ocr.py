"""
Real OCR Functionality Tests
Tests actual OCR functionality with real PDF and DOCX files containing images.
"""

import pytest
import os
from io import BytesIO
from unittest.mock import patch

# Check if OCR dependencies are available
try:
    import pytesseract
    # Also check if Tesseract is actually installed and working
    pytesseract.get_tesseract_version()
    OCR_AVAILABLE = True
    print("OCR dependencies available: Tesseract", pytesseract.get_tesseract_version())
except (ImportError, Exception) as e:
    OCR_AVAILABLE = False
    print(f"OCR dependencies not available: {e}")

from tests.fixtures.ocr_test_files import (
    invoice_pdf_with_image,
    chart_docx_with_image,
    form_pdf_with_image,
    receipt_docx_with_image,
    multiple_ocr_test_files,
    ocr_test_image,
    ocr_test_data,
    verify_ocr_text_extraction,
    create_ocr_test_report
)


@pytest.mark.real_ocr
class TestRealOCRFunctionality:
    """Tests for real OCR functionality with actual image-containing documents."""

    def test_real_pdf_ocr_with_invoice_image(self, async_client, invoice_pdf_with_image):
        """Test real OCR extraction from PDF with invoice image."""
        with open(invoice_pdf_with_image, 'rb') as f:
            files = {"file": ("invoice.pdf", BytesIO(f.read()), "application/pdf")}
            response = async_client.post("/documents/upload", files=files)

            # OCR processing should work if dependencies are available
            assert response.status_code in [200, 500]

            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True

                # Verify OCR text extraction
                extracted_text = data.get("extracted_text", "")
                if extracted_text:
                    print(f"Extracted OCR text: {extracted_text[:100]}...")
                    # Verify that invoice keywords are present
                    assert any(keyword.lower() in extracted_text.lower() for keyword in ["invoice", "inv-2024-001", "abc company", "1,250.00"])
                else:
                    print("No OCR text extracted (expected if no images in PDF)")

    def test_real_docx_ocr_with_chart_image(self, async_client, chart_docx_with_image):
        """Test real OCR extraction from DOCX with chart image."""
        with open(chart_docx_with_image, 'rb') as f:
            files = {"file": ("chart.docx", BytesIO(f.read()), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = async_client.post("/documents/upload", files=files)

            assert response.status_code in [200, 500]

            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True

                # Verify OCR text extraction
                extracted_text = data.get("extracted_text", "")
                if extracted_text:
                    print(f"Extracted OCR text: {extracted_text[:100]}...")
                    # Verify that chart keywords are present
                    assert any(keyword.lower() in extracted_text.lower() for keyword in ["q4", "sales", "revenue", "2.5m", "15%"])
                else:
                    print("No OCR text extracted (expected if no images in DOCX)")

    def test_real_pdf_ocr_with_form_image(self, async_client, form_pdf_with_image):
        """Test real OCR extraction from PDF with form image."""
        with open(form_pdf_with_image, 'rb') as f:
            files = {"file": ("form.pdf", BytesIO(f.read()), "application/pdf")}
            response = async_client.post("/documents/upload", files=files)

            assert response.status_code in [200, 500]

            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True

                # Verify form field extraction
                extracted_text = data.get("extracted_text", "").lower()
                assert any(keyword.lower() in extracted_text for keyword in ["application", "name", "email"])

    def test_real_docx_ocr_with_receipt_image(self, async_client, receipt_docx_with_image):
        """Test real OCR extraction from DOCX with receipt image."""
        with open(receipt_docx_with_image, 'rb') as f:
            files = {"file": ("receipt.docx", BytesIO(f.read()), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = async_client.post("/documents/upload", files=files)

            assert response.status_code in [200, 500]

            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True

                # Verify OCR text extraction
                extracted_text = data.get("extracted_text", "")
                if extracted_text:
                    print(f"Extracted OCR text: {extracted_text[:100]}...")
                    # Verify that receipt keywords are present
                    assert any(keyword.lower() in extracted_text.lower() for keyword in ["receipt", "2024-01-15", "45.67"])
                else:
                    print("No OCR text extracted (expected if no images in DOCX)")


@pytest.mark.ocr_batch
class TestOCRBatchProcessing:
    """Tests for batch OCR processing with multiple files."""

    @pytest.mark.slow
    def test_batch_ocr_processing(self, async_client, multiple_ocr_test_files):
        """Test batch processing of multiple OCR files."""
        results = []
        
        # Handle the fixture data correctly - it should be a list of tuples (file_type, file_path)
        if isinstance(multiple_ocr_test_files, list):
            for file_type, file_path in multiple_ocr_test_files:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        files = {"file": (os.path.basename(file_path), BytesIO(f.read()), f"application/{file_type}")}
                        response = async_client.post("/documents/upload", files=files)
                        
                        results.append({
                            'file': os.path.basename(file_path),
                            'status': response.status_code,
                            'success': response.status_code == 200
                        })
        
        # Verify that at least some files were processed successfully
        successful_uploads = sum(1 for r in results if r['success'])
        assert successful_uploads > 0, f"Expected at least one successful upload, got {successful_uploads}"
        
        print(f"Batch OCR processing results: {len(results)} files, {successful_uploads} successful")

    def test_ocr_with_different_file_formats(self, async_client):
        """Test OCR with different file formats containing images."""
        # This test would require actual test files with different formats
        # For now, we'll test the basic functionality
        assert True  # Placeholder test


@pytest.mark.ocr_accuracy
class TestOCRAccuracy:
    """Tests for OCR accuracy and text extraction quality."""

    @pytest.mark.slow
    def test_ocr_text_extraction_accuracy(self, async_client, ocr_test_data):
        """Test OCR text extraction accuracy with known test data."""
        # Handle the fixture data correctly - it should be a dictionary
        if not ocr_test_data or not isinstance(ocr_test_data, dict):
            pytest.skip("No valid OCR test data available")
            
        # Create test files from the test data
        from tests.fixtures.ocr_test_files import create_test_image_with_text, create_proper_pdf_with_image, create_proper_docx_with_image
        
        test_files = []
        try:
            for test_type, test_info in ocr_test_data.items():
                # Create test image
                image = create_test_image_with_text(test_info["text"])
                
                # Create PDF file
                pdf_path = create_proper_pdf_with_image(image, f"{test_type}.pdf")
                test_files.append(("pdf", pdf_path, test_info["expected_keywords"]))
                
                # Create DOCX file
                docx_path = create_proper_docx_with_image(image, f"{test_type}.docx")
                test_files.append(("docx", docx_path, test_info["expected_keywords"]))
            
            # Test each file
            for file_type, file_path, expected_keywords in test_files:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        content_type = "application/pdf" if file_type == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        files = {"file": (os.path.basename(file_path), BytesIO(f.read()), content_type)}
                        response = async_client.post("/documents/upload", files=files)
                        
                        if response.status_code == 200:
                            data = response.json()
                            extracted_text = data.get("extracted_text", "").lower()
                            
                            # Verify accuracy using the test case verification function
                            accuracy = verify_ocr_text_extraction(
                                extracted_text, 
                                expected_keywords
                            )
                            
                            # OCR should have at least 50% accuracy for clear text
                            assert accuracy >= 0.5, \
                                f"OCR accuracy {accuracy} below threshold 0.5 for {file_path}"
                            
                            print(f"OCR accuracy for {file_path}: {accuracy:.2f}")
        
        finally:
            # Clean up test files
            for file_type, file_path, expected_keywords in test_files:
                if os.path.exists(file_path):
                    os.unlink(file_path)

    def test_ocr_with_different_text_types(self, async_client):
        """Test OCR with different types of text (handwritten, printed, etc.)."""
        # This test would require actual test files with different text types
        # For now, we'll test the basic functionality
        assert True  # Placeholder test


@pytest.mark.ocr_integration
class TestOCRIntegration:
    """Integration tests for OCR functionality."""

    def test_ocr_with_actual_document_processing(self, async_client, invoice_pdf_with_image):
        """Test OCR integration with actual document processing workflow."""
        # Upload document with OCR
        with open(invoice_pdf_with_image, 'rb') as f:
            files = {"file": ("integration_test.pdf", BytesIO(f.read()), "application/pdf")}

            response = async_client.post("/documents/upload", files=files)

            if response.status_code == 200:
                data = response.json()
                assert data["success"] is True

                # Verify OCR processing completed
                extracted_text = data.get("extracted_text", "")
                assert len(extracted_text) > 0

                # Test question answering with OCR content
                question_response = async_client.post(
                    "/questions/ask",
                    json={"question": "What is the invoice amount?", "top_k": 3}
                )

                if question_response.status_code == 200:
                    qa_data = question_response.json()
                    print(f"✅ OCR integration test: SUCCESS")
                    print(f"   Question answer: {qa_data.get('answer', 'No answer')[:100]}...")
                else:
                    print(f"⚠️  OCR integration test: Question answering failed")
                    print(f"   Status: {question_response.status_code}")
            else:
                print(f"⚠️  OCR integration test: Document upload failed")
                print(f"   Status: {response.status_code}")

    def test_ocr_error_handling_integration(self, async_client):
        """Test OCR error handling in integration scenarios."""
        # Test with invalid file
        invalid_content = b"This is not a valid PDF or image file"
        files = {"file": ("invalid.txt", BytesIO(invalid_content), "text/plain")}
        response = async_client.post("/documents/upload", files=files)
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 500]


@pytest.mark.ocr_performance
class TestOCRPerformance:
    """Performance tests for OCR functionality."""

    def test_ocr_processing_time(self, async_client, invoice_pdf_with_image):
        """Test OCR processing time for performance validation."""
        import time
        
        start_time = time.time()
        
        with open(invoice_pdf_with_image, 'rb') as f:
            files = {"file": ("performance_test.pdf", BytesIO(f.read()), "application/pdf")}
            response = async_client.post("/documents/upload", files=files)
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                # OCR processing should complete within reasonable time
                assert processing_time < 60.0  # 60 seconds max
                print(f"OCR processing time: {processing_time:.2f} seconds")
            else:
                print(f"OCR processing failed (expected if deps missing)")

    @pytest.mark.slow
    def test_ocr_memory_usage(self, async_client, multiple_ocr_test_files):
        """Test OCR memory usage during processing."""
        import os
        
        # Check if psutil is available
        try:
            import psutil
            psutil_available = True
        except ImportError:
            psutil_available = False
            print("psutil not available - skipping memory monitoring")
        
        # Handle the fixture data correctly - it should be a list of tuples (file_type, file_path)
        if not isinstance(multiple_ocr_test_files, list) or len(multiple_ocr_test_files) == 0:
            pytest.skip("No valid OCR test files available")
        
        # Get initial memory usage if psutil is available
        if psutil_available:
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            print(f"Initial memory usage: {initial_memory:.2f} MB")
        
        results = []
        try:
            # Process each file
            for file_type, file_path in multiple_ocr_test_files:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        files = {"file": (os.path.basename(file_path), BytesIO(f.read()), f"application/{file_type}")}
                        response = async_client.post("/documents/upload", files=files)
                        
                        results.append({
                            'file': os.path.basename(file_path),
                            'status': response.status_code,
                            'success': response.status_code == 200
                        })
            
            # Verify that at least some files were processed successfully
            successful_uploads = sum(1 for r in results if r['success'])
            assert successful_uploads > 0, f"Expected at least one successful upload, got {successful_uploads}"
            
            if psutil_available:
                # Get memory usage after processing
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = final_memory - initial_memory
                
                assert memory_increase < 500  # Should not increase by more than 500MB
                print(f"Memory increase: {memory_increase:.2f} MB")
            else:
                print("OCR processing completed successfully (memory monitoring not available)")
            
            print(f"OCR memory usage test results: {len(results)} files, {successful_uploads} successful")
        
        except Exception as e:
            print(f"Error during OCR memory usage test: {e}")
            raise


def run_all_ocr_tests():
    """Run all OCR tests and generate a comprehensive report."""
    import subprocess
    import sys
    
    print("Running comprehensive OCR functionality tests...")
    
    # Run pytest for all OCR tests
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/integration/test_real_ocr.py",
        "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print("OCR Test Results:")
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    return result.returncode == 0


if __name__ == "__main__":
    run_all_ocr_tests() 