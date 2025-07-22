from typing import List, Dict, Any

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