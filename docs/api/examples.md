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
       "question": "Who created Python?",
       "top_k": 3
     }'
```

#### Python
```python
import requests

data = {
    "question": "Who created Python?",
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
  "answer": "Python was created by Guido van Rossum in 1991.",
  "sources": [
    {
      "content": "Python is a high-level programming language created by Guido van Rossum in 1991.",
      "metadata": {"source": "python_info", "chunk_index": 0},
      "score": 0.9876543
    }
  ],
  "context_used": "Python is a high-level programming language created by Guido van Rossum in 1991."
}
```

### 5. RAG-Enhanced Chat Completions

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
           "content": "You are a helpful technical assistant. Answer questions based on the provided context."
         },
         {
           "role": "user",
           "content": "What are the main features of Python?"
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
            "content": "You are a helpful technical assistant. Answer questions based on the provided context."
        },
        {
            "role": "user",
            "content": "What are the main features of Python?"
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
        "content": "Based on the context, Python is a high-level programming language created by Guido van Rossum in 1991. It's known for its simplicity, readability, and extensive standard library."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 45,
    "total_tokens": 195
  },
  "rag_metadata": {
    "agent_persona_preserved": true,
    "context_documents_found": 1,
    "original_message_count": 2,
    "enhanced_message_count": 2
  }
}
```

### 6. Get System Statistics

#### cURL
```bash
curl -X GET "http://localhost:8000/stats"
```

#### Python
```python
import requests

response = requests.get("http://localhost:8000/stats")
print(response.json())
```

**Response:**
```json
{
  "success": true,
  "vector_store": {
    "total_documents": 2,
    "collection_name": "documents",
    "vector_size": 1536
  },
  "supported_formats": [".pdf", ".txt", ".docx"],
  "chunk_size": 1000,
  "chunk_overlap": 200
}
```

### 7. Clear Knowledge Base

#### cURL
```bash
curl -X DELETE "http://localhost:8000/documents/clear"
```

#### Python
```python
import requests

response = requests.delete("http://localhost:8000/documents/clear")
print(response.json())
```

**Response:**
```json
{
  "success": true,
  "message": "Knowledge base cleared successfully"
}
```

## Advanced Examples

### Multi-Agentic Chat System

#### Customer Service Agent
```python
import requests

# Customer service agent conversation
messages = [
    {
        "role": "system",
        "content": "You are a helpful customer service agent for TechCorp. You are friendly, professional, and knowledgeable about our products."
    },
    {
        "role": "user",
        "content": "What are the specifications of the X1 laptop?"
    }
]

data = {
    "model": "gpt-3.5-turbo",
    "messages": messages,
    "temperature": 0.7,
    "max_tokens": 500
}

response = requests.post(
    "http://localhost:8000/chat/completions",
    json=data
)
print(response.json())
```

#### Technical Support Agent
```python
import requests

# Technical support agent conversation
messages = [
    {
        "role": "system",
        "content": "You are a technical support specialist. You help users with technical issues and provide detailed troubleshooting steps."
    },
    {
        "role": "user",
        "content": "How do I install Python on Windows?"
    }
]

data = {
    "model": "gpt-3.5-turbo",
    "messages": messages,
    "temperature": 0.5,
    "max_tokens": 800
}

response = requests.post(
    "http://localhost:8000/chat/completions",
    json=data
)
print(response.json())
```

### Batch Document Processing

```python
import requests
import os

def upload_documents(directory_path):
    """Upload all documents in a directory"""
    supported_extensions = ['.pdf', '.txt', '.docx']
    
    for filename in os.listdir(directory_path):
        if any(filename.endswith(ext) for ext in supported_extensions):
            file_path = os.path.join(directory_path, filename)
            
            with open(file_path, "rb") as file:
                files = {"file": file}
                response = requests.post(
                    "http://localhost:8000/documents/upload",
                    files=files
                )
                
                if response.status_code == 200:
                    print(f"✅ {filename}: {response.json()['message']}")
                else:
                    print(f"❌ {filename}: {response.json()['detail']}")

# Usage
upload_documents("./documents")
```

### Interactive Question Answering

```python
import requests

def interactive_qa():
    """Interactive question answering session"""
    print("🤖 RAG Question Answering System")
    print("Type 'quit' to exit\n")
    
    while True:
        question = input("❓ Your question: ")
        
        if question.lower() == 'quit':
            break
        
        data = {
            "question": question,
            "top_k": 3
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/questions/ask",
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n🤖 Answer: {result['answer']}")
                
                if result['sources']:
                    print("\n📚 Sources:")
                    for i, source in enumerate(result['sources'], 1):
                        print(f"  {i}. {source['content'][:100]}... (Score: {source['score']:.3f})")
            else:
                print(f"❌ Error: {response.json()['detail']}")
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        print("\n" + "="*50 + "\n")

# Usage
interactive_qa()
```

### Error Handling Examples

#### Handle File Upload Errors
```python
import requests

def safe_upload_document(file_path):
    """Safely upload a document with error handling"""
    try:
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(
                "http://localhost:8000/documents/upload",
                files=files
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 400:
                error_detail = response.json()['detail']
                if "File too large" in error_detail:
                    return {"error": "File size exceeds limit (10MB)"}
                elif "Unsupported file format" in error_detail:
                    return {"error": "File format not supported"}
                else:
                    return {"error": error_detail}
            else:
                return {"error": f"Server error: {response.status_code}"}
                
    except FileNotFoundError:
        return {"error": "File not found"}
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}

# Usage
result = safe_upload_document("large_document.pdf")
if "error" in result:
    print(f"❌ {result['error']}")
else:
    print(f"✅ {result['message']}")
```

#### Handle API Key Errors
```python
import requests

def check_api_status():
    """Check if API keys are properly configured"""
    try:
        response = requests.get("http://localhost:8000/")
        
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# Usage
if check_api_status():
    print("Ready to use the API!")
else:
    print("Please check your API configuration")
```

## Integration Examples

### FastAPI Client Integration

```python
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.post("/process-document")
async def process_document(file_path: str):
    """Process document through RAG API"""
    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = await client.post(
                "http://localhost:8000/documents/upload",
                files=files
            )
            return response.json()

@app.post("/ask-question")
async def ask_question(question: str):
    """Ask question through RAG API"""
    async with httpx.AsyncClient() as client:
        data = {"question": question, "top_k": 3}
        response = await client.post(
            "http://localhost:8000/questions/ask",
            json=data
        )
        return response.json()
```

### JavaScript/Node.js Integration

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

// Upload document
async function uploadDocument(filePath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    
    try {
        const response = await axios.post('http://localhost:8000/documents/upload', form, {
            headers: form.getHeaders()
        });
        return response.data;
    } catch (error) {
        console.error('Upload error:', error.response?.data || error.message);
        throw error;
    }
}

// Ask question
async function askQuestion(question) {
    try {
        const response = await axios.post('http://localhost:8000/questions/ask', {
            question: question,
            top_k: 3
        });
        return response.data;
    } catch (error) {
        console.error('Question error:', error.response?.data || error.message);
        throw error;
    }
}

// Usage
uploadDocument('./document.pdf')
    .then(result => console.log('Upload result:', result))
    .catch(error => console.error('Error:', error));

askQuestion('What is the main topic?')
    .then(result => console.log('Answer:', result.answer))
    .catch(error => console.error('Error:', error));
``` 