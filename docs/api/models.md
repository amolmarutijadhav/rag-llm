# API Models Reference

## Request Models

### TextInputRequest
Used for adding raw text to the knowledge base.

```python
class TextInputRequest(BaseModel):
    text: str
    source_name: Optional[str] = "text_input"
```

**Fields:**
- `text` (str, required): The text content to add
- `source_name` (str, optional): Name for the text source (default: "text_input")

### QuestionRequest
Used for asking questions to the RAG system.

```python
class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3
```

**Fields:**
- `question` (str, required): The question to ask
- `top_k` (int, optional): Number of top results to retrieve (default: 3)

### ChatCompletionRequest
Used for RAG-enhanced chat completions.

```python
class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    # Additional OpenAI parameters as needed
```

**Fields:**
- `model` (str, required): The model to use (e.g., "gpt-3.5-turbo")
- `messages` (List[Dict], required): List of message objects
- `temperature` (float, optional): Response randomness (default: 0.7)
- `max_tokens` (int, optional): Maximum tokens in response (default: 1000)

## Response Models

### HealthResponse
Health check endpoint response.

```python
class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
```

**Fields:**
- `status` (str): Health status ("healthy")
- `version` (str): API version
- `timestamp` (str): ISO timestamp

### DocumentResponse
Response for document operations.

```python
class DocumentResponse(BaseModel):
    success: bool
    message: str
    chunks_processed: Optional[int] = None
```

**Fields:**
- `success` (bool): Operation success status
- `message` (str): Descriptive message
- `chunks_processed` (int, optional): Number of chunks processed

### QuestionResponse
Response for question answering.

```python
class QuestionResponse(BaseModel):
    success: bool
    answer: str
    sources: List[Dict[str, Any]]
    context_used: str
```

**Fields:**
- `success` (bool): Operation success status
- `answer` (str): Generated answer
- `sources` (List[Dict]): Source documents with metadata
- `context_used` (str): Combined context from retrieved documents

### Source Document Structure
```python
{
    "content": "Document content snippet",
    "metadata": {
        "source": "document_name",
        "chunk_index": 0
    },
    "score": 0.8670988  # Similarity score
}
```

### StatsResponse
System statistics response.

```python
class StatsResponse(BaseModel):
    success: bool
    vector_store: Dict[str, Any]
    supported_formats: List[str]
    chunk_size: int
    chunk_overlap: int
```

**Fields:**
- `success` (bool): Operation success status
- `vector_store` (Dict): Vector store statistics
- `supported_formats` (List[str]): Supported file formats
- `chunk_size` (int): Document chunk size
- `chunk_overlap` (int): Chunk overlap size

### Vector Store Statistics
```python
{
    "total_documents": 2,
    "collection_name": "documents",
    "vector_size": 1536
}
```

### ChatCompletionResponse
RAG-enhanced chat completion response.

```python
class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    rag_metadata: Dict[str, Any]
```

**Fields:**
- `id` (str): Unique completion ID
- `object` (str): Object type ("chat.completion")
- `created` (int): Unix timestamp
- `model` (str): Model used
- `choices` (List[Dict]): Generated responses
- `usage` (Dict): Token usage statistics
- `rag_metadata` (Dict): RAG processing metadata

### RAG Metadata Structure
```python
{
    "agent_persona_preserved": True,
    "context_documents_found": 2,
    "original_message_count": 2,
    "enhanced_message_count": 2
}
```

## Message Models

### Chat Message Structure
```python
{
    "role": "system|user|assistant",
    "content": "Message content"
}
```

**Roles:**
- `system`: System instructions or agent persona
- `user`: User input messages
- `assistant`: AI-generated responses

### Multi-Agentic Message Validation
- First message must be `system` role (agent persona)
- Must contain at least one `user` message
- Supports multiple agents with different personas

## Error Models

### HTTPException
Standard FastAPI error response.

```python
{
    "detail": "Error message description"
}
```

### ValidationError
Pydantic validation error response.

```python
{
    "detail": [
        {
            "loc": ["body", "field_name"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

## Configuration Models

### Environment Variables
All configuration is externalized via environment variables:

```python
# API Endpoints
EMBEDDING_API_URL
VECTOR_COLLECTION_URL
VECTOR_INSERT_API_URL
VECTOR_SEARCH_API_URL
LLM_API_URL

# Authentication
OPENAI_API_KEY
QDRANT_API_KEY

# Processing Configuration
CHUNK_SIZE
CHUNK_OVERLAP
TOP_K_RESULTS
RAG_PROMPT_TEMPLATE

# Model Configuration
EMBEDDING_MODEL
LLM_MODEL
VECTOR_SIZE
VECTOR_DISTANCE_METRIC
```

## Data Types

### Supported File Formats
- `.pdf`: PDF documents
- `.txt`: Text files
- `.docx`: Word documents

### Vector Configuration
- **Vector Size**: 1536 dimensions
- **Distance Metric**: Cosine similarity
- **Embedding Model**: text-embedding-ada-002
- **LLM Model**: gpt-3.5-turbo (configurable) 