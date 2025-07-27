from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.routes import health, documents, questions, chat
from app.core.config import Config
from app.core.logging_config import logging_config, get_logger, generate_correlation_id, set_correlation_id, set_request_start_time
from app.api.middleware.request_logging import enhanced_request_logging

# Setup logging first
logging_config.setup_logging()
logger = get_logger(__name__)

# Initialize FastAPI app with configurable settings
app = FastAPI(
    title=Config.API_TITLE,
    description=Config.API_DESCRIPTION,
    version=Config.API_VERSION
)

# Add CORS middleware with configurable settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.CORS_ALLOW_ORIGINS,
    allow_credentials=Config.CORS_ALLOW_CREDENTIALS,
    allow_methods=Config.CORS_ALLOW_METHODS,
    allow_headers=Config.CORS_ALLOW_HEADERS,
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(questions.router, prefix="/questions", tags=["questions"])
app.include_router(chat.router, tags=["chat"])

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to all requests for tracing"""
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    set_request_start_time()
    
    # Add correlation ID to request state
    request.state.correlation_id = correlation_id
    
    logger.info(f"Request started: {request.method} {request.url.path}", extra={
        'extra_fields': {
            'event_type': 'request_start',
            'method': request.method,
            'path': request.url.path,
            'client_ip': request.client.host if request.client else "unknown",
            'correlation_id': correlation_id
        }
    })
    
    response = await call_next(request)
    
    # Add correlation ID to response headers
    response.headers["X-Correlation-ID"] = correlation_id
    
    logger.info(f"Request completed: {request.method} {request.url.path} - {response.status_code}", extra={
        'extra_fields': {
            'event_type': 'request_complete',
            'method': request.method,
            'path': request.url.path,
            'status_code': response.status_code,
            'correlation_id': correlation_id
        }
    })
    
    return response

@app.middleware("http")
async def enhanced_http_logging(request: Request, call_next):
    """Enhanced HTTP request/response logging with detailed information"""
    return await enhanced_request_logging(request, call_next)

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up", extra={
        'extra_fields': {
            'event_type': 'application_startup',
            'environment': os.getenv("ENVIRONMENT", "development"),
            'log_level': logging_config.log_level
        }
    })

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down", extra={
        'extra_fields': {
            'event_type': 'application_shutdown'
        }
    }) 