# Configuration Externalization Guide

This document provides a comprehensive overview of the configuration system for the RAG LLM API, including environment variables, provider configuration, and best practices with the new **Plugin Architecture**.

## 🔧 Configuration Overview

The RAG LLM API uses a comprehensive externalized configuration system that supports the plugin architecture, allowing you to configure different provider types and their specific settings through environment variables.

### Configuration Philosophy

1. **Externalization**: All configuration is externalized to environment variables
2. **Provider Flexibility**: Support for multiple provider types per service
3. **Environment Separation**: Easy switching between development, staging, and production
4. **Security**: Sensitive data kept out of code
5. **Maintainability**: Centralized configuration management

## 🔌 Provider Configuration

### Provider Type Configuration

The plugin architecture allows you to configure different provider types for each service:

```bash
# Provider Type Configuration
PROVIDER_EMBEDDING_TYPE=openai      # or "inhouse", "cohere"
PROVIDER_LLM_TYPE=openai           # or "inhouse", "anthropic"
PROVIDER_VECTOR_STORE_TYPE=qdrant  # or "inhouse", "pinecone"
```

### Provider-Specific Configuration

Each provider type has its own configuration settings:

#### OpenAI Provider Configuration

```bash
# OpenAI Provider Settings
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
```

#### Qdrant Provider Configuration

```bash
# Qdrant Provider Settings
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_COLLECTION_NAME=rag-llm-dev
VECTOR_SIZE=1536
VECTOR_DISTANCE_METRIC=Cosine
```

#### In-House Provider Configuration

```bash
# In-House Provider Settings
INHOUSE_EMBEDDING_API_URL=https://your-inhouse-embedding-api.com
INHOUSE_LLM_API_URL=https://your-inhouse-llm-api.com
INHOUSE_VECTOR_STORE_URL=https://your-inhouse-vector-store.com
INHOUSE_API_KEY=your_inhouse_key
INHOUSE_EMBEDDING_MODEL=your-embedding-model
INHOUSE_LLM_MODEL=your-llm-model
```

## 🏗️ Configuration Architecture

### Configuration Class Structure

The `Config` class provides methods to get provider-specific configurations:

```python
class Config:
    @classmethod
    def get_embedding_provider_config(cls) -> Dict[str, Any]:
        """Get embedding provider configuration based on provider type"""
        provider_type = os.getenv("PROVIDER_EMBEDDING_TYPE", "openai")
        
        if provider_type == "openai":
            return {
                "type": "openai",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "api_url": os.getenv("OPENAI_API_URL", "https://api.openai.com/v1"),
                "model": os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
            }
        elif provider_type == "inhouse":
            return {
                "type": "inhouse",
                "api_url": os.getenv("INHOUSE_EMBEDDING_API_URL"),
                "api_key": os.getenv("INHOUSE_API_KEY"),
                "model": os.getenv("INHOUSE_EMBEDDING_MODEL")
            }
        else:
            raise ValueError(f"Unsupported embedding provider type: {provider_type}")
    
    @classmethod
    def get_llm_provider_config(cls) -> Dict[str, Any]:
        """Get LLM provider configuration based on provider type"""
        provider_type = os.getenv("PROVIDER_LLM_TYPE", "openai")
        
        if provider_type == "openai":
            return {
                "type": "openai",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "api_url": os.getenv("OPENAI_API_URL", "https://api.openai.com/v1"),
                "model": os.getenv("CHAT_MODEL", "gpt-3.5-turbo"),
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
                "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "1000"))
            }
        elif provider_type == "inhouse":
            return {
                "type": "inhouse",
                "api_url": os.getenv("INHOUSE_LLM_API_URL"),
                "api_key": os.getenv("INHOUSE_API_KEY"),
                "model": os.getenv("INHOUSE_LLM_MODEL"),
                "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
                "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "1000"))
            }
        else:
            raise ValueError(f"Unsupported LLM provider type: {provider_type}")
    
    @classmethod
    def get_vector_store_provider_config(cls) -> Dict[str, Any]:
        """Get vector store provider configuration based on provider type"""
        provider_type = os.getenv("PROVIDER_VECTOR_STORE_TYPE", "qdrant")
        
        if provider_type == "qdrant":
            return {
                "type": "qdrant",
                "api_key": os.getenv("QDRANT_API_KEY"),
                "base_url": os.getenv("QDRANT_URL"),
                "collection_name": os.getenv("QDRANT_COLLECTION_NAME", "rag-llm-dev"),
                "vector_size": int(os.getenv("VECTOR_SIZE", "1536")),
                "distance_metric": os.getenv("VECTOR_DISTANCE_METRIC", "Cosine")
            }
        elif provider_type == "inhouse":
            return {
                "type": "inhouse",
                "api_url": os.getenv("INHOUSE_VECTOR_STORE_URL"),
                "api_key": os.getenv("INHOUSE_API_KEY"),
                "collection_name": os.getenv("QDRANT_COLLECTION_NAME", "rag-llm-dev"),
                "vector_size": int(os.getenv("VECTOR_SIZE", "1536"))
            }
        else:
            raise ValueError(f"Unsupported vector store provider type: {provider_type}")
```

