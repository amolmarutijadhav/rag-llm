from pydantic import BaseModel, validator
from typing import Optional, List

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