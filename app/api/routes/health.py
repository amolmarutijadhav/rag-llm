from fastapi import APIRouter
from app.core.config import Config
from app.core.logging_config import get_logger, get_correlation_id

logger = get_logger(__name__)
router = APIRouter()

@router.get("/")
async def root():
    """Root endpoint with API information and enhanced logging"""
    correlation_id = get_correlation_id()
    
    logger.info("Root endpoint accessed", extra={
        'extra_fields': {
            'event_type': 'api_root_endpoint_access',
            'correlation_id': correlation_id
        }
    })
    
    return {
        "message": "RAG LLM API",
        "version": Config.API_VERSION,
        "description": Config.API_DESCRIPTION,
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "documents": "/documents",
            "questions": "/questions",
            "chat": "/chat/completions",
            "docs": "/docs"
        }
    }

@router.get("/health")
async def health_check():
    """Health check endpoint with enhanced logging"""
    correlation_id = get_correlation_id()
    
    logger.info("Health check request received", extra={
        'extra_fields': {
            'event_type': 'api_health_check_request_start',
            'correlation_id': correlation_id
        }
    })
    
    try:
        # Basic health check - could be extended with database connectivity, etc.
        health_status = {
            "status": "healthy",
            "version": Config.API_VERSION,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
            "services": {
                "api": "healthy",
                "logging": "healthy"
            }
        }
        
        logger.info("Health check completed successfully", extra={
            'extra_fields': {
                'event_type': 'api_health_check_success',
                'status': health_status['status'],
                'version': health_status['version'],
                'correlation_id': correlation_id
            }
        })
        
        return health_status
        
    except Exception as e:
        logger.error("Health check failed", extra={
            'extra_fields': {
                'event_type': 'api_health_check_failure',
                'error': str(e),
                'error_type': type(e).__name__,
                'correlation_id': correlation_id
            }
        })
        
        return {
            "status": "unhealthy",
            "version": Config.API_VERSION,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
            "error": str(e)
        } 