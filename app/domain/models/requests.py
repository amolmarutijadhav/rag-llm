from pydantic import BaseModel, validator
from typing import Optional

class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = None
    
    @validator('question')
    def question_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()

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