from pydantic import BaseModel, validator
from typing import Optional, List
from enum import Enum

class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = None
    
    @validator('question')
    def question_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()
    
    @validator('top_k')
    def top_k_must_be_valid(cls, v):
        if v is not None and v <= 0:
            raise ValueError('top_k must be greater than 0')
        return v

class TextInputRequest(BaseModel):
    text: str
    source_name: Optional[str] = None
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()

class SecureClearRequest(BaseModel):
    """Request model for secure clear endpoint"""
    confirmation_token: str
    reason: Optional[str] = None
    
    @validator('confirmation_token')
    def confirmation_token_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Confirmation token cannot be empty')
        return v.strip()

class ChatMessage(BaseModel):
    """Model for chat messages"""
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    """Request model for chat completions"""
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

# Context-Aware RAG Models

class ResponseMode(str, Enum):
    """Response modes for context-aware RAG"""
    RAG_ONLY = "RAG_ONLY"           # Only RAG, refuse if no docs
    LLM_ONLY = "LLM_ONLY"           # Only LLM knowledge
    HYBRID = "HYBRID"               # RAG first, LLM fallback
    SMART_FALLBACK = "SMART_FALLBACK"  # Confidence-based decision
    RAG_PRIORITY = "RAG_PRIORITY"   # Prefer RAG, LLM for gaps
    LLM_PRIORITY = "LLM_PRIORITY"   # Prefer LLM, RAG for specific topics

class DocumentContext(BaseModel):
    """Mandatory document context for upload (Option 2B: Multiple Values)"""
    context_type: List[str]  # MANDATORY: ["technical", "api_docs"]
    content_domain: List[str]  # MANDATORY: ["api_documentation", "user_support"]
    document_category: List[str]  # MANDATORY: ["user_guide", "reference"]
    relevance_tags: List[str] = []  # OPTIONAL: ["authentication", "endpoints"]
    description: Optional[str] = None  # OPTIONAL: Brief description
    
    @validator('context_type', 'content_domain', 'document_category')
    def validate_non_empty_lists(cls, v):
        if not v or len(v) == 0:
            raise ValueError('List cannot be empty')
        # Normalize to lowercase and filter empty strings
        normalized = [item.strip().lower() for item in v if item.strip()]
        if not normalized:
            raise ValueError('List cannot contain only empty values')
        return normalized
    
    @validator('relevance_tags')
    def validate_relevance_tags(cls, v):
        if v:
            # Normalize to lowercase and filter empty strings
            normalized = [tag.strip().lower() for tag in v if tag.strip()]
            return normalized
        return v

class SystemMessageDirective(BaseModel):
    """Parsed system message directives"""
    response_mode: ResponseMode = ResponseMode.SMART_FALLBACK
    document_context: Optional[List[str]] = None  # List of context types to use
    content_domains: Optional[List[str]] = None  # List of content domains to focus on
    document_categories: Optional[List[str]] = None  # List of document categories to use
    min_confidence: Optional[float] = 0.7  # Minimum confidence for RAG results
    fallback_strategy: str = "hybrid"  # llm_knowledge, refuse, hybrid
    
    @validator('min_confidence')
    def validate_confidence(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('min_confidence must be between 0.0 and 1.0')
        return v

class DocumentUploadRequest(BaseModel):
    """Enhanced document upload request with mandatory context"""
    file_path: str
    context: DocumentContext  # MANDATORY context
    
    @validator('file_path')
    def file_path_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('File path cannot be empty')
        return v.strip()

class TextUploadRequest(BaseModel):
    """Enhanced text upload request with mandatory context"""
    text: str
    context: DocumentContext  # MANDATORY context
    source_name: Optional[str] = None
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip()

class ContextAwareQuestionRequest(BaseModel):
    """Enhanced question request with context awareness"""
    question: str
    top_k: Optional[int] = None
    context_filter: Optional[DocumentContext] = None  # Optional context filtering
    
    @validator('question')
    def question_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()
    
    @validator('top_k')
    def top_k_must_be_valid(cls, v):
        if v is not None and v <= 0:
            raise ValueError('top_k must be greater than 0')
        return v 