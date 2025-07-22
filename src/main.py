import os
import tempfile
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.rag_service import RAGService
from src.models import (
    QuestionRequest, QuestionResponse, TextInputRequest, 
    DocumentResponse, StatsResponse, HealthResponse
)
from src.config import Config

# Helper functions for multi-agentic RAG processing
def extract_last_user_message(messages: List[Dict[str, str]]) -> str:
    """Extract the last user message from the conversation"""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""

def validate_multi_agent_messages(messages: List[Dict[str, str]]) -> bool:
    """Validate that messages follow multi-agentic structure"""
    if not messages:
        return False
    
    # Check if first message is system (agent persona)
    if messages[0].get("role") != "system":
        return False
    
    # Check for at least one user message
    has_user_message = any(msg.get("role") == "user" for msg in messages)
    if not has_user_message:
        return False
    
    return True

def get_agent_persona(messages: List[Dict[str, str]]) -> str:
    """Extract the agent's persona from system message"""
    if messages and messages[0].get("role") == "system":
        return messages[0].get("content", "")
    return ""

def enhance_messages_with_rag(messages: List[Dict[str, str]], relevant_docs: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Enhance messages with RAG context while preserving agent persona"""
    if not relevant_docs:
        return messages
    
    # Prepare RAG context
    context = "\n\n".join([doc["content"] for doc in relevant_docs])
    rag_enhancement = f"\n\nYou have access to the following relevant information that may help answer the user's question:\n{context}\n\nUse this information to provide more accurate and helpful responses while maintaining your designated role and personality."
    
    enhanced_messages = []
    
    for i, message in enumerate(messages):
        if i == 0 and message.get("role") == "system":
            # Enhance the first system message with RAG context
            enhanced_content = message["content"] + rag_enhancement
            enhanced_messages.append({
                "role": "system",
                "content": enhanced_content
            })
        else:
            # Keep other messages unchanged
            enhanced_messages.append(message)
    
    return enhanced_messages

# Initialize FastAPI app
app = FastAPI(
    title="RAG LLM API",
    description="A simple RAG (Retrieval-Augmented Generation) API for document Q&A",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service
rag_service = RAGService()

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question and get an answer using RAG"""
    try:
        result = await rag_service.ask_question(request.question, request.top_k)
        return QuestionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file size
        if file.size and file.size > Config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size is {Config.MAX_FILE_SIZE} bytes"
            )
        
        # Validate file format
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in Config.SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {Config.SUPPORTED_FORMATS}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process the document using external APIs
            result = await rag_service.add_document(temp_file_path)
            return DocumentResponse(**result)
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add-text", response_model=DocumentResponse)
async def add_text(request: TextInputRequest):
    """Add raw text to the knowledge base"""
    try:
        result = await rag_service.add_text(request.text, request.source_name)
        return DocumentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics"""
    try:
        result = rag_service.get_stats()
        return StatsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear", response_model=DocumentResponse)
async def clear_knowledge_base():
    """Clear all documents from the knowledge base"""
    try:
        result = rag_service.clear_knowledge_base()
        return DocumentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/chat/completions")
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
        
        # Get RAG context
        relevant_docs = await rag_service.vector_store.search(last_user_message, top_k=3)
        
        # Enhance messages while preserving agent persona
        enhanced_messages = enhance_messages_with_rag(messages, relevant_docs)
        
        # Forward to OpenAI
        modified_request = request.copy()
        modified_request["messages"] = enhanced_messages
        
        response = await rag_service.api_service.call_openai_completions(modified_request)
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG
    ) 