import os
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException, Request, Depends
from app.domain.models import DocumentResponse, TextInputRequest, SecureClearRequest
from app.domain.services.rag_service import RAGService
from app.core.config import Config
from app.api.middleware.security import security_middleware

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
    """Clear all documents from the knowledge base (DEPRECATED - Use /clear-secure instead)"""
    raise HTTPException(
        status_code=410, 
        detail="This endpoint is deprecated. Use /clear-secure with proper authentication and confirmation."
    )

@router.delete("/clear-secure", response_model=DocumentResponse)
async def clear_knowledge_base_secure(
    request: Request,
    clear_request: SecureClearRequest,
    api_key_verified: bool = Depends(security_middleware.verify_api_key)
):
    """
    Clear all documents from the knowledge base with security measures.
    
    This endpoint requires:
    1. Valid API key in Authorization header
    2. Confirmation token in request body
    3. Rate limiting (max 5 calls per hour)
    4. Audit logging enabled
    
    Example:
    ```bash
    curl -X DELETE "http://localhost:8000/documents/clear-secure" \
         -H "Authorization: Bearer your-api-key" \
         -H "Content-Type: application/json" \
         -d '{"confirmation_token": "CONFIRM_DELETE_ALL_DATA", "reason": "Data cleanup"}'
    ```
    """
    try:
        # Get client information for audit logging
        client_info = security_middleware.get_client_info(request)
        
        # Verify confirmation token
        security_middleware.verify_confirmation_token(clear_request.confirmation_token)
        
        # Check rate limiting
        security_middleware.check_rate_limit(client_info["client_ip"])
        
        # Log the attempt
        security_middleware.log_audit_event(
            operation="clear_knowledge_base_attempt",
            client_ip=client_info["client_ip"],
            user_agent=client_info["user_agent"],
            success=True,
            details=f"Reason: {clear_request.reason or 'Not specified'}"
        )
        
        # Perform the clear operation
        result = rag_service.clear_knowledge_base()
        
        # Log the result
        security_middleware.log_audit_event(
            operation="clear_knowledge_base_result",
            client_ip=client_info["client_ip"],
            user_agent=client_info["user_agent"],
            success=result["success"],
            details=f"Result: {result.get('message', 'Unknown')}"
        )
        
        return DocumentResponse(**result)
        
    except HTTPException:
        # Log failed attempts
        client_info = security_middleware.get_client_info(request)
        security_middleware.log_audit_event(
            operation="clear_knowledge_base_failed",
            client_ip=client_info["client_ip"],
            user_agent=client_info["user_agent"],
            success=False,
            details=f"Reason: {clear_request.reason or 'Not specified'}"
        )
        raise
    except Exception as e:
        # Log unexpected errors
        client_info = security_middleware.get_client_info(request)
        security_middleware.log_audit_event(
            operation="clear_knowledge_base_error",
            client_ip=client_info["client_ip"],
            user_agent=client_info["user_agent"],
            success=False,
            details=f"Error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e)) 