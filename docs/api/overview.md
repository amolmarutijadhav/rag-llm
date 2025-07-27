# API Overview

## Introduction

The RAG LLM API is a production-ready Retrieval-Augmented Generation (RAG) system built with FastAPI, LangChain, and Qdrant Cloud. It provides a comprehensive solution for document processing, semantic search, and AI-powered question answering.

## Architecture Overview

The API follows a **Domain-Driven Design** architecture with clear separation of concerns:

```
app/
├── api/          # API layer (routes, middleware)
├── core/         # Core configuration and utilities
├── domain/       # Business logic and models
├── infrastructure/ # External integrations
└── utils/        # Helper functions
```

## Key Components

### 1. Document Processing
- **Supported Formats**: PDF, TXT, DOCX
- **Chunking Strategy**: Configurable chunk size and overlap
- **Embedding**: OpenAI text-embedding-ada-002 model
- **Vector Storage**: Qdrant Cloud with 1536-dimensional vectors

### 2. RAG Pipeline
1. **Document Ingestion**: Upload or add text content
2. **Chunking**: Split documents into manageable pieces
3. **Embedding**: Convert chunks to vector representations
4. **Storage**: Store vectors in Qdrant Cloud
5. **Retrieval**: Semantic search for relevant context
6. **Generation**: AI-powered answer generation

### 3. Multi-Agentic Support
- **Agent Persona Preservation**: Maintains agent personalities in chat completions
- **Context Integration**: Seamlessly adds RAG context to agent knowledge
- **Backward Compatibility**: Works with existing OpenAI chat completions

## Core Features

### ✅ Document Management
- Upload documents (PDF, TXT, DOCX)
- Add raw text to knowledge base
- Clear entire knowledge base
- Configurable file size limits

### ✅ Question Answering
- Semantic search using vector similarity
- Configurable top-k results
- Source attribution and scoring
- Context-aware responses

### ✅ Chat Completions
- RAG-enhanced chat completions
- Multi-agentic support
- Agent persona preservation
- OpenAI-compatible API

### ✅ System Monitoring
- Health check endpoints
- System statistics
- Vector store metrics
- Error handling and logging

## Technology Stack

- **Framework**: FastAPI
- **Vector Database**: Qdrant Cloud
- **Embeddings**: OpenAI text-embedding-ada-002
- **LLM**: OpenAI GPT-3.5-turbo
- **Document Processing**: LangChain
- **Configuration**: Environment variables
- **Testing**: pytest with comprehensive coverage

## Security & Configuration

- **SSL/TLS Support**: Configurable certificate handling
- **API Authentication**: OpenAI and Qdrant API keys
- **CORS Configuration**: Configurable cross-origin settings
- **Rate Limiting**: Built-in request timeout handling
- **Error Handling**: Comprehensive error responses

## Performance Features

- **Asynchronous Processing**: Non-blocking operations
- **Configurable Timeouts**: Request and retry limits
- **Vector Optimization**: Cosine similarity with configurable metrics
- **Memory Management**: Efficient document processing
- **Scalable Architecture**: Clean separation of concerns 