# API Usage Examples

## Quick Start Examples

### 1. Health Check

#### cURL
```bash
curl -X GET "http://localhost:8000/"
```

#### Python
```python
import requests

response = requests.get("http://localhost:8000/")
print(response.json())
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-05-01T12:00:00"
}
```

### 2. Upload Document

#### cURL
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_document.pdf"
```

#### Python
```python
import requests

with open("your_document.pdf", "rb") as file:
    files = {"file": file}
    response = requests.post(
        "http://localhost:8000/documents/upload",
        files=files
    )
    print(response.json())
```

**Response:**
```json
{
  "success": true,
  "message": "Document 'your_document.pdf' added successfully",
  "chunks_processed": 5
}
```

### 3. Add Text Content

#### cURL
```bash
curl -X POST "http://localhost:8000/documents/add-text" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Python is a high-level programming language created by Guido van Rossum in 1991.",
       "source_name": "python_info"
     }'
```

#### Python
```python
import requests

data = {
    "text": "Python is a high-level programming language created by Guido van Rossum in 1991.",
    "source_name": "python_info"
}

response = requests.post(
    "http://localhost:8000/documents/add-text",
    json=data
)
print(response.json())
```

**Response:**
```json
{
  "success": true,
  "message": "Text from 'python_info' added successfully",
  "chunks_processed": 1
}
```

### 4. Ask Questions

#### cURL
```bash
curl -X POST "http://localhost:8000/questions/ask" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What is Python?",
       "top_k": 3
     }'
```

#### Python
```python
import requests

data = {
    "question": "What is Python?",
    "top_k": 3
}

response = requests.post(
    "http://localhost:8000/questions/ask",
    json=data
)
print(response.json())
```

**Response:**
```json
{
  "success": true,
  "answer": "Python is a high-level programming language created by Guido van Rossum in 1991...",
  "sources": [
    {
      "content": "Python is a high-level programming language...",
      "metadata": {"source": "python_info"},
      "score": 0.95
    }
  ],
  "context_used": "Python is a high-level programming language..."
}
```

### 5. Basic Chat Completions

#### cURL
```bash
curl -X POST "http://localhost:8000/chat/completions" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [
         {
           "role": "system",
           "content": "You are a helpful assistant."
         },
         {
           "role": "user",
           "content": "What is the main topic?"
         }
       ],
       "temperature": 0.7,
       "max_tokens": 500
     }'
```

#### Python
```python
import requests

data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "What is the main topic?"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 500
}

response = requests.post(
    "http://localhost:8000/chat/completions",
    json=data
)
print(response.json())
```

**Response:**
```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on the available information..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 45,
    "total_tokens": 195
  },
  "sources": [
    {
      "content": "Relevant content from documents",
      "metadata": {"source": "document.pdf"},
      "score": 0.92
    }
  ]
}
```

## Enhanced Chat Completion Examples

### 6. Conversation-Aware Chat Completions

#### cURL
```bash
curl -X POST "http://localhost:8000/enhanced-chat/completions" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [
         {
           "role": "system",
           "content": "You are a technical support specialist for software products."
         },
         {
           "role": "user",
           "content": "I am having trouble installing the software."
         },
         {
           "role": "assistant",
           "content": "I can help you with the installation. What operating system are you using?"
         },
         {
           "role": "user",
           "content": "Windows 10. I get a permission error."
         }
       ],
       "temperature": 0.7,
       "max_tokens": 1000
     }'
```

#### Python
```python
import requests

data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "system",
            "content": "You are a technical support specialist for software products."
        },
        {
            "role": "user",
            "content": "I am having trouble installing the software."
        },
        {
            "role": "assistant",
            "content": "I can help you with the installation. What operating system are you using?"
        },
        {
            "role": "user",
            "content": "Windows 10. I get a permission error."
        }
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

