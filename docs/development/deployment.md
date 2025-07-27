# Deployment Guide

## Overview

This guide covers deploying the RAG LLM API to production environments, including Docker containerization, cloud deployment, and monitoring setup.

## Prerequisites

### Production Requirements
- **Python**: 3.8 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: At least 500MB free space
- **Network**: Stable internet connection for external APIs

### Required Services
- **OpenAI API**: For embeddings and chat completions
- **Qdrant Cloud**: For vector database storage
- **SSL Certificate**: For HTTPS in production

## Docker Deployment

### 1. Dockerfile

```dockerfile
# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  rag-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_API_KEY=${QDRANT_API_KEY}
      - VECTOR_COLLECTION_URL=${VECTOR_COLLECTION_URL}
      - VECTOR_INSERT_API_URL=${VECTOR_INSERT_API_URL}
      - VECTOR_SEARCH_API_URL=${VECTOR_SEARCH_API_URL}
      - DEBUG=False
      - HOST=0.0.0.0
      - PORT=8000
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - rag-api
    restart: unless-stopped
```

### 3. Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream rag_api {
        server rag-api:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        location / {
            proxy_pass http://rag_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check endpoint
        location /health {
            proxy_pass http://rag_api/health;
            access_log off;
        }
    }
}
```

### 4. Environment Variables

```bash
# .env.production
OPENAI_API_KEY=sk-your-production-api-key
QDRANT_API_KEY=your-production-qdrant-key
VECTOR_COLLECTION_URL=https://your-cluster.qdrant.io:6333/collections/documents
VECTOR_INSERT_API_URL=https://your-cluster.qdrant.io:6333/collections/documents/points
VECTOR_SEARCH_API_URL=https://your-cluster.qdrant.io:6333/collections/documents/points/search

# Production settings
DEBUG=False
HOST=0.0.0.0
PORT=8000

# Security settings
CORS_ALLOW_ORIGINS=https://your-domain.com,https://app.your-domain.com
CORS_ALLOW_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,Authorization

# Performance settings
REQUEST_TIMEOUT=60
MAX_RETRIES=5
```

## Cloud Deployment

### AWS Deployment

#### 1. EC2 Deployment

```bash
# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t3.medium \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx \
    --subnet-id subnet-xxxxxxxxx \
    --user-data file://user-data.sh
```

#### 2. User Data Script

```bash
#!/bin/bash
# user-data.sh

# Update system
yum update -y

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/your-username/rag-llm.git
cd rag-llm

# Create environment file
cat > .env << EOF
OPENAI_API_KEY=${OPENAI_API_KEY}
QDRANT_API_KEY=${QDRANT_API_KEY}
VECTOR_COLLECTION_URL=${VECTOR_COLLECTION_URL}
VECTOR_INSERT_API_URL=${VECTOR_INSERT_API_URL}
VECTOR_SEARCH_API_URL=${VECTOR_SEARCH_API_URL}
DEBUG=False
EOF

# Start application
docker-compose up -d
```

#### 3. Application Load Balancer

```yaml
# alb.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'RAG LLM API Load Balancer'

Parameters:
  VpcId:
    Type: AWS::EC2::VPC::Id
  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>

Resources:
  ALB:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Type: application
      Scheme: internet-facing
      Subnets: !Ref SubnetIds
      SecurityGroups:
        - !Ref ALBSecurityGroup

  ALBSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: ALB Security Group
      VpcId: !Ref VpcId
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0

  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      VpcId: !Ref VpcId
      Port: 8000
      Protocol: HTTP
      HealthCheckPath: /health
      HealthCheckIntervalSeconds: 30
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 3

  Listener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      LoadBalancerArn: !Ref ALB
      Port: 80
      Protocol: HTTP
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup
```

### Google Cloud Platform

#### 1. Cloud Run Deployment

```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: rag-llm-api
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containers:
      - image: gcr.io/your-project/rag-llm-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: rag-api-secrets
              key: openai-api-key
        - name: QDRANT_API_KEY
          valueFrom:
            secretKeyRef:
              name: rag-api-secrets
              key: qdrant-api-key
        - name: DEBUG
          value: "False"
```

#### 2. Deployment Commands

```bash
# Build and push image
docker build -t gcr.io/your-project/rag-llm-api .
docker push gcr.io/your-project/rag-llm-api

# Deploy to Cloud Run
gcloud run deploy rag-llm-api \
    --image gcr.io/your-project/rag-llm-api \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars DEBUG=False
