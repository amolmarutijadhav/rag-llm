"""
Sample data and fixtures for testing
"""

import pytest
from typing import List, Dict, Any

# Sample documents for testing
SAMPLE_DOCUMENTS = [
    {
        "id": "doc1",
        "content": "Python is a programming language created by Guido van Rossum in 1991.",
        "metadata": {"source": "python_info.txt", "page": 1, "chunk_index": 0}
    },
    {
        "id": "doc2",
        "content": "Java is a high-level, class-based, object-oriented programming language developed by James Gosling at Sun Microsystems in 1995.",
        "metadata": {"source": "java_info.txt", "page": 1, "chunk_index": 0}
    },
    {
        "id": "doc3",
        "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions without being explicitly programmed.",
        "metadata": {"source": "ml_info.txt", "page": 1, "chunk_index": 0}
    }
]

# Sample questions and expected responses
SAMPLE_QUESTIONS = [
    {
        "question": "Who created Python?",
        "expected_keywords": ["Guido van Rossum", "1991"],
        "category": "programming_language"
    },
    {
        "question": "Who created Java?",
        "expected_keywords": ["James Gosling", "Sun Microsystems", "1995"],
        "category": "programming_language"
    },
    {
        "question": "What is machine learning?",
        "expected_keywords": ["artificial intelligence", "learn", "decisions"],
        "category": "ai_ml"
    }
]

# Sample chat messages for testing
SAMPLE_CHAT_MESSAGES = [
    {
        "role": "system",
        "content": "You are a helpful programming assistant."
    },
    {
        "role": "user",
        "content": "Tell me about Python programming language."
    }
]

# Sample API responses
SAMPLE_API_RESPONSES = {
    "openai_chat_completion": {
        "id": "chatcmpl-1234567890",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-3.5-turbo",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Python is a high-level programming language known for its simplicity and readability."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 25,
            "total_tokens": 75
        }
    },
    "openai_embeddings": {
        "object": "list",
        "data": [
            {
                "object": "embedding",
                "embedding": [0.1, 0.2, 0.3] * 512,  # 1536 dimensions
                "index": 0
            }
        ],
        "model": "text-embedding-ada-002",
        "usage": {
            "prompt_tokens": 10,
            "total_tokens": 10
        }
    },
    "qdrant_search": {
        "result": [
            {
                "id": "doc1",
                "score": 0.95,
                "payload": {
                    "content": "Python is a programming language created by Guido van Rossum in 1991.",
                    "metadata": {"source": "python_info.txt"}
                }
            }
        ]
    }
}

# Sample error responses
SAMPLE_ERROR_RESPONSES = {
    "validation_error": {
        "detail": [
            {
                "loc": ["body", "question"],
                "msg": "field required",
                "type": "value_error.missing"
            }
        ]
    },
    "not_found": {
        "detail": "Not Found"
    },
    "internal_error": {
        "detail": "Internal server error"
    }
}

@pytest.fixture
def sample_documents():
    """Fixture providing sample documents for testing"""
    return SAMPLE_DOCUMENTS

@pytest.fixture
def sample_questions():
    """Fixture providing sample questions for testing"""
    return SAMPLE_QUESTIONS

@pytest.fixture
def sample_chat_messages():
    """Fixture providing sample chat messages for testing"""
    return SAMPLE_CHAT_MESSAGES

@pytest.fixture
def sample_api_responses():
    """Fixture providing sample API responses for testing"""
    return SAMPLE_API_RESPONSES

@pytest.fixture
def sample_error_responses():
    """Fixture providing sample error responses for testing"""
    return SAMPLE_ERROR_RESPONSES

@pytest.fixture
def sample_question_request():
    """Fixture providing a sample question request"""
    return {
        "question": "Who created Python?",
        "top_k": 3
    }

@pytest.fixture
def sample_text_input_request():
    """Fixture providing a sample text input request"""
    return {
        "text": "Python is a programming language created by Guido van Rossum in 1991.",
        "source_name": "python_info"
    }

@pytest.fixture
def sample_chat_completion_request():
    """Fixture providing a sample chat completion request"""
    return {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful programming assistant."
            },
            {
                "role": "user",
                "content": "Tell me about Python programming language."
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    } 