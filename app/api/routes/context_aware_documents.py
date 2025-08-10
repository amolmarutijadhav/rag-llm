"""
Context-Aware Document Upload Routes
Provides endpoints for uploading documents and text with mandatory context.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from app.domain.services.context_aware_rag_service import ContextAwareRAGService
from app.domain.models.requests import (
    DocumentUploadRequest, TextUploadRequest, DocumentContext,
    ResponseMode
)
from app.infrastructure.providers import get_embedding_provider, get_llm_provider, get_vector_store_provider
from app.core.logging_config import get_logger, get_correlation_id
import tempfile
import os

logger = get_logger(__name__)
router = APIRouter(prefix="/context-aware-documents", tags=["Context-Aware Documents"])

# Initialize context-aware RAG service with proper providers
from app.infrastructure.providers import get_embedding_provider, get_vector_store_provider, get_llm_provider

# Get providers
embedding_provider = get_embedding_provider()
vector_store_provider = get_vector_store_provider()
llm_provider = get_llm_provider()

# Initialize context-aware RAG service with providers
context_aware_rag_service = ContextAwareRAGService(
    embedding_provider=embedding_provider,
    llm_provider=llm_provider,
    vector_store_provider=vector_store_provider
)

class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    documents_added: Optional[int] = None
    context: Optional[Dict[str, Any]] = None

class ContextOptionsResponse(BaseModel):
    context_types: List[str]
    document_categories: List[str]
    example_domains: List[str]

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document_with_context(
    file: UploadFile = File(...),
    context_type: str = Form(...),
    content_domain: str = Form(...),
    document_category: str = Form(...),
    relevance_tags: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Upload document with mandatory context"""
    correlation_id = get_correlation_id()
    
    logger.info("Document upload with context request received", extra={
        'extra_fields': {
            'event_type': 'context_aware_document_upload_request',
            'filename': file.filename,
            'file_size': file.size,
            'context_type': context_type,
            'content_domain': content_domain,
            'document_category': document_category,
            'correlation_id': correlation_id
        }
    })
    
    try:
        # Validate context type
        valid_context_types = [
            "technical", "creative", "general", "api_docs", "user_guides", 
            "reference", "tutorial", "faq", "policies", "marketing", 
            "support", "legal", "academic"
        ]
        if context_type.lower() not in valid_context_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid context_type. Must be one of: {valid_context_types}"
            )
        
        # Validate document category
        valid_categories = [
            "user_guide", "reference", "tutorial", "faq", "api_reference",
            "getting_started", "troubleshooting", "examples", "best_practices",
            "release_notes", "configuration", "deployment", "security"
        ]
        if document_category.lower() not in valid_categories:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document_category. Must be one of: {valid_categories}"
            )
        
        # Parse relevance tags
        tags = []
        if relevance_tags:
            tags = [tag.strip() for tag in relevance_tags.split(',') if tag.strip()]
        
        # Create document context
        context = DocumentContext(
            context_type=[context_type.lower()],
            content_domain=[content_domain.lower()],
            document_category=[document_category.lower()],
            relevance_tags=tags,
            description=description
        )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Create upload request
            upload_request = DocumentUploadRequest(
                file_path=temp_file_path,
                context=context
            )
            
            # Process document
            result = await context_aware_rag_service.add_document_with_context(upload_request)
            
            if result.get('success', False):
                logger.info("Document upload with context completed successfully", extra={
                    'extra_fields': {
                        'event_type': 'context_aware_document_upload_success',
                        'filename': file.filename,
                        'context_type': context_type,
                        'documents_added': result.get('documents_added', 0),
                        'correlation_id': correlation_id
                    }
                })
                return DocumentUploadResponse(**result)
            else:
                logger.error("Document upload with context failed", extra={
                    'extra_fields': {
                        'event_type': 'context_aware_document_upload_failure',
                        'filename': file.filename,
                        'error': result.get('message', 'Unknown error'),
                        'correlation_id': correlation_id
                    }
                })
                # Return HTTP 500 for failures instead of 200
                raise HTTPException(
                    status_code=500, 
                    detail=result.get('message', 'Document upload failed')
                )
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in document upload with context", extra={
            'extra_fields': {
                'event_type': 'context_aware_document_upload_error',
                'filename': file.filename if file else 'unknown',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-text", response_model=DocumentUploadResponse)
async def upload_text_with_context(
    text: str = Form(...),
    context_type: str = Form(...),
    content_domain: str = Form(...),
    document_category: str = Form(...),
    source_name: Optional[str] = Form(None),
    relevance_tags: Optional[str] = Form(None),
    description: Optional[str] = Form(None)
):
    """Upload text with mandatory context"""
    correlation_id = get_correlation_id()
    
    logger.info("Text upload with context request received", extra={
        'extra_fields': {
            'event_type': 'context_aware_text_upload_request',
            'text_length': len(text),
            'context_type': context_type,
            'content_domain': content_domain,
            'document_category': document_category,
            'correlation_id': correlation_id
        }
    })
    
    try:
        # Validate context type
        valid_context_types = [
            "technical", "creative", "general", "api_docs", "user_guides", 
            "reference", "tutorial", "faq", "policies", "marketing", 
            "support", "legal", "academic"
        ]
        if context_type.lower() not in valid_context_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid context_type. Must be one of: {valid_context_types}"
            )
        
        # Validate document category
        valid_categories = [
            "user_guide", "reference", "tutorial", "faq", "api_reference",
            "getting_started", "troubleshooting", "examples", "best_practices",
            "release_notes", "configuration", "deployment", "security"
        ]
        if document_category.lower() not in valid_categories:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document_category. Must be one of: {valid_categories}"
            )
        
        # Parse relevance tags
        tags = []
        if relevance_tags:
            tags = [tag.strip() for tag in relevance_tags.split(',') if tag.strip()]
        
        # Create document context
        context = DocumentContext(
            context_type=[context_type.lower()],
            content_domain=[content_domain.lower()],
            document_category=[document_category.lower()],
            relevance_tags=tags,
            description=description
        )
        
        # Create upload request
        upload_request = TextUploadRequest(
            text=text,
            context=context,
            source_name=source_name
        )
        
        # Process text
        result = await context_aware_rag_service.add_text_with_context(upload_request)
        
        if result.get('success', False):
            logger.info("Text upload with context completed successfully", extra={
                'extra_fields': {
                    'event_type': 'context_aware_text_upload_success',
                    'text_length': len(text),
                    'context_type': context_type,
                    'documents_added': result.get('documents_added', 0),
                    'correlation_id': correlation_id
                }
            })
            return DocumentUploadResponse(**result)
        else:
            logger.error("Text upload with context failed", extra={
                'extra_fields': {
                    'event_type': 'context_aware_text_upload_failure',
                    'text_length': len(text),
                    'error': result.get('message', 'Unknown error'),
                    'correlation_id': correlation_id
                }
            })
            # Return HTTP 500 for failures instead of 200
            raise HTTPException(
                status_code=500, 
                detail=result.get('message', 'Text upload failed')
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Unexpected error in text upload with context", extra={
            'extra_fields': {
                'event_type': 'context_aware_text_upload_error',
                'text_length': len(text),
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/context-options", response_model=ContextOptionsResponse)
async def get_context_options():
    """Get available context options for document upload"""
    return ContextOptionsResponse(
        context_types=[
            "technical", "creative", "general", "api_docs", "user_guides", 
            "reference", "tutorial", "faq", "policies", "marketing", 
            "support", "legal", "academic"
        ],
        document_categories=[
            "user_guide", "reference", "tutorial", "faq", "api_reference",
            "getting_started", "troubleshooting", "examples", "best_practices",
            "release_notes", "configuration", "deployment", "security"
        ],
        example_domains=[
            "api_documentation",
            "user_support", 
            "marketing",
            "technical_reference",
            "tutorials",
            "policies",
            "release_notes",
            "best_practices"
        ]
    )

@router.get("/stats")
async def get_context_aware_stats():
    """Get statistics for context-aware documents"""
    return await context_aware_rag_service.get_stats()

@router.delete("/clear")
async def clear_context_aware_knowledge_base():
    """Clear all context-aware documents"""
    return context_aware_rag_service.clear_knowledge_base()

@router.get("/health")
async def check_provider_health():
    """Check if all providers are working correctly"""
    correlation_id = get_correlation_id()
    
    try:
        logger.info("Checking provider health", extra={
            'extra_fields': {
                'event_type': 'provider_health_check_start',
                'correlation_id': correlation_id
            }
        })
        
        # Test embedding provider
        test_embeddings = await context_aware_rag_service.rag_service.vector_store.embedding_provider.get_embeddings(["test"])
        
        # Test vector store provider
        test_stats = context_aware_rag_service.rag_service.vector_store.get_collection_stats()
        
        logger.info("Provider health check completed successfully", extra={
            'extra_fields': {
                'event_type': 'provider_health_check_success',
                'embedding_provider': type(context_aware_rag_service.rag_service.vector_store.embedding_provider).__name__,
                'vector_store_provider': type(context_aware_rag_service.rag_service.vector_store.vector_store_provider).__name__,
                'correlation_id': correlation_id
            }
        })
        
        return {
            "status": "healthy",
            "embedding_provider": "working",
            "vector_store_provider": "working",
            "collection_stats": test_stats,
            "embedding_dimensions": len(test_embeddings[0]) if test_embeddings else 0
        }
    except Exception as e:
        logger.error("Provider health check failed", extra={
            'extra_fields': {
                'event_type': 'provider_health_check_failure',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        
        return {
            "status": "unhealthy",
            "error": str(e),
            "error_type": type(e).__name__,
            "embedding_provider": type(context_aware_rag_service.rag_service.vector_store.embedding_provider).__name__,
            "vector_store_provider": type(context_aware_rag_service.rag_service.vector_store.vector_store_provider).__name__
        } 