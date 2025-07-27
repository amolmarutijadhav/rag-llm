# Development Setup Guide

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 1GB free space

### Required Accounts
- **OpenAI Account**: For API access (https://platform.openai.com/)
- **Qdrant Cloud Account**: For vector database (https://cloud.qdrant.io/)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd rag-llm
```

### 2. Create Virtual Environment

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

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

#### Copy Environment Template
```bash
cp config/env.example .env
```

#### Configure Environment Variables
Edit `.env` file with your API keys and configuration:

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

### 5. Qdrant Cloud Setup

#### Create Qdrant Cloud Account
1. Visit https://cloud.qdrant.io/
2. Sign up for a free account
3. Create a new cluster
4. Note your cluster URL and API key

#### Create Collection
```bash
# Using Qdrant Cloud API
curl -X PUT "https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io:6333/collections/documents" \
     -H "api-key: your-qdrant-api-key" \
     -H "Content-Type: application/json" \
     -d '{
       "vectors": {
         "size": 1536,
         "distance": "Cosine"
       }
     }'
```

### 6. OpenAI API Setup

#### Get API Key
1. Visit https://platform.openai.com/
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-`)

#### Verify API Access
```bash
curl -H "Authorization: Bearer sk-your-api-key" \
     https://api.openai.com/v1/models
```

## Development Environment

### Project Structure
```
rag-llm/
├── app/                    # Main application code
│   ├── api/               # API routes and middleware
│   ├── core/              # Configuration and utilities
│   ├── domain/            # Business logic and models
│   ├── infrastructure/    # External service integrations
│   └── utils/             # Helper functions
├── tests/                 # Test suite
├── docs/                  # Documentation
├── config/                # Configuration files
└── scripts/               # Utility scripts
```

### Running the Application

#### Development Server
```bash
python scripts/run.py
```

#### Alternative Methods
```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Using FastAPI CLI
fastapi run app.main:app --reload
```

### Accessing the API

#### API Endpoints
- **API Base URL**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

#### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

## Development Tools

### Code Quality

#### Install Development Dependencies
```bash
pip install black flake8 mypy pytest pytest-asyncio
```

#### Code Formatting
```bash
# Format code with Black
black app/ tests/

# Check code style with Flake8
flake8 app/ tests/

# Type checking with MyPy
mypy app/
```

### Testing

#### Run All Tests
```bash
python scripts/run_tests.py
```

#### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# End-to-end tests only
pytest tests/e2e/
```

#### Run Tests with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Debugging

#### Enable Debug Mode
```bash
export DEBUG=True
python scripts/run.py
```

#### Logging Configuration
```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Configuration Options

### Environment Variables Reference

#### API Configuration
```bash
# OpenAI
OPENAI_API_KEY=sk-your-api-key
EMBEDDING_API_URL=https://api.openai.com/v1/embeddings
LLM_API_URL=https://api.openai.com/v1/chat/completions

# Qdrant
QDRANT_API_KEY=your-qdrant-api-key
VECTOR_COLLECTION_URL=https://your-cluster.qdrant.io:6333/collections/documents
VECTOR_INSERT_API_URL=https://your-cluster.qdrant.io:6333/collections/documents/points
VECTOR_SEARCH_API_URL=https://your-cluster.qdrant.io:6333/collections/documents/points/search
```

#### Application Settings
```bash
# Server Configuration
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Document Processing
MAX_FILE_SIZE=10485760  # 10MB
SUPPORTED_FORMATS=[".pdf", ".txt", ".docx"]
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# RAG Configuration
TOP_K_RESULTS=3
RAG_PROMPT_TEMPLATE="You are a helpful AI assistant..."
```

#### Model Configuration
```bash
# AI Models
EMBEDDING_MODEL=text-embedding-ada-002
LLM_MODEL=gpt-3.5-turbo
VECTOR_SIZE=1536
VECTOR_DISTANCE_METRIC=Cosine

# LLM Parameters
LLM_TEMPERATURE=0.1
LLM_MAX_TOKENS=1000
```

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

#### 2. API Key Errors
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $QDRANT_API_KEY

# Verify API keys are valid
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

#### 3. Qdrant Connection Issues
```bash
# Test Qdrant connection
curl -H "api-key: $QDRANT_API_KEY" \
     "$VECTOR_COLLECTION_URL"
```

#### 4. Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>
```

### Debug Mode

#### Enable Verbose Logging
```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
python scripts/run.py
```

#### Check Configuration
```python
from app.core.config import Config

print(f"OpenAI API Key: {'Set' if Config.OPENAI_API_KEY else 'Not Set'}")
print(f"Qdrant API Key: {'Set' if Config.QDRANT_API_KEY else 'Not Set'}")
print(f"Debug Mode: {Config.DEBUG}")
```

## Next Steps

### 1. Test the Setup
```bash
# Run health check
curl http://localhost:8000/health

# Upload a test document
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@test_document.txt"

# Ask a question
curl -X POST "http://localhost:8000/questions/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is this about?"}'
```

### 2. Explore the API
- Visit http://localhost:8000/docs for interactive documentation
- Try the example requests in the documentation
- Test different file formats and question types

### 3. Start Development
- Review the project structure
- Check out the test examples
- Read the contributing guidelines
- Join the development community

## Support

### Getting Help
- **Documentation**: Check the `/docs` directory
- **Issues**: Report bugs on GitHub
- **Discussions**: Join community discussions
- **Examples**: See `/docs/api/examples.md`

### Useful Commands
```bash
# Quick start
python scripts/run.py

# Run tests
python scripts/run_tests.py

# Format code
black app/ tests/

# Check health
curl http://localhost:8000/health
``` 