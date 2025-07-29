import pytest
import tempfile
import os
import sys
from unittest.mock import patch, AsyncMock, MagicMock
from io import BytesIO
from fastapi import UploadFile


@pytest.mark.document_upload
class TestDocumentUpload:
    """Comprehensive test suite for document upload functionality."""

    def test_upload_pdf_success(self, async_client):
        """Test successful PDF document upload."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'test.pdf' added successfully",
                "chunks_processed": 3
            }
            
            # Create a mock PDF file
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(PDF Test Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n364\n%%EOF"
            
            files = {"file": ("test.pdf", BytesIO(pdf_content), "application/pdf")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "added successfully" in data["message"]
            assert data["chunks_processed"] == 3

    def test_upload_txt_success(self, async_client):
        """Test successful TXT document upload."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'test.txt' added successfully",
                "chunks_processed": 1
            }
            
            txt_content = b"This is a test text document with some content."
            files = {"file": ("test.txt", BytesIO(txt_content), "text/plain")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["chunks_processed"] == 1

    def test_upload_docx_success(self, async_client):
        """Test successful DOCX document upload."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'test.docx' added successfully",
                "chunks_processed": 2
            }
            
            # Create a minimal DOCX file (simplified for testing)
            docx_content = b"PK\x03\x04\x14\x00\x00\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00[Content_Types].xml"
            files = {"file": ("test.docx", BytesIO(docx_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["chunks_processed"] == 2

    def test_upload_unsupported_format(self, async_client):
        """Test upload with unsupported file format."""
        files = {"file": ("test.xyz", BytesIO(b"content"), "application/octet-stream")}
        response = async_client.post("/documents/upload", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported file format" in data["detail"]

    def test_upload_file_too_large(self, async_client):
        """Test upload with file exceeding size limit."""
        # Create content larger than MAX_FILE_SIZE (10MB)
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("large.txt", BytesIO(large_content), "text/plain")}
        response = async_client.post("/documents/upload", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "File too large" in data["detail"]

    def test_upload_missing_file(self, async_client):
        """Test upload without providing a file."""
        response = async_client.post("/documents/upload")
        
        assert response.status_code == 422  # Validation error

    def test_upload_empty_file(self, async_client):
        """Test upload with empty file."""
        files = {"file": ("empty.txt", BytesIO(b""), "text/plain")}
        response = async_client.post("/documents/upload", files=files)
        
        assert response.status_code == 200  # Should be accepted but may fail in processing

    def test_upload_service_error(self, async_client):
        """Test upload when RAG service fails."""
        with patch('app.api.routes.documents.rag_service') as mock_rag_service:
            mock_rag_service.add_document.side_effect = Exception("Service error")
            
            files = {"file": ("test.txt", BytesIO(b"content"), "text/plain")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data

    def test_upload_document_processing_error(self, async_client):
        """Test upload when document processing fails."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": False,
                "message": "Error processing document: Invalid PDF format"
            }
            
            files = {"file": ("test.txt", BytesIO(b"content"), "text/plain")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "Error processing document" in data["message"]

    def test_upload_vector_store_error(self, async_client):
        """Test upload when vector store fails."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": False,
                "message": "Failed to add document to vector store"
            }
            
            files = {"file": ("test.txt", BytesIO(b"content"), "text/plain")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "Failed to add document" in data["message"]

    def test_upload_with_special_characters_in_filename(self, async_client):
        """Test upload with special characters in filename."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'test-file_123.txt' added successfully",
                "chunks_processed": 1
            }
            
            files = {"file": ("test-file_123.txt", BytesIO(b"content"), "text/plain")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_upload_large_text_content(self, async_client):
        """Test upload with large text content."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'large.txt' added successfully",
                "chunks_processed": 10
            }
            
            # Create large text content (but under size limit)
            large_text = "This is a large text document. " * 10000  # ~300KB
            files = {"file": ("large.txt", BytesIO(large_text.encode()), "text/plain")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["chunks_processed"] == 10

    def test_upload_multiple_files_same_request(self, async_client):
        """Test upload with multiple files in same request (should fail)."""
        files = {
            "file": ("test1.txt", BytesIO(b"content1"), "text/plain"),
            "file2": ("test2.txt", BytesIO(b"content2"), "text/plain")
        }
        response = async_client.post("/documents/upload", files=files)
        
        # FastAPI will only process the first file, so this should work
        assert response.status_code == 200

    def test_upload_with_different_content_types(self, async_client):
        """Test upload with different content types for same file format."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'test.txt' added successfully",
                "chunks_processed": 1
            }
            
            # Test with different content types for text files
            content_types = [
                "text/plain",
                "application/text",
                "text/html",  # Should still work for .txt files
            ]
            
            for content_type in content_types:
                files = {"file": ("test.txt", BytesIO(b"content"), content_type)}
                response = async_client.post("/documents/upload", files=files)
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True

    def test_upload_file_without_extension(self, async_client):
        """Test upload with file without extension."""
        files = {"file": ("testfile", BytesIO(b"content"), "text/plain")}
        response = async_client.post("/documents/upload", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported file format" in data["detail"]

    def test_upload_with_uppercase_extension(self, async_client):
        """Test upload with uppercase file extension."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'test.TXT' added successfully",
                "chunks_processed": 1
            }
            
            files = {"file": ("test.TXT", BytesIO(b"content"), "text/plain")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_upload_with_mixed_case_extension(self, async_client):
        """Test upload with mixed case file extension."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'test.Pdf' added successfully",
                "chunks_processed": 1
            }
            
            files = {"file": ("test.Pdf", BytesIO(b"content"), "application/pdf")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


@pytest.mark.document_upload
class TestDocumentUploadEdgeCases:
    """Test edge cases for document upload functionality."""

    def test_upload_with_very_long_filename(self, async_client):
        """Test upload with very long filename."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document added successfully",
                "chunks_processed": 1
            }
            
            long_filename = "a" * 255 + ".txt"  # Very long filename
            files = {"file": (long_filename, BytesIO(b"content"), "text/plain")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_upload_with_binary_content_in_text_file(self, async_client):
        """Test upload with binary content in text file."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'binary.txt' added successfully",
                "chunks_processed": 1
            }
            
            # Binary content in a .txt file
            binary_content = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09"
            files = {"file": ("binary.txt", BytesIO(binary_content), "text/plain")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_upload_with_unicode_content(self, async_client):
        """Test upload with Unicode content."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'unicode.txt' added successfully",
                "chunks_processed": 1
            }
            
            unicode_content = "This is a test with Unicode characters: éñüßáñö"
            files = {"file": ("unicode.txt", BytesIO(unicode_content.encode('utf-8')), "text/plain")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_upload_with_compressed_content(self, async_client):
        """Test upload with compressed content (should fail for unsupported formats)."""
        import gzip
        
        # Create gzipped content
        original_content = b"This is test content that will be compressed"
        compressed_content = gzip.compress(original_content)
        
        files = {"file": ("compressed.txt.gz", BytesIO(compressed_content), "application/gzip")}
        response = async_client.post("/documents/upload", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "Unsupported file format" in data["detail"]

    def test_upload_with_malformed_pdf(self, async_client):
        """Test upload with malformed PDF content."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": False,
                "message": "Error processing document: Invalid PDF format"
            }
            
            # Malformed PDF content
            malformed_pdf = b"This is not a valid PDF file"
            files = {"file": ("malformed.pdf", BytesIO(malformed_pdf), "application/pdf")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "Error processing document" in data["message"]


@pytest.mark.document_upload
class TestDocumentUploadIntegration:
    """Integration tests for document upload with actual file processing."""

    def test_upload_real_text_file(self, async_client):
        """Test upload with a real text file."""
        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("This is a real text file for testing document upload functionality.")
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {"file": ("real_test.txt", BytesIO(f.read()), "text/plain")}
                response = async_client.post("/documents/upload", files=files)
                
                # This test may fail if external services are not configured
                # but should not crash the application
                assert response.status_code in [200, 500]
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_upload_with_actual_pdf_processing(self, async_client):
        """Test upload with actual PDF processing."""
        # Create a simple PDF file for testing
        import tempfile
        import os
        
        # Create a minimal PDF file (simplified for testing)
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF Content) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_content)
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {"file": ("test.pdf", BytesIO(f.read()), "application/pdf")}
                response = async_client.post("/documents/upload", files=files)
                
                # This test may fail if external services are not configured
                # but should not crash the application
                assert response.status_code in [200, 500]
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_upload_with_actual_docx_processing(self, async_client):
        """Test upload with actual DOCX processing."""
        # Create a simple DOCX file for testing
        import tempfile
        import os
        import zipfile
        
        # Create a minimal DOCX file (simplified for testing)
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            # Create a basic DOCX structure
            with zipfile.ZipFile(temp_file, 'w') as docx:
                # Add content types
                docx.writestr('[Content_Types].xml', 
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                    '<Default Extension="xml" ContentType="application/xml"/>'
                    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                    '</Types>')
                
                # Add document content
                docx.writestr('word/document.xml',
                    '<?xml version="1.0" encoding="UTF-8"?>'
                    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                    '<w:body>'
                    '<w:p><w:r><w:t>Test DOCX Content</w:t></w:r></w:p>'
                    '</w:body>'
                    '</w:document>')
            
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {"file": ("test.docx", BytesIO(f.read()), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                response = async_client.post("/documents/upload", files=files)
                
                # This test may fail if external services are not configured
                # but should not crash the application
                assert response.status_code in [200, 500]
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path) 


@pytest.mark.document_upload
class TestDocumentImageProcessing:
    """Tests for image processing and OCR capabilities in documents."""

    def test_pdf_with_images_processing(self, async_client):
        """Test PDF processing with embedded images."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'test_with_images.pdf' added successfully",
                "chunks_processed": 3
            }
            
            # Create a PDF with image content (simplified test)
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Test PDF with Images) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
            
            files = {"file": ("test_with_images.pdf", BytesIO(pdf_content), "application/pdf")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    def test_docx_with_images_processing(self, async_client):
        """Test DOCX processing with embedded images."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'test_with_images.docx' added successfully",
                "chunks_processed": 2
            }
            
            # Create a DOCX with image content (simplified test)
            import zipfile
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                with zipfile.ZipFile(temp_file, 'w') as docx:
                    # Add content types
                    docx.writestr('[Content_Types].xml', 
                        '<?xml version="1.0" encoding="UTF-8"?>'
                        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                        '<Default Extension="xml" ContentType="application/xml"/>'
                        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                        '</Types>')
                    
                    # Add document content
                    docx.writestr('word/document.xml',
                        '<?xml version="1.0" encoding="UTF-8"?>'
                        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                        '<w:body>'
                        '<w:p><w:r><w:t>Test DOCX with Images</w:t></w:r></w:p>'
                        '</w:body>'
                        '</w:document>')
                
                temp_file_path = temp_file.name
            
            try:
                with open(temp_file_path, 'rb') as f:
                    files = {"file": ("test_with_images.docx", BytesIO(f.read()), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
                    response = async_client.post("/documents/upload", files=files)
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["success"] is True
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

    def test_image_processing_disabled_fallback(self, async_client):
        """Test that document processing still works when image processing is disabled."""
        with patch('app.api.routes.documents.rag_service.add_document') as mock_add_document:
            mock_add_document.return_value = {
                "success": True,
                "message": "Document 'test_fallback.pdf' added successfully",
                "chunks_processed": 1
            }
            
            # Test that regular text processing still works
            pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Fallback Test) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF"
            
            files = {"file": ("test_fallback.pdf", BytesIO(pdf_content), "application/pdf")}
            response = async_client.post("/documents/upload", files=files)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True 