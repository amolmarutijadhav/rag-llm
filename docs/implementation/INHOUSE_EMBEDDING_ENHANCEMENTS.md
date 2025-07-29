# Inhouse Embedding Provider Enhancements

## Overview

The InhouseEmbeddingProvider has been enhanced to support single text processing instead of batch processing, as required by the inhouse embedding API. Additionally, the provider now sends requests using form data format instead of JSON, as required by the inhouse API specification. This enhancement maintains backward compatibility while providing better performance, error handling, and monitoring capabilities.

## Key Enhancements

### 1. Single Text Processing

**Problem**: The inhouse embedding API processes one text at a time, not arrays of texts.

**Solution**: Enhanced the provider to:
- Process texts individually using `get_single_embedding()`
- Maintain the same interface for `get_embeddings()` 
- Use controlled concurrency for batch processing

### 2. Form Data Request Format

**Problem**: The inhouse embedding API expects form data instead of JSON.

**Solution**: Updated the provider to:
- Send requests using `data` parameter instead of `json_data`
- Use `application/x-www-form-urlencoded` content type
- Maintain proper request formatting for the API

### 3. Controlled Concurrency

**Features**:
- Configurable `max_concurrent_requests` (default: 5)
- Configurable `request_delay` between requests (default: 0.1s)
- Semaphore-based concurrency control
- Rate limiting support

### 4. Enhanced Error Handling

**Improvements**:
- Individual text failure handling
- Maintains order in batch responses
- Detailed error logging with correlation IDs
- Graceful degradation for failed texts

### 5. Multiple Response Format Support

**Supported Formats**:
```json
// Format 1: Direct embedding
{"embedding": [0.1, 0.2, 0.3, ...]}

// Format 2: Vector field
{"vector": [0.1, 0.2, 0.3, ...]}

// Format 3: Data array
{"data": [{"embedding": [0.1, 0.2, 0.3, ...]}]}

// Format 4: Embeddings array
{"embeddings": [[0.1, 0.2, 0.3, ...]]}
```

### 6. Performance Monitoring

**Metrics Tracked**:
- Processing time per text
- Total processing time
- Character count and throughput
- Success/failure rates
- Concurrent request utilization

## Configuration

### Basic Configuration

```python
config = {
    "api_url": "https://inhouse-embeddings.company.com/api/v1/embed",
    "api_key": "your-api-key-here",
    "model": "company-embedding-v2",
    "max_concurrent_requests": 5,
    "request_delay": 0.1
}
```

**Note**: The provider automatically sends requests using form data format (`application/x-www-form-urlencoded`) instead of JSON, as required by the inhouse embedding API.

### Advanced Configuration

```python
config = {
    "api_url": "https://inhouse-embeddings.company.com/api/v1/embed",
    "api_key": "your-api-key-here",
    "model": "company-embedding-v2",
    "max_concurrent_requests": 10,  # Higher concurrency
    "request_delay": 0.05,  # Faster processing
    "timeout": 30,  # Request timeout
    "max_retries": 3  # Retry configuration
}
```

## Usage Examples

### Single Text Processing

```python
provider = InhouseEmbeddingProvider(config)

# Process single text
embedding = await provider.get_single_embedding("Sample text")
print(f"Embedding dimensions: {len(embedding)}")
```

### Batch Processing (Internal Single Processing)

```python
# Process multiple texts (handled as individual requests)
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = await provider.get_embeddings(texts)

for i, embedding in enumerate(embeddings):
    print(f"Text {i+1}: {len(embedding)} dimensions")
```

### Error Handling

```python
# Mixed batch with potential failures
texts = ["Valid text", "", "Another valid text"]
embeddings = await provider.get_embeddings(texts)

# Failed texts return empty embeddings but maintain order
for i, embedding in enumerate(embeddings):
    if embedding:
        print(f"Text {i+1}: Success")
    else:
        print(f"Text {i+1}: Failed")
```

## Performance Considerations

### Concurrency Settings

| Use Case | max_concurrent_requests | request_delay | Description |
|----------|------------------------|---------------|-------------|
| Development | 1 | 0.5s | Conservative, easy debugging |
| Production | 5-10 | 0.1s | Balanced performance |
| High Throughput | 10-20 | 0.05s | Maximum performance |
| Rate Limited API | 1-3 | 1.0s | Respect API limits |

### Monitoring

The enhanced provider provides comprehensive logging:

```python
# Log entries include:
{
    "event_type": "inhouse_embedding_request_success",
    "provider": "inhouse_embeddings",
    "text_count": 5,
    "embedding_count": 5,
    "duration_ms": 1250,
    "total_chars": 1500,
    "avg_ms_per_text": 250,
    "processing_mode": "single_text"
}
```

## Migration Guide

### From Previous Version

No code changes required! The interface remains the same:

```python
# This still works exactly the same
embeddings = await provider.get_embeddings(texts)
```

### New Features Available

```python
# New: Single text processing
embedding = await provider.get_single_embedding("Single text")

# New: Enhanced configuration
config = {
    "max_concurrent_requests": 10,
    "request_delay": 0.05
}

# New: Better error handling
# Failed texts return empty embeddings instead of raising exceptions
```

## Testing

### Unit Tests

```python
# Test single text processing
async def test_single_embedding():
    provider = InhouseEmbeddingProvider(config)
    embedding = await provider.get_single_embedding("test")
    assert len(embedding) > 0

# Test batch processing
async def test_batch_processing():
    provider = InhouseEmbeddingProvider(config)
    embeddings = await provider.get_embeddings(["text1", "text2"])
    assert len(embeddings) == 2
```

### Integration Tests

```python
# Test with real API
async def test_real_api():
    provider = InhouseEmbeddingProvider(real_config)
    embeddings = await provider.get_embeddings(test_texts)
    # Verify embeddings are valid
    for embedding in embeddings:
        assert len(embedding) == expected_dimensions
```

## Troubleshooting

### Common Issues

1. **Rate Limiting**: Increase `request_delay` or decrease `max_concurrent_requests`
2. **Timeout Errors**: Increase `timeout` in configuration
3. **Empty Embeddings**: Check API response format in `_extract_single_embedding()`
4. **Performance Issues**: Monitor logs for `avg_ms_per_text` and adjust concurrency

### Debug Mode

Enable debug logging to see detailed request/response information:

```python
import logging
logging.getLogger("app.infrastructure.providers.inhouse_provider").setLevel(logging.DEBUG)
```

## Future Enhancements

1. **Caching Layer**: Add embedding caching for repeated texts
2. **Model-Specific Configurations**: Support different models with specific parameters
3. **Advanced Retry Logic**: Implement exponential backoff and circuit breaker patterns
4. **Metrics Export**: Export performance metrics to monitoring systems
5. **Batch Size Optimization**: Automatic batch size adjustment based on text length

## Conclusion

The enhanced InhouseEmbeddingProvider provides a robust, performant solution for single text processing while maintaining full backward compatibility. The implementation includes comprehensive error handling, performance monitoring, and flexible configuration options suitable for production use. 