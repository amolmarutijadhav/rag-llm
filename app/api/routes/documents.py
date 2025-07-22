import os
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.domain.models import DocumentResponse, TextInputRequest
from app.domain.services.rag_service import RAGService
from app.core.config import Config

router = APIRouter()
rag_service = RAGService()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file size
        if file.size and file.size > Config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size is {Config.MAX_FILE_SIZE} bytes"
            )
        
        # Validate file format
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in Config.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {Config.SUPPORTED_FORMATS}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process the document using external APIs
            result = await rag_service.add_document(temp_file_path)
            return DocumentResponse(**result)
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-text", response_model=DocumentResponse)
async def add_text(request: TextInputRequest):
    """Add raw text to the knowledge base"""
    try:
        result = await rag_service.add_text(request.text, request.source_name)
        return DocumentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear", response_model=DocumentResponse)
async def clear_knowledge_base():
    """Clear all documents from the knowledge base"""
    try:
        result = rag_service.clear_knowledge_base()
        return DocumentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 