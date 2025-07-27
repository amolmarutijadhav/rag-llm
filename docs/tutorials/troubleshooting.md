# Troubleshooting Guide

## Common Issues and Solutions

This guide helps you resolve common issues when using the RAG LLM API. If you don't find your issue here, please check the GitHub issues or create a new one.

## Setup Issues

### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solutions**:
```bash
# Make sure you're in the correct directory
cd rag-llm

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. API Key Configuration

**Problem**: `"detail": "OPENAI_API_KEY is required"`

**Solutions**:
```bash
# Check if environment variables are set
echo $OPENAI_API_KEY
echo $QDRANT_API_KEY

# Verify .env file exists and has correct values
cat .env

# Set environment variables manually
export OPENAI_API_KEY="sk-your-api-key"
export QDRANT_API_KEY="your-qdrant-key"
```

### 3. Qdrant Connection Issues

**Problem**: `"detail": "Connection to Qdrant failed"`

**Solutions**:
```bash
# Test Qdrant connection
curl -H "api-key: $QDRANT_API_KEY" \
     "$VECTOR_COLLECTION_URL"

# Check Qdrant Cloud status
# Visit https://cloud.qdrant.io/status

# Verify collection exists
curl -X GET "$VECTOR_COLLECTION_URL" \
     -H "api-key: $QDRANT_API_KEY"
```

## Runtime Issues

### 4. Port Already in Use

**Problem**: `OSError: [Errno 48] Address already in use`

**Solutions**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or change the port
export PORT=8001
python scripts/run.py
```

### 5. File Upload Errors

**Problem**: `"detail": "Unsupported file format"`

**Solutions**:
- Ensure file has supported extension: `.pdf`, `.txt`, `.docx`
- Check file is not corrupted
- Verify file size is under 10MB

**Problem**: `"detail": "File too large"`

**Solutions**:
```bash
# Check file size
ls -lh your_file.pdf

# Increase file size limit in .env
MAX_FILE_SIZE=20971520  # 20MB
```

### 6. Memory Issues

**Problem**: `MemoryError` or slow performance

**Solutions**:
```bash
# Check memory usage
free -h  # Linux
top       # macOS

# Reduce chunk size in .env
CHUNK_SIZE=500
CHUNK_OVERLAP=100

# Use smaller batch sizes
TOP_K_RESULTS=2
```

## API Issues

### 7. OpenAI API Errors

**Problem**: `"detail": "OpenAI API error"`

**Solutions**:
```bash
# Test OpenAI API directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Check API key format
# Should start with "sk-"

# Verify account has credits
# Visit https://platform.openai.com/account/usage
```

### 8. Rate Limiting

**Problem**: `"detail": "Rate limit exceeded"`

**Solutions**:
```bash
# Implement exponential backoff
# Add to your requests
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "rate limit" in str(e).lower():
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
                continue
            raise e
```

### 9. SSL Certificate Issues

**Problem**: `"detail": "SSL certificate verification failed"`

**Solutions**:
```bash
# Update certificate configuration
CERT_FILE_PATH=/path/to/certificate.cer
VERIFY_SSL=True
CERT_VERIFY_MODE=auto

# Or disable SSL verification (not recommended for production)
VERIFY_SSL=False
```

## Performance Issues

### 10. Slow Response Times

**Problem**: API responses are slow

**Solutions**:
```bash
# Optimize chunk size
CHUNK_SIZE=500  # Smaller chunks for faster processing

# Reduce top_k for faster search
TOP_K_RESULTS=2

# Use async requests
import asyncio
import aiohttp

async def make_requests():
    async with aiohttp.ClientSession() as session:
        # Make concurrent requests
        pass
```

### 11. High Memory Usage

**Problem**: Application uses too much memory

**Solutions**:
```bash
# Monitor memory usage
docker stats  # If using Docker
htop          # System monitor

# Optimize configuration
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=2

# Restart application periodically
# Add to crontab
0 */6 * * * /path/to/restart_script.sh
```

## Debugging

### 12. Enable Debug Mode

```bash
# Set debug environment variable
export DEBUG=True

# Run with verbose logging
python scripts/run.py

# Check logs
tail -f app.log
```

### 13. Test Individual Components

```python
# Test document loading
from app.infrastructure.document_processing.loader import DocumentLoader
loader = DocumentLoader()
text = loader.load_document("test.txt")
print(f"Loaded {len(text)} characters")

# Test embedding generation
from app.infrastructure.external.external_api_service import ExternalAPIService
api_service = ExternalAPIService()
embeddings = await api_service.call_openai_embeddings(["test"])
print(f"Generated {len(embeddings)} embeddings")

# Test vector search
from app.infrastructure.vector_store.vector_store import VectorStore
vector_store = VectorStore()
results = await vector_store.search("test query", top_k=3)
print(f"Found {len(results)} results")
```

