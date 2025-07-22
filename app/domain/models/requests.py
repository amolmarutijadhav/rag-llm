from pydantic import BaseModel, Field
from typing import Optional

class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str = Field(..., description="The question to ask")
    top_k: Optional[int] = Field(3, description="Number of relevant documents to retrieve")

class TextInputRequest(BaseModel):
    """Request model for adding text to knowledge base"""
    text: str = Field(..., description="Text content to add")
    source_name: Optional[str] = Field("text_input", description="Name for the text source") 