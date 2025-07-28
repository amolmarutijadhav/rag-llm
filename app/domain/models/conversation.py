from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ConversationContext(BaseModel):
    """Model representing the context extracted from a conversation"""
    topics: List[str] = []
    entities: List[str] = []
    context_clues: List[str] = []
    question_evolution: List[str] = []
    conversation_length: int = 0
    last_user_message: Optional[str] = None
    conversation_summary: Optional[str] = None
    extracted_at: datetime = datetime.now()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ConversationAnalysisResult(BaseModel):
    """Result of conversation analysis"""
    context: ConversationContext
    confidence_score: float
    analysis_method: str
    processing_time_ms: float

class EnhancedQuery(BaseModel):
    """Enhanced query with conversation context"""
    original_query: str
    enhanced_queries: List[str]
    context_used: ConversationContext
    query_generation_method: str 