### 14. Check Configuration

```python
# Verify all configuration values
from app.core.config import Config

print(f"OpenAI API Key: {'Set' if Config.OPENAI_API_KEY else 'Not Set'}")
print(f"Qdrant API Key: {'Set' if Config.QDRANT_API_KEY else 'Not Set'}")
print(f"Debug Mode: {Config.DEBUG}")
print(f"Chunk Size: {Config.CHUNK_SIZE}")
print(f"Top K Results: {Config.TOP_K_RESULTS}")
```

## Network Issues

### 15. Connection Timeouts

**Problem**: `"detail": "Connection timeout"`

**Solutions**:
```bash
# Increase timeout values
REQUEST_TIMEOUT=60
MAX_RETRIES=5

# Test network connectivity
ping api.openai.com
ping your-qdrant-cluster.qdrant.io

# Check firewall settings
# Ensure ports 443 and 6333 are open
```

### 16. DNS Resolution Issues

**Problem**: `"detail": "Name resolution failed"`

**Solutions**:
```bash
# Test DNS resolution
nslookup api.openai.com
nslookup your-qdrant-cluster.qdrant.io

# Use IP addresses directly (temporary)
# Update .env with IP addresses
```

## Production Issues

### 17. Docker Issues

**Problem**: Container won't start

**Solutions**:
```bash
# Check Docker logs
docker logs rag-api

# Verify Dockerfile
docker build -t rag-api .

# Check resource limits
docker run --memory=4g rag-api

# Test container health
docker exec rag-api curl http://localhost:8000/health
```

### 18. Load Balancer Issues

**Problem**: Health checks failing

**Solutions**:
```bash
# Verify health endpoint
curl http://your-api.com/health

# Check load balancer configuration
# Ensure health check path is correct: /health

# Test from load balancer perspective
curl -H "Host: your-api.com" http://localhost/health
```

### 19. SSL Certificate Issues

**Problem**: HTTPS not working

**Solutions**:
```bash
# Verify certificate
openssl x509 -in cert.pem -text -noout

# Test SSL connection
openssl s_client -connect your-api.com:443

# Check certificate expiration
echo | openssl s_client -servername your-api.com -connect your-api.com:443 2>/dev/null | openssl x509 -noout -dates
```

## Monitoring and Logging

### 20. Set Up Monitoring

```python
# Add custom logging
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Monitor key metrics
from app.domain.services.rag_service import RAGService

rag_service = RAGService()
stats = rag_service.get_stats()
print(f"Total documents: {stats['vector_store']['total_documents']}")
```

### 21. Error Tracking

```python
# Add error tracking
import traceback

try:
    # Your code here
    pass
except Exception as e:
    logging.error(f"Error: {str(e)}")
    logging.error(f"Traceback: {traceback.format_exc()}")
    # Send to error tracking service
```

## Getting Help

### 22. Collect Debug Information

```bash
# System information
uname -a
python --version
pip list

# Configuration
cat .env

# Logs
tail -n 100 app.log

# Network connectivity
curl -v https://api.openai.com/v1/models
curl -v "$VECTOR_COLLECTION_URL"
```

### 23. Report Issues

When reporting issues, include:

1. **Error message**: Exact error text
2. **Steps to reproduce**: Detailed steps
3. **Environment**: OS, Python version, dependencies
4. **Configuration**: Relevant .env settings (without API keys)
5. **Logs**: Relevant log entries
6. **Expected vs actual behavior**: What you expected vs what happened

### 24. Community Support

- **GitHub Issues**: Report bugs and feature requests
- **GitHub Discussions**: Ask questions and share solutions
- **Documentation**: Check `/docs` directory for guides
- **Examples**: See `/docs/api/examples.md` for usage examples

## Prevention

### 25. Best Practices

1. **Regular Updates**: Keep dependencies updated
2. **Monitoring**: Set up health checks and monitoring
3. **Backups**: Regular backups of configuration and data
4. **Testing**: Test changes in staging before production
5. **Documentation**: Keep documentation updated
6. **Security**: Regular security audits and updates

### 26. Maintenance Checklist

- [ ] Monitor application logs daily
- [ ] Check API usage and costs weekly
- [ ] Update dependencies monthly
- [ ] Review security settings quarterly
- [ ] Test disaster recovery procedures
- [ ] Update documentation as needed

---

If you continue to have issues after trying these solutions, please:

1. Check the GitHub issues for similar problems
2. Create a new issue with detailed information
3. Join the community discussions for help
4. Consider contributing a fix or improvement

Happy troubleshooting! 🔧 