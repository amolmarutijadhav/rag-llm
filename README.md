# RAG LLM API - Phase 1 MVP

A simple yet powerful Retrieval-Augmented Generation (RAG) API built with FastAPI, LangChain, and ChromaDB.

## 🚀 Features

- **Document Upload**: Support for PDF, TXT, and DOCX files
- **Text Input**: Add raw text to the knowledge base
- **Question Answering**: Ask questions and get AI-generated answers
- **Vector Search**: Semantic search using ChromaDB
- **RESTful API**: Clean, documented API endpoints
- **Auto-generated Docs**: Interactive API documentation

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd rag-llm
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

## 🏃‍♂️ Quick Start

1. **Start the server**
   ```bash
   python run.py
   ```

2. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## 📚 API Endpoints

### Health Check
- `GET /` - Health check and API info
- `GET /health` - Simple health check

### Document Management
- `POST /upload` - Upload and process documents
- `POST /add-text` - Add raw text to knowledge base
- `DELETE /clear` - Clear all documents

### Question Answering
- `POST /ask` - Ask questions and get answers

### System Info
- `GET /stats` - Get system statistics

## 🔧 Configuration

Edit `src/config.py` or set environment variables:

```python
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here

# Vector Database
CHROMA_DB_PATH=./chroma_db

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Document Processing
MAX_FILE_SIZE=10485760  # 10MB
SUPPORTED_FORMATS=[".pdf", ".txt", ".docx"]

# RAG Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=3
```

## 📖 Usage Examples

### 1. Upload a Document
```bash
curl -X POST "http://localhost:8000/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_document.pdf"
```

### 2. Add Text
```bash
curl -X POST "http://localhost:8000/add-text" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your text content here", "source_name": "my_text"}'
```

### 3. Ask a Question
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is the main topic?", "top_k": 3}'
```

### 4. Get Statistics
```bash
curl -X GET "http://localhost:8000/stats"
```

## 🏗️ Project Structure

```
rag-llm/
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── document_loader.py # Document processing
│   ├── vector_store.py    # Vector database operations
│   ├── rag_service.py     # Main RAG orchestration
│   ├── models.py          # Pydantic models
│   └── main.py           # FastAPI application
├── requirements.txt       # Python dependencies
├── env.example           # Environment template
├── run.py               # Application runner
└── README.md            # This file
```

## 🔍 How It Works

1. **Document Processing**: Documents are loaded, chunked, and embedded
2. **Vector Storage**: Chunks are stored in ChromaDB with embeddings
3. **Question Processing**: User questions are embedded and searched
4. **Context Retrieval**: Most relevant document chunks are retrieved
5. **Answer Generation**: LLM generates answers using retrieved context

## 🧪 Testing

The API includes comprehensive error handling and validation. Test the endpoints using the interactive documentation at `/docs`.

## 🔄 Next Phases

This is Phase 1 MVP. Future phases will include:
- **Phase 2**: Enhanced document processing, better chunking strategies
- **Phase 3**: Advanced RAG techniques, hybrid search
- **Phase 4**: Microservices architecture, Qdrant vector database
- **Phase 5**: Production features, monitoring, scaling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Ensure your OpenAI API key is valid
4. Verify document formats are supported 