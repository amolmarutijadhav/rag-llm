from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str = Field(..., description="The question to ask")
    top_k: Optional[int] = Field(3, description="Number of relevant documents to retrieve")

class TextInputRequest(BaseModel):
    """Request model for adding text to knowledge base"""
    text: str = Field(..., description="Text content to add")
    source_name: Optional[str] = Field("text_input", description="Name for the text source")

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