response = requests.post(
    "http://localhost:8000/enhanced-chat/completions",
    json=data
)
print(response.json())
```

**Response:**
```json
{
  "id": "chatcmpl-enhanced-1234567890",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on your Windows 10 system and the permission error you're experiencing, here are the steps to resolve this issue:\n\n1. **Run as Administrator**: Right-click the installer and select 'Run as administrator'\n2. **Check User Account Control**: Temporarily disable UAC or adjust settings\n3. **Verify File Permissions**: Ensure you have write permissions to the installation directory\n\nWould you like me to provide more specific troubleshooting steps for your situation?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 250,
    "completion_tokens": 120,
    "total_tokens": 370
  },
  "sources": [
    {
      "content": "Windows 10 installation troubleshooting guide with permission error solutions",
      "metadata": {"source": "installation_guide.pdf"},
      "score": 0.92
    }
  ],
  "metadata": {
    "conversation_aware": true,
    "strategy_used": "topic_tracking",
    "enhanced_queries_count": 4,
    "conversation_context": {
      "topics": ["software", "installation", "permission", "error", "windows"],
      "entities": ["Windows 10", "permission error"],
      "conversation_length": 4
    },
    "processing_plugins": ["conversation_context", "multi_query_rag", "response_enhancement"]
  }
}
```

### 7. Entity Extraction Strategy Example

#### cURL
```bash
curl -X POST "http://localhost:8000/enhanced-chat/completions" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "gpt-3.5-turbo",
       "messages": [
         {
           "role": "system",
           "content": "You are a data analyst. Extract and analyze entities from the conversation."
         },
         {
           "role": "user",
           "content": "I need information about John Smith, the CEO of TechCorp, and their relationship with Microsoft."
         }
       ],
       "temperature": 0.7,
       "max_tokens": 1000
     }'
```

#### Python
```python
import requests

data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "system",
            "content": "You are a data analyst. Extract and analyze entities from the conversation."
        },
        {
            "role": "user",
            "content": "I need information about John Smith, the CEO of TechCorp, and their relationship with Microsoft."
        }
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

response = requests.post(
    "http://localhost:8000/enhanced-chat/completions",
    json=data
)
print(response.json())
```

**Response:**
```json
{
  "id": "chatcmpl-enhanced-1234567891",
  "object": "chat.completion",
  "created": 1677652289,
  "model": "gpt-3.5-turbo",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on the available information, here's what I found about the entities you mentioned:\n\n**John Smith**: CEO of TechCorp\n**TechCorp**: Technology company\n**Microsoft**: Technology corporation\n\n**Relationship Analysis**: TechCorp has a strategic partnership with Microsoft..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 200,
    "completion_tokens": 150,
    "total_tokens": 350
  },
  "sources": [
    {
      "content": "TechCorp company profile and leadership information",
      "metadata": {"source": "company_profiles.pdf"},
      "score": 0.89
    }
  ],
  "metadata": {
    "conversation_aware": true,
    "strategy_used": "entity_extraction",
    "enhanced_queries_count": 3,
    "conversation_context": {
      "topics": ["data_analysis", "entity_extraction"],
      "entities": ["John Smith", "TechCorp", "Microsoft", "CEO"],
      "relationships": ["CEO_of", "partnership_with"],
      "conversation_length": 2
    },
    "processing_plugins": ["conversation_context", "multi_query_rag", "response_enhancement"]
  }
}
```

### 8. Get Available Strategies

#### cURL
```bash
curl -X GET "http://localhost:8000/enhanced-chat/strategies"
```

#### Python
```python
import requests

response = requests.get("http://localhost:8000/enhanced-chat/strategies")
print(response.json())
```

**Response:**
```json
{
  "strategies": [
    {
      "name": "topic_tracking",
      "description": "Tracks conversation topics and generates topic-aware queries",
      "features": ["topic_extraction", "context_awareness", "conversation_flow"]
    },
    {
      "name": "entity_extraction",
      "description": "Extracts entities and relationships for enhanced query generation",
      "features": ["entity_recognition", "relationship_mapping", "semantic_analysis"]
    }
  ]
}
```

### 9. Get Available Plugins

#### cURL
```bash
curl -X GET "http://localhost:8000/enhanced-chat/plugins"
```

#### Python
```python
import requests

response = requests.get("http://localhost:8000/enhanced-chat/plugins")
print(response.json())
```

**Response:**
```json
{
  "plugins": [
    {
      "name": "conversation_context",
      "description": "Analyzes conversation context and extracts relevant information",
      "priority": "HIGH"
    },
    {
      "name": "multi_query_rag",
      "description": "Generates multiple enhanced queries for improved document retrieval",
      "priority": "NORMAL"
    },
    {
      "name": "response_enhancement",
      "description": "Enhances final response with context and metadata",
      "priority": "LOW"
    }
  ]
}
```

## Advanced Usage Examples

### 10. Multi-Turn Conversation with Context Preservation

#### Python
```python
import requests

