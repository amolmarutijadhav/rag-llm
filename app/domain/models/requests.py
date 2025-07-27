from pydantic import BaseModel, Field, validator
from typing import Optional

class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str = Field(..., min_length=1, description="The question to ask")
    top_k: Optional[int] = Field(3, ge=1, le=100, description="Number of relevant documents to retrieve")
    
    @validator('question')
    def question_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()

class TextInputRequest(BaseModel):
    """Request model for adding text to knowledge base"""
    text: str = Field(..., min_length=1, description="Text content to add")
    source_name: Optional[str] = Field("text_input", description="Name for the text source")
    
    @validator('text')
    def text_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        return v.strip() 