## 📋 Complete Environment Variables

### Core Configuration

```bash
# Application Configuration
API_TITLE=RAG LLM API
API_DESCRIPTION=A simple RAG (Retrieval-Augmented Generation) API for document Q&A
API_VERSION=1.0.0
DEBUG=true
HOST=0.0.0.0
PORT=8000

# CORS Configuration
CORS_ALLOW_ORIGINS=*
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# HTTP Configuration
REQUEST_TIMEOUT=30
MAX_RETRIES=3
```

### Provider Configuration

```bash
# Provider Type Configuration
PROVIDER_EMBEDDING_TYPE=openai      # or "inhouse", "cohere"
PROVIDER_LLM_TYPE=openai           # or "inhouse", "anthropic"
PROVIDER_VECTOR_STORE_TYPE=qdrant  # or "inhouse", "pinecone"

# OpenAI Provider Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_URL=https://api.openai.com/v1
EMBEDDING_MODEL=text-embedding-ada-002
CHAT_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# Qdrant Provider Configuration
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_COLLECTION_NAME=rag-llm-dev
VECTOR_SIZE=1536
VECTOR_DISTANCE_METRIC=Cosine

# In-House Provider Configuration (optional)
INHOUSE_EMBEDDING_API_URL=https://your-inhouse-embedding-api.com
INHOUSE_LLM_API_URL=https://your-inhouse-llm-api.com
INHOUSE_VECTOR_STORE_URL=https://your-inhouse-vector-store.com
INHOUSE_API_KEY=your_inhouse_key
INHOUSE_EMBEDDING_MODEL=your-embedding-model
INHOUSE_LLM_MODEL=your-llm-model
```

### OCR Configuration

```bash
# OCR Configuration
OCR_CONFIDENCE_THRESHOLD=60
```

### Security Configuration

```bash
# Security Configuration
CLEAR_ENDPOINT_API_KEY=your_secure_api_key
CLEAR_ENDPOINT_CONFIRMATION_TOKEN=your_confirmation_token
CLEAR_ENDPOINT_RATE_LIMIT_PER_HOUR=10
ENABLE_CLEAR_ENDPOINT_AUDIT_LOGGING=true
```

## 🔄 Configuration Management

### Environment-Specific Configuration

#### Development Environment

```bash
# .env.development
DEBUG=true
PROVIDER_EMBEDDING_TYPE=openai
PROVIDER_LLM_TYPE=openai
PROVIDER_VECTOR_STORE_TYPE=qdrant
OPENAI_API_KEY=your_dev_openai_key
QDRANT_API_KEY=your_dev_qdrant_key
```

#### Staging Environment

```bash
# .env.staging
DEBUG=false
PROVIDER_EMBEDDING_TYPE=openai
PROVIDER_LLM_TYPE=openai
PROVIDER_VECTOR_STORE_TYPE=qdrant
OPENAI_API_KEY=your_staging_openai_key
QDRANT_API_KEY=your_staging_qdrant_key
```

#### Production Environment

```bash
# .env.production
DEBUG=false
PROVIDER_EMBEDDING_TYPE=inhouse
PROVIDER_LLM_TYPE=inhouse
PROVIDER_VECTOR_STORE_TYPE=inhouse
INHOUSE_API_KEY=your_production_key
INHOUSE_EMBEDDING_API_URL=https://prod-embedding-api.company.com
INHOUSE_LLM_API_URL=https://prod-llm-api.company.com
INHOUSE_VECTOR_STORE_URL=https://prod-vector-store.company.com
```

### Configuration Validation

The configuration system includes validation to ensure required settings are present:

```python
def validate_provider_config(config: Dict[str, Any], provider_type: str) -> None:
    """Validate provider configuration"""
    required_fields = {
        "openai": ["api_key"],
        "qdrant": ["api_key", "base_url"],
        "inhouse": ["api_url", "api_key"]
    }
    
    if provider_type not in required_fields:
        raise ValueError(f"Unknown provider type: {provider_type}")
    
    missing_fields = []
    for field in required_fields[provider_type]:
        if not config.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required fields for {provider_type}: {missing_fields}")
```

## 🚀 Configuration Best Practices

### 1. Environment Separation

- **Development**: Use development API keys and endpoints
- **Staging**: Use staging environment with production-like settings
- **Production**: Use production endpoints and secure configuration