```

### Azure Deployment

#### 1. Container Instances

```yaml
# azure-container-instance.yaml
apiVersion: 2019-12-01
location: eastus
name: rag-llm-api
properties:
  containers:
  - name: rag-api
    properties:
      image: your-registry.azurecr.io/rag-llm-api:latest
      ports:
      - port: 8000
      environmentVariables:
      - name: OPENAI_API_KEY
        value: "your-openai-api-key"
      - name: QDRANT_API_KEY
        value: "your-qdrant-api-key"
      - name: DEBUG
        value: "False"
      resources:
        requests:
          memoryInGB: 2
          cpu: 1
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: tcp
      port: 8000
```

## Monitoring & Observability

### 1. Health Checks

```python
# Enhanced health check
@router.get("/health")
async def health_check():
    """Comprehensive health check with external service status."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {}
    }
    
    # Check OpenAI API
    try:
        response = await api_service.call_openai_embeddings(["test"])
        health_status["services"]["openai"] = "healthy"
    except Exception as e:
        health_status["services"]["openai"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Qdrant API
    try:
        stats = await vector_store.get_stats()
        health_status["services"]["qdrant"] = "healthy"
    except Exception as e:
        health_status["services"]["qdrant"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status
```

### 2. Metrics Collection

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
REQUEST_COUNT = Counter('rag_api_requests_total', 'Total requests', ['endpoint', 'method'])
REQUEST_DURATION = Histogram('rag_api_request_duration_seconds', 'Request duration', ['endpoint'])
ACTIVE_REQUESTS = Gauge('rag_api_active_requests', 'Active requests')
DOCUMENT_COUNT = Gauge('rag_api_documents_total', 'Total documents in vector store')

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    ACTIVE_REQUESTS.inc()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        endpoint=request.url.path,
        method=request.method
    ).inc()
    REQUEST_DURATION.labels(endpoint=request.url.path).observe(duration)
    ACTIVE_REQUESTS.dec()
    
    return response
```

### 3. Logging Configuration

```python
# logging_config.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
```

## Security Configuration

### 1. SSL/TLS Setup

```bash
# Generate SSL certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Configure SSL in application
CERT_FILE_PATH=/path/to/cert.pem
VERIFY_SSL=True
CERT_VERIFY_MODE=verify
```

### 2. Security Headers

```python
# security_middleware.py
from fastapi import Request
from fastapi.responses import Response

@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response
```

### 3. Rate Limiting

```python
# rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/questions/ask")
@limiter.limit("10/minute")
async def ask_question(request: Request, question_request: QuestionRequest):
    # Implementation
    pass
```

## Performance Optimization

### 1. Connection Pooling

```python
# connection_pool.py
import httpx
from app.core.config import Config

# Create connection pool
async def get_http_client():
    return httpx.AsyncClient(
        timeout=httpx.Timeout(Config.REQUEST_TIMEOUT),
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    )
```

### 2. Caching Strategy

```python
# caching.py
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            
            return result
        return wrapper
    return decorator
```

## Backup & Recovery

### 1. Data Backup

```bash
#!/bin/bash
# backup.sh

# Backup environment variables
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# Backup logs
tar -czf logs_backup_$(date +%Y%m%d_%H%M%S).tar.gz logs/

# Backup configuration
cp -r config/ config_backup_$(date +%Y%m%d_%H%M%S)/
```

### 2. Recovery Procedures

```bash
#!/bin/bash
# recovery.sh

# Restore environment variables
cp .env.backup.$(date +%Y%m%d_%H%M%S) .env

# Restart services
docker-compose down
docker-compose up -d

# Verify health
curl -f http://localhost:8000/health || exit 1
```

## Troubleshooting

### Common Issues

#### 1. Memory Issues
```bash
# Check memory usage
docker stats

# Increase memory limits
docker run --memory=4g your-image
```

#### 2. Network Issues
```bash
# Test external API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Test Qdrant connectivity
curl -H "api-key: $QDRANT_API_KEY" \
     "$VECTOR_COLLECTION_URL"
```

#### 3. Performance Issues
```bash
# Monitor application performance
docker logs -f rag-api

# Check resource usage
htop
```

## Maintenance

### Regular Tasks

#### Daily
- Monitor application logs
- Check health endpoints
- Review error rates

#### Weekly
- Update dependencies
- Review performance metrics
- Backup configuration

#### Monthly
- Security updates
- Performance optimization
- Capacity planning

### Update Procedures

```bash
# Update application
git pull origin main
docker-compose build
docker-compose up -d

# Verify deployment
curl http://localhost:8000/health
```

---

This deployment guide provides comprehensive instructions for deploying the RAG LLM API to production environments. Follow the security best practices and monitor your deployment regularly. 