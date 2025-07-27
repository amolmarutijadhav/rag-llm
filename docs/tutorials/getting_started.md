# Getting Started Tutorial

## Welcome to RAG LLM API! 🚀

This tutorial will guide you through setting up and using the RAG LLM API for the first time. By the end of this tutorial, you'll be able to upload documents, ask questions, and get AI-powered answers.

## Prerequisites

Before starting, make sure you have:

- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **OpenAI API key** (get one at https://platform.openai.com/)
- **Qdrant Cloud account** (free tier available at https://cloud.qdrant.io/)

## Step 1: Setup

### 1.1 Clone the Repository

```bash
git clone https://github.com/your-username/rag-llm.git
cd rag-llm
```

### 1.2 Create Virtual Environment

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 1.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.4 Configure Environment

```bash
# Copy environment template
cp config/env.example .env

# Edit the .env file with your API keys
```

Edit the `.env` file with your API keys:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Qdrant Cloud Configuration
QDRANT_API_KEY=your-qdrant-api-key-here
VECTOR_COLLECTION_URL=https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io:6333/collections/documents
VECTOR_INSERT_API_URL=https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io:6333/collections/documents/points
VECTOR_SEARCH_API_URL=https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io:6333/collections/documents/points/search

# Application Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### 1.5 Start the Server

```bash
python scripts/run.py
```

You should see output like:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Step 2: Verify Installation

### 2.1 Check Health Endpoint

Open your browser or use curl to check if the API is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-05-01T12:00:00"
}
```

### 2.2 Access Interactive Documentation

Open your browser and go to:
```
http://localhost:8000/docs
```

This will show you the interactive API documentation where you can test endpoints directly.

## Step 3: Your First Document

### 3.1 Create a Test Document

Create a simple text file to test with:

```bash
echo "Python is a high-level programming language created by Guido van Rossum in 1991. It is known for its simplicity and readability." > test_document.txt
```

### 3.2 Upload the Document

Using curl:
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@test_document.txt"
```

Or using the interactive docs at `http://localhost:8000/docs`:
1. Go to the `/documents/upload` endpoint
2. Click "Try it out"
3. Choose your file
4. Click "Execute"

Expected response:
```json
{
  "success": true,
  "message": "Document 'test_document.txt' added successfully",
  "chunks_processed": 1
}
```

## Step 4: Ask Your First Question

### 4.1 Ask a Question

Using curl:
```bash
curl -X POST "http://localhost:8000/questions/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "Who created Python?",
       "top_k": 3
     }'
```

Or using the interactive docs:
1. Go to the `/questions/ask` endpoint
2. Click "Try it out"
3. Enter your question
4. Click "Execute"

Expected response:
```json
{
  "success": true,
  "answer": "Python was created by Guido van Rossum in 1991.",
  "sources": [
    {
      "content": "Python is a high-level programming language created by Guido van Rossum in 1991. It is known for its simplicity and readability.",
      "metadata": {"source": "test_document.txt", "chunk_index": 0},
      "score": 0.9876543
    }
  ],
  "context_used": "Python is a high-level programming language created by Guido van Rossum in 1991. It is known for its simplicity and readability."
}
```

## Step 5: Add Text Content

### 5.1 Add Raw Text

You can also add text directly without uploading a file:

```bash
curl -X POST "http://localhost:8000/documents/add-text" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
       "source_name": "ml_info"
     }'
```

### 5.2 Ask About the New Content

```bash
curl -X POST "http://localhost:8000/questions/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What is machine learning?",
       "top_k": 3
     }'
```

## Step 6: Chat Completions

### 6.1 Try RAG-Enhanced Chat

The API also supports RAG-enhanced chat completions:

```bash
curl -X POST "http://localhost:8000/chat/completions" \
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

## Step 7: Check System Status

### 7.1 Get System Statistics

```bash
curl -X GET "http://localhost:8000/stats"
```

This will show you:
- Total documents in the vector store
- Supported file formats
- Processing configuration

## Common Tasks

### Upload Different File Types

The API supports multiple file formats:

#### PDF Files
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@document.pdf"
```

#### Word Documents
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@document.docx"
```

#### Text Files
```bash
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@document.txt"
```

### Clear Knowledge Base

To start fresh:
```bash
curl -X DELETE "http://localhost:8000/documents/clear"
```

### Get Better Answers

For more detailed answers, increase the `top_k` parameter:
```bash
curl -X POST "http://localhost:8000/questions/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "What is the main topic?",
       "top_k": 5
     }'
```

## Troubleshooting

### Common Issues

#### 1. API Key Errors
**Problem**: `"detail": "OPENAI_API_KEY is required"`
**Solution**: Check your `.env` file and ensure the API key is set correctly.

#### 2. Qdrant Connection Issues
**Problem**: `"detail": "Connection to Qdrant failed"`
**Solution**: Verify your Qdrant Cloud configuration and API key.

#### 3. File Upload Errors
**Problem**: `"detail": "Unsupported file format"`
**Solution**: Ensure your file is one of: `.pdf`, `.txt`, `.docx`

#### 4. Server Not Starting
**Problem**: Port 8000 already in use
**Solution**: Change the port in your `.env` file or kill the process using port 8000.

### Debug Mode

Enable debug mode for more detailed error messages:
```bash
export DEBUG=True
python scripts/run.py
```

## Next Steps

### 1. Explore the API
- Try different types of questions
- Upload various document formats
- Experiment with the chat completions

### 2. Read the Documentation
- Check out the full API documentation
- Read the architecture guide
- Review the deployment guide

### 3. Build Your Application
- Integrate the API into your applications
- Build a web interface
- Create automated workflows

### 4. Contribute
- Report bugs and suggest features
- Contribute code improvements
- Help improve documentation

## Support

If you run into issues:

1. **Check the logs**: Look at the console output for error messages
2. **Verify configuration**: Ensure all environment variables are set correctly
3. **Test connectivity**: Verify your internet connection and API access
4. **Ask for help**: Open an issue on GitHub or join discussions

## Congratulations! 🎉

You've successfully set up and used the RAG LLM API! You can now:
- ✅ Upload and process documents
- ✅ Ask questions and get AI-powered answers
- ✅ Use RAG-enhanced chat completions
- ✅ Manage your knowledge base

Happy building! 🚀 