from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from app.domain.services.rag_service import RAGService
from app.infrastructure.providers import get_llm_provider
from app.core.config import Config
from app.utils.message_utils import (
    extract_last_user_message,
    validate_multi_agent_messages,
    get_agent_persona,
    enhance_messages_with_rag
)

router = APIRouter()
rag_service = RAGService()

@router.post("/chat/completions")
async def rag_chat_completions_multi_agent(request: Dict[str, Any]):
    """RAG-enhanced chat completions for multi-agentic systems"""
    try:
        messages = request.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Validate multi-agentic structure
        if not validate_multi_agent_messages(messages):
            raise HTTPException(
                status_code=400, 
                detail="Invalid message structure. First message must be 'system' role for agent persona."
            )
        
        # Extract agent persona for logging/debugging
        agent_persona = get_agent_persona(messages)
        
        # Extract the last user message for RAG search
        last_user_message = extract_last_user_message(messages)
        if not last_user_message:
            raise HTTPException(status_code=400, detail="No user message found")
        
        # Get RAG context with configurable top_k
        relevant_docs = await rag_service.vector_store.search(last_user_message, top_k=Config.DEFAULT_TOP_K)
        
        # Enhance messages while preserving agent persona
        enhanced_messages = enhance_messages_with_rag(messages, relevant_docs)
        
        # Forward to LLM provider using plugin architecture
        modified_request = request.copy()
        modified_request["messages"] = enhanced_messages
        
        # Get LLM provider from service locator
        llm_provider = get_llm_provider()
        response = await llm_provider.call_llm_api(modified_request, return_full_response=True)
        
        # Add metadata for debugging
        response["rag_metadata"] = {
            "agent_persona_preserved": True,
            "context_documents_found": len(relevant_docs),
            "original_message_count": len(messages),
            "enhanced_message_count": len(enhanced_messages)
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG processing error: {str(e)}") 