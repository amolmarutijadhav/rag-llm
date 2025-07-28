from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QuestionResponse(BaseModel):
    """Response model for question answers"""
    success: bool
    answer: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    context_used: Optional[str] = None

class DocumentResponse(BaseModel):
    """Response model for document operations"""
    success: bool
    message: str
    chunks_processed: Optional[int] = None
    extracted_text: Optional[str] = None

class StatsResponse(BaseModel):
    """Response model for system statistics"""
    success: bool
    vector_store: Dict[str, Any]
    supported_formats: List[str]
    chunk_size: int
    chunk_overlap: int

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    timestamp: str

class ChatCompletionResponse(BaseModel):
    """Response model for chat completions"""
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, Any]] = None
    sources: Optional[List[Dict[str, Any]]] = None 