### 2. Security Considerations

- **API Keys**: Never commit API keys to version control
- **Environment Files**: Use `.env` files for local development
- **Secrets Management**: Use proper secrets management in production
- **Access Control**: Limit access to production configuration

### 3. Provider Switching

- **Gradual Migration**: Test new providers in staging first
- **Configuration Validation**: Validate configuration before switching
- **Fallback Strategy**: Have fallback providers configured
- **Monitoring**: Monitor provider performance after switching

### 4. Configuration Validation

```bash
# Validate configuration before starting
python -c "
from app.core.config import Config
try:
    Config.get_embedding_provider_config()
    Config.get_llm_provider_config()
    Config.get_vector_store_provider_config()
    print('✅ Configuration is valid')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    exit(1)
"
```

## 🔧 Configuration Examples

### Example 1: OpenAI + Qdrant (Default)

```bash
# .env
PROVIDER_EMBEDDING_TYPE=openai
PROVIDER_LLM_TYPE=openai
PROVIDER_VECTOR_STORE_TYPE=qdrant

OPENAI_API_KEY=sk-your-openai-key
QDRANT_API_KEY=your-qdrant-key
QDRANT_URL=https://your-cluster.qdrant.io
```

### Example 2: In-House Services

```bash
# .env
PROVIDER_EMBEDDING_TYPE=inhouse
PROVIDER_LLM_TYPE=inhouse
PROVIDER_VECTOR_STORE_TYPE=inhouse

INHOUSE_API_KEY=your-inhouse-key
INHOUSE_EMBEDDING_API_URL=https://embedding-api.company.com
INHOUSE_LLM_API_URL=https://llm-api.company.com
INHOUSE_VECTOR_STORE_URL=https://vector-store.company.com
```

### Example 3: Mixed Providers

```bash
# .env
PROVIDER_EMBEDDING_TYPE=openai
PROVIDER_LLM_TYPE=inhouse
PROVIDER_VECTOR_STORE_TYPE=qdrant

OPENAI_API_KEY=sk-your-openai-key
QDRANT_API_KEY=your-qdrant-key
QDRANT_URL=https://your-cluster.qdrant.io

INHOUSE_API_KEY=your-inhouse-key
INHOUSE_LLM_API_URL=https://llm-api.company.com
```

## 📊 Configuration Monitoring

### Configuration Health Checks

```python
def check_configuration_health() -> Dict[str, Any]:
    """Check configuration health and provider availability"""
    health_status = {
        "configuration_valid": True,
        "providers": {},
        "errors": []
    }
    
    try:
        # Check embedding provider
        embedding_config = Config.get_embedding_provider_config()
        health_status["providers"]["embedding"] = {
            "type": embedding_config["type"],
            "configured": True
        }
    except Exception as e:
        health_status["configuration_valid"] = False
        health_status["errors"].append(f"Embedding provider: {e}")
    
    try:
        # Check LLM provider
        llm_config = Config.get_llm_provider_config()
        health_status["providers"]["llm"] = {
            "type": llm_config["type"],
            "configured": True
        }
    except Exception as e:
        health_status["configuration_valid"] = False
        health_status["errors"].append(f"LLM provider: {e}")
    
    try:
        # Check vector store provider
        vector_config = Config.get_vector_store_provider_config()
        health_status["providers"]["vector_store"] = {
            "type": vector_config["type"],
            "configured": True
        }
    except Exception as e:
        health_status["configuration_valid"] = False
        health_status["errors"].append(f"Vector store provider: {e}")
    
    return health_status
```

## 🔮 Future Configuration Enhancements

### Planned Features

1. **Configuration Hot Reloading**: Reload configuration without restart
2. **Configuration Validation**: Enhanced validation with schemas
3. **Configuration Encryption**: Encrypt sensitive configuration values
4. **Configuration Templates**: Pre-built configuration templates
5. **Configuration Migration**: Tools for migrating between configurations

### Configuration Schema

```python
# Future configuration schema
from pydantic import BaseSettings

class ProviderConfig(BaseSettings):
    type: str
    api_key: str
    api_url: str
    model: str = "default"
    
    class Config:
        env_file = ".env"

class AppConfig(BaseSettings):
    embedding_provider: ProviderConfig
    llm_provider: ProviderConfig
    vector_store_provider: ProviderConfig
    
    class Config:
        env_file = ".env"
```

## 📚 Related Documentation

- [Plugin Architecture Guide](PLUGIN_ARCHITECTURE.md) - Provider system documentation
- [Architecture Guide](architecture.md) - System architecture overview
- [API Documentation](../api/overview.md) - API configuration examples
- [Deployment Guide](../deployment/DOCKER_DEPLOYMENT_GUIDE.md) - Deployment configuration 