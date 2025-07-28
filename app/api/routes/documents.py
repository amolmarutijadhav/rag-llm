import os
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException, Request, Depends
from app.domain.models import DocumentResponse, TextInputRequest, SecureClearRequest, StatsResponse
from app.domain.services.rag_service import RAGService
from app.core.config import Config
from app.api.middleware.security import security_middleware
from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)
router = APIRouter()
rag_service = RAGService()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document with enhanced logging"""
    correlation_id = get_correlation_id()
    
    logger.info("Document upload request received", extra={
        'extra_fields': {
            'event_type': 'api_document_upload_request_start',
            'filename': file.filename,
            'content_type': file.content_type,
            'file_size': file.size,
            'correlation_id': correlation_id
        }
    })
    
    try:
        # Validate file size
        if file.size and file.size > Config.MAX_FILE_SIZE:
            logger.warning("File size validation failed", extra={
                'extra_fields': {
                    'event_type': 'api_document_upload_validation_failure',
                    'filename': file.filename,
                    'file_size': file.size,
                    'max_file_size': Config.MAX_FILE_SIZE,
                    'error': 'File too large',
                    'correlation_id': correlation_id
                }
            })
            
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size is {Config.MAX_FILE_SIZE} bytes"
            )
        
        # Validate file format
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in Config.SUPPORTED_FORMATS:
            logger.warning("File format validation failed", extra={
                'extra_fields': {
                    'event_type': 'api_document_upload_validation_failure',
                    'filename': file.filename,
                    'file_extension': file_extension,
                    'supported_formats': Config.SUPPORTED_FORMATS,
                    'error': 'Unsupported file format',
                    'correlation_id': correlation_id
                }
            })
            
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {Config.SUPPORTED_FORMATS}"
            )
        
        logger.info("File validation passed", extra={
            'extra_fields': {
                'event_type': 'api_document_upload_validation_success',
                'filename': file.filename,
                'file_extension': file_extension,
                'file_size': file.size,
                'correlation_id': correlation_id
            }
        })
        
        # Save uploaded file temporarily
        logger.debug("Saving uploaded file to temporary location", extra={
            'extra_fields': {
                'event_type': 'api_document_upload_temp_save_start',
                'filename': file.filename,
                'correlation_id': correlation_id
            }
        })
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        logger.debug("File saved to temporary location", extra={
            'extra_fields': {
                'event_type': 'api_document_upload_temp_save_success',
                'filename': file.filename,
                'temp_file_path': temp_file_path,
                'correlation_id': correlation_id
            }
        })
        
        try:
            # Process the document using external APIs
            logger.info("Starting document processing", extra={
                'extra_fields': {
                    'event_type': 'api_document_upload_processing_start',
                    'filename': file.filename,
                    'temp_file_path': temp_file_path,
                    'correlation_id': correlation_id
                }
            })
            
            result = await rag_service.add_document(temp_file_path)
            
            logger.info("Document processing completed", extra={
                'extra_fields': {
                    'event_type': 'api_document_upload_processing_complete',
                    'filename': file.filename,
                    'processing_success': result.get('success', False),
                    'chunks_processed': result.get('chunks_processed', 0),
                    'correlation_id': correlation_id
                }
            })
            
            return DocumentResponse(**result)
            
        finally:
            # Clean up temporary file
            logger.debug("Cleaning up temporary file", extra={
                'extra_fields': {
                    'event_type': 'api_document_upload_cleanup',
                    'temp_file_path': temp_file_path,
                    'correlation_id': correlation_id
                }
            })
            
            try:
                os.unlink(temp_file_path)
                logger.debug("Temporary file cleaned up successfully", extra={
                    'extra_fields': {
                        'event_type': 'api_document_upload_cleanup_success',
                        'temp_file_path': temp_file_path,
                        'correlation_id': correlation_id
                    }
                })
            except Exception as cleanup_error:
                logger.warning("Failed to clean up temporary file", extra={
                    'extra_fields': {
                        'event_type': 'api_document_upload_cleanup_failure',
                        'temp_file_path': temp_file_path,
                        'error': str(cleanup_error),
                        'correlation_id': correlation_id
                    }
                })
            
    except HTTPException:
        logger.error("Document upload failed with HTTP exception", extra={
            'extra_fields': {
                'event_type': 'api_document_upload_http_error',
                'filename': file.filename,
                'correlation_id': correlation_id
            }
        })
        raise
    except Exception as e:
        logger.error("Document upload failed with unexpected error", extra={
            'extra_fields': {
                'event_type': 'api_document_upload_error',
                'filename': file.filename,
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add-text", response_model=DocumentResponse)
async def add_text(request: TextInputRequest):
    """Add raw text to the knowledge base with enhanced logging"""
    correlation_id = get_correlation_id()
    
    logger.info("Text addition request received", extra={
        'extra_fields': {
            'event_type': 'api_text_add_request_start',
            'source_name': request.source_name,
            'text_length': len(request.text),
            'correlation_id': correlation_id
        }
    })
    
    try:
        # Validate text input
        if not request.text or not request.text.strip():
            logger.warning("Text validation failed - empty text", extra={
                'extra_fields': {
                    'event_type': 'api_text_add_validation_failure',
                    'source_name': request.source_name,
                    'error': 'Text cannot be empty',
                    'correlation_id': correlation_id
                }
            })
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        logger.info("Text validation passed", extra={
            'extra_fields': {
                'event_type': 'api_text_add_validation_success',
                'source_name': request.source_name,
                'text_length': len(request.text),
                'correlation_id': correlation_id
            }
        })
        
        # Process the text
        logger.info("Starting text processing", extra={
            'extra_fields': {
                'event_type': 'api_text_add_processing_start',
                'source_name': request.source_name,
                'text_length': len(request.text),
                'correlation_id': correlation_id
            }
        })
        
        result = await rag_service.add_text(request.text, request.source_name)
        
        logger.info("Text processing completed", extra={
            'extra_fields': {
                'event_type': 'api_text_add_processing_complete',
                'source_name': request.source_name,
                'processing_success': result.get('success', False),
                'chunks_processed': result.get('chunks_processed', 0),
                'correlation_id': correlation_id
            }
        })
        
        return DocumentResponse(**result)
        
    except HTTPException:
        logger.error("Text addition failed with HTTP exception", extra={
            'extra_fields': {
                'event_type': 'api_text_add_http_error',
                'source_name': request.source_name,
                'correlation_id': correlation_id
            }
        })
        raise
    except Exception as e:
        logger.error("Text addition failed with unexpected error", extra={
            'extra_fields': {
                'event_type': 'api_text_add_error',
                'source_name': request.source_name,
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear", response_model=DocumentResponse)
async def clear_knowledge_base():
    """Clear all documents from the knowledge base (DEPRECATED - Use /clear-secure instead) with enhanced logging"""
    correlation_id = get_correlation_id()
    
    logger.warning("Deprecated clear endpoint accessed", extra={
        'extra_fields': {
            'event_type': 'api_document_clear_deprecated_access',
            'endpoint': '/clear',
            'recommended_endpoint': '/clear-secure',
            'correlation_id': correlation_id
        }
    })
    
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
    Clear all documents from the knowledge base with security measures and enhanced logging.
    
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
    correlation_id = get_correlation_id()
    
    logger.warning("Secure clear request received", extra={
        'extra_fields': {
            'event_type': 'api_document_clear_secure_request_start',
            'confirmation_token_provided': bool(clear_request.confirmation_token),
            'reason_provided': bool(clear_request.reason),
            'api_key_verified': api_key_verified,
            'correlation_id': correlation_id
        }
    })
    
    try:
        # Get client information for audit logging
        client_info = security_middleware.get_client_info(request)
        
        logger.info("Client information retrieved for audit", extra={
            'extra_fields': {
                'event_type': 'api_document_clear_secure_client_info',
                'client_ip': client_info.get('client_ip', 'unknown'),
                'user_agent': client_info.get('user_agent', 'unknown'),
                'correlation_id': correlation_id
            }
        })
        
        # Verify confirmation token
        logger.debug("Verifying confirmation token", extra={
            'extra_fields': {
                'event_type': 'api_document_clear_secure_token_verification_start',
                'correlation_id': correlation_id
            }
        })
        
        security_middleware.verify_confirmation_token(clear_request.confirmation_token)
        
        logger.info("Confirmation token verified successfully", extra={
            'extra_fields': {
                'event_type': 'api_document_clear_secure_token_verification_success',
                'correlation_id': correlation_id
            }
        })
        
        # Check rate limiting
        logger.debug("Checking rate limiting", extra={
            'extra_fields': {
                'event_type': 'api_document_clear_secure_rate_limit_check_start',
                'client_ip': client_info.get('client_ip', 'unknown'),
                'correlation_id': correlation_id
            }
        })
        
        security_middleware.check_rate_limit(client_info["client_ip"])
        
        logger.info("Rate limit check passed", extra={
            'extra_fields': {
                'event_type': 'api_document_clear_secure_rate_limit_check_success',
                'client_ip': client_info.get('client_ip', 'unknown'),
                'correlation_id': correlation_id
            }
        })
        
        # Log the attempt
        logger.warning("Security checks passed, proceeding with knowledge base clear", extra={
            'extra_fields': {
                'event_type': 'api_document_clear_secure_security_passed',
                'client_ip': client_info.get('client_ip', 'unknown'),
                'reason': clear_request.reason,
                'correlation_id': correlation_id
            }
        })
        
        # Perform the clear operation
        logger.warning("Executing knowledge base clear operation", extra={
            'extra_fields': {
                'event_type': 'api_document_clear_secure_execution_start',
                'client_ip': client_info.get('client_ip', 'unknown'),
                'reason': clear_request.reason,
                'correlation_id': correlation_id
            }
        })
        
        result = rag_service.clear_knowledge_base()
        
        logger.warning("Knowledge base clear operation completed", extra={
            'extra_fields': {
                'event_type': 'api_document_clear_secure_execution_complete',
                'client_ip': client_info.get('client_ip', 'unknown'),
                'reason': clear_request.reason,
                'operation_success': result.get('success', False),
                'documents_cleared': result.get('documents_cleared', 0),
                'correlation_id': correlation_id
            }
        })
        
        return DocumentResponse(**result)
        
    except HTTPException:
        logger.error("Secure clear failed with HTTP exception", extra={
            'extra_fields': {
                'event_type': 'api_document_clear_secure_http_error',
                'client_ip': client_info.get('client_ip', 'unknown') if 'client_info' in locals() else 'unknown',
                'correlation_id': correlation_id
            }
        })
        raise
    except Exception as e:
        logger.error("Secure clear failed with unexpected error", extra={
            'extra_fields': {
                'event_type': 'api_document_clear_secure_error',
                'client_ip': client_info.get('client_ip', 'unknown') if 'client_info' in locals() else 'unknown',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get collection statistics with enhanced logging"""
    correlation_id = get_correlation_id()
    
    logger.info("Statistics request received", extra={
        'extra_fields': {
            'event_type': 'api_document_stats_request_start',
            'correlation_id': correlation_id
        }
    })
    
    try:
        logger.debug("Retrieving collection statistics", extra={
            'extra_fields': {
                'event_type': 'api_document_stats_retrieval_start',
                'correlation_id': correlation_id
            }
        })
        
        stats = rag_service.get_stats()
        
        logger.info("Statistics retrieved successfully", extra={
            'extra_fields': {
                'event_type': 'api_document_stats_retrieval_success',
                'retrieval_success': stats.get('success', False),
                'total_documents': stats.get('vector_store', {}).get('total_documents', 0),
                'correlation_id': correlation_id
            }
        })
        
        return StatsResponse(**stats)
        
    except Exception as e:
        logger.error("Statistics retrieval failed", extra={
            'extra_fields': {
                'event_type': 'api_document_stats_retrieval_error',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e)) 