# First turn
conversation = [
    {
        "role": "system",
        "content": "You are a customer service representative for an e-commerce platform."
    },
    {
        "role": "user",
        "content": "I want to return a product I bought last week."
    }
]

data = {
    "model": "gpt-3.5-turbo",
    "messages": conversation,
    "temperature": 0.7,
    "max_tokens": 1000
}

response = requests.post(
    "http://localhost:8000/enhanced-chat/completions",
    json=data
)
first_response = response.json()

# Add assistant response to conversation
conversation.append({
    "role": "assistant",
    "content": first_response["choices"][0]["message"]["content"]
})

# Second turn - the system will remember the context
conversation.append({
    "role": "user",
    "content": "The order number is ORD-12345. Can you help me with the return process?"
})

data["messages"] = conversation

response = requests.post(
    "http://localhost:8000/enhanced-chat/completions",
    json=data
)
second_response = response.json()

print("First Response:", first_response["choices"][0]["message"]["content"])
print("Second Response:", second_response["choices"][0]["message"]["content"])
print("Strategy Used:", second_response["metadata"]["strategy_used"])
print("Enhanced Queries:", second_response["metadata"]["enhanced_queries_count"])
```

### 11. Error Handling Examples

#### Missing Messages
```python
import requests

data = {
    "model": "gpt-3.5-turbo",
    "messages": [],  # Empty messages
    "temperature": 0.7,
    "max_tokens": 1000
}

try:
    response = requests.post(
        "http://localhost:8000/enhanced-chat/completions",
        json=data
    )
    print(response.json())
except requests.exceptions.HTTPError as e:
    print(f"Error: {e}")
    print(f"Response: {e.response.json()}")
```

**Error Response:**
```json
{
  "detail": "Messages cannot be empty"
}
```

#### No User Message
```python
import requests

data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        }
        # No user message
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

try:
    response = requests.post(
        "http://localhost:8000/enhanced-chat/completions",
        json=data
    )
    print(response.json())
except requests.exceptions.HTTPError as e:
    print(f"Error: {e}")
    print(f"Response: {e.response.json()}")
```

**Error Response:**
```json
{
  "detail": "No user message found"
}
```

## Performance Considerations

### 12. Batch Processing Example

```python
import requests
import asyncio
import aiohttp
from typing import List, Dict

async def batch_enhanced_chat_completions(
    requests_data: List[Dict],
    base_url: str = "http://localhost:8000"
) -> List[Dict]:
    """Process multiple enhanced chat completion requests concurrently"""
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for data in requests_data:
            task = session.post(
                f"{base_url}/enhanced-chat/completions",
                json=data
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return [await response.json() for response in responses]

# Example usage
requests_data = [
    {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Question {i}?"}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    for i in range(5)
]

# Run batch processing
results = asyncio.run(batch_enhanced_chat_completions(requests_data))
for i, result in enumerate(results):
    print(f"Request {i}: {result['metadata']['strategy_used']}")
```

## Integration Examples

### 13. Integration with External Systems

```python
import requests
import json
from datetime import datetime

class EnhancedChatClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def chat_completion(
        self,
        messages: List[Dict],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict:
        """Send enhanced chat completion request"""
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = self.session.post(
            f"{self.base_url}/enhanced-chat/completions",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def get_strategies(self) -> Dict:
        """Get available strategies"""
        response = self.session.get(f"{self.base_url}/enhanced-chat/strategies")
        response.raise_for_status()
        return response.json()
    
    def get_plugins(self) -> Dict:
        """Get available plugins"""
        response = self.session.get(f"{self.base_url}/enhanced-chat/plugins")
        response.raise_for_status()
        return response.json()

# Usage example
client = EnhancedChatClient()

# Get system information
strategies = client.get_strategies()
plugins = client.get_plugins()

print("Available Strategies:", [s["name"] for s in strategies["strategies"]])
print("Available Plugins:", [p["name"] for p in plugins["plugins"]])

# Send chat completion
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the weather like today?"}
]

response = client.chat_completion(messages)
print(f"Response: {response['choices'][0]['message']['content']}")
print(f"Strategy Used: {response['metadata']['strategy_used']}")
``` 