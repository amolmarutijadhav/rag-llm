# Plugin Architecture Documentation

## Overview

The RAG LLM API now supports a plugin architecture that allows you to easily switch between different external service providers without changing any code. This architecture uses the **Strategy Pattern + Factory Pattern** approach to provide maximum flexibility and extensibility.

## Architecture Components

### 1. Domain Interfaces (`app/domain/interfaces/`)

The foundation of the plugin architecture consists of abstract base classes that define contracts for all external services:

- **`EmbeddingProvider`**: Contract for embedding services
- **`VectorStoreProvider`**: Contract for vector database services  
- **`LLMProvider`**: Contract for language model services

### 2. Provider Implementations (`app/infrastructure/providers/`)

Concrete implementations of the interfaces:

- **OpenAI Providers**: `OpenAIEmbeddingProvider`, `OpenAILLMProvider`
- **Qdrant Provider**: `QdrantVectorStoreProvider`
- **In-House Providers**: `InhouseEmbeddingProvider`, `InhouseLLMProvider`, `InhouseVectorStoreProvider`

### 3. Factory Pattern (`ProviderFactory`)

The factory handles provider creation based on configuration:

```python
# Create providers based on configuration
embedding_provider = ProviderFactory.create_embedding_provider(config)
llm_provider = ProviderFactory.create_llm_provider(config)
vector_store_provider = ProviderFactory.create_vector_store_provider(config)
```

### 4. Service Locator (`ServiceLocator`)

Manages provider instances and provides dependency injection:

```python
# Get providers from service locator
embedding_provider = get_embedding_provider()
llm_provider = get_llm_provider()
vector_store_provider = get_vector_store_provider()
```

## Configuration

### Environment Variables

The plugin architecture is controlled through environment variables:

```bash
# Provider Types
PROVIDER_EMBEDDING_TYPE=openai      # or "inhouse", "cohere"
PROVIDER_LLM_TYPE=openai           # or "inhouse", "anthropic"
PROVIDER_VECTOR_STORE_TYPE=qdrant  # or "inhouse", "pinecone"

# Provider-specific configuration
OPENAI_API_KEY=your_openai_key
QDRANT_API_KEY=your_qdrant_key
EMBEDDING_API_URL=https://api.openai.com/v1/embeddings
LLM_API_URL=https://api.openai.com/v1/chat/completions
```

### Configuration Methods

The `Config` class provides methods to get provider-specific configurations:

```python
# Get provider configurations
embedding_config = Config.get_embedding_provider_config()
llm_config = Config.get_llm_provider_config()
vector_store_config = Config.get_vector_store_provider_config()
```

## Usage Examples

### 1. Using Default Providers (OpenAI + Qdrant)

```bash
# .env file
PROVIDER_EMBEDDING_TYPE=openai
PROVIDER_LLM_TYPE=openai
PROVIDER_VECTOR_STORE_TYPE=qdrant
OPENAI_API_KEY=your_openai_key
QDRANT_API_KEY=your_qdrant_key
```

### 2. Using In-House Providers

```bash
# .env file
PROVIDER_EMBEDDING_TYPE=inhouse
PROVIDER_LLM_TYPE=inhouse
PROVIDER_VECTOR_STORE_TYPE=inhouse
INHOUSE_EMBEDDING_API_URL=https://your-inhouse-embedding-api.com
INHOUSE_LLM_API_URL=https://your-inhouse-llm-api.com
INHOUSE_VECTOR_STORE_URL=https://your-inhouse-vector-store.com
INHOUSE_API_KEY=your_inhouse_key
```

### 3. Mixed Configuration (Qdrant + In-House LLM)

```bash
# .env file
PROVIDER_EMBEDDING_TYPE=openai
PROVIDER_LLM_TYPE=inhouse
PROVIDER_VECTOR_STORE_TYPE=qdrant
OPENAI_API_KEY=your_openai_key
QDRANT_API_KEY=your_qdrant_key
INHOUSE_LLM_API_URL=https://your-inhouse-llm-api.com
INHOUSE_API_KEY=your_inhouse_key
```

## Adding New Providers

### Step 1: Create Provider Implementation

Create a new provider class that implements the appropriate interface:

```python
# app/infrastructure/providers/cohere_provider.py
from app.domain.interfaces.providers import EmbeddingProvider
from .base_provider import BaseProvider

class CohereEmbeddingProvider(BaseProvider, EmbeddingProvider):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        # Implementation for Cohere API
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        return {"provider": "cohere", "api_url": self.api_url}
```

### Step 2: Update Factory

Add the new provider to the factory:

```python
# In app/infrastructure/providers/factory.py
from .cohere_provider import CohereEmbeddingProvider

class ProviderFactory:
    @staticmethod
    def create_embedding_provider(config: Dict[str, Any]) -> EmbeddingProvider:
        provider_type = config.get("type", "openai").lower()
        
        if provider_type == "cohere":
            return CohereEmbeddingProvider(config)
        # ... other providers
```

### Step 3: Update Configuration

Add configuration support for the new provider:

```python
# In app/core/config.py
@classmethod
def get_embedding_provider_config(cls) -> Dict[str, Any]:
    config = {
        "type": cls.PROVIDER_EMBEDDING_TYPE,
        # ... existing config
    }
    
    if cls.PROVIDER_EMBEDDING_TYPE == "cohere":
        config.update({
            "api_url": os.getenv("COHERE_API_URL"),
            "api_key": os.getenv("COHERE_API_KEY"),
        })
    
    return config
```

## Benefits

### 1. Zero Code Changes
Switch between providers by changing environment variables only.

### 2. Easy Testing
Mock providers for testing without affecting production code.

### 3. Enterprise Ready
Support for in-house services and custom implementations.

### 4. Type Safety
Strong typing with abstract base classes ensures contract compliance.

### 5. Extensibility
Easy to add new providers without modifying existing code.

## Migration Guide

### From Monolithic ExternalAPIService

The old `ExternalAPIService` class has been replaced with the plugin architecture. To migrate:

1. **Update imports**:
   ```python
   # Old
   from app.infrastructure.external.external_api_service import ExternalAPIService
   
   # New
   from app.infrastructure.providers import get_embedding_provider, get_llm_provider, get_vector_store_provider
   ```

2. **Update service usage**:
   ```python
   # Old
   api_service = ExternalAPIService()
   embeddings = await api_service.get_embeddings(texts)
   
   # New
   embedding_provider = get_embedding_provider()
   embeddings = await embedding_provider.get_embeddings(texts)
   ```

3. **Update configuration**:
   ```bash
   # Add provider configuration to .env
   PROVIDER_EMBEDDING_TYPE=openai
   PROVIDER_LLM_TYPE=openai
   PROVIDER_VECTOR_STORE_TYPE=qdrant
   ```

## Testing

### Unit Testing

```python
import pytest
from unittest.mock import Mock
from app.infrastructure.providers import ServiceLocator

def test_provider_creation():
    # Mock provider
    mock_provider = Mock()
    
    # Register mock provider
    service_locator = ServiceLocator()
    service_locator.register_provider("embedding", mock_provider)
    
    # Test
    provider = service_locator.get_embedding_provider()
    assert provider == mock_provider
```

### Integration Testing

```python
def test_openai_provider_integration():
    config = {
        "type": "openai",
        "api_url": "https://api.openai.com/v1/embeddings",
        "api_key": "test_key",
        "model": "text-embedding-ada-002"
    }
    
    provider = ProviderFactory.create_embedding_provider(config)
    assert isinstance(provider, OpenAIEmbeddingProvider)
```

## Troubleshooting

### Common Issues

1. **Provider not found**: Check `PROVIDER_*_TYPE` environment variables
2. **Configuration errors**: Verify API keys and URLs are set correctly
3. **Import errors**: Ensure provider classes are imported in factory

### Debug Mode

Enable debug logging to see provider initialization:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Plugin Discovery**: Automatic discovery of provider plugins
- **Configuration Validation**: Validate provider configurations at startup
- **Provider Health Checks**: Monitor provider availability
- **Fallback Providers**: Automatic fallback to backup providers
- **Provider Metrics**: Collect usage metrics for each provider 