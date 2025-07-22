from fastapi import APIRouter, HTTPException
from app.domain.models import QuestionRequest, QuestionResponse, StatsResponse
from app.domain.services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question and get an answer using RAG"""
    try:
        result = await rag_service.ask_question(request.question, request.top_k)
        return QuestionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics"""
    try:
        result = rag_service.get_stats()
        return StatsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 