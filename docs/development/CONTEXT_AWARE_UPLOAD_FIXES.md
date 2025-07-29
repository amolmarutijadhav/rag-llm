# Context-Aware Document Upload Fixes

This document explains the fixes implemented for the context-aware document upload functionality and how to use them.

## 🔧 **Issues Fixed**

### **1. HTTP Status Code Issue**
**Problem**: The API was returning HTTP 200 even when the upload operation failed.
**Fix**: Modified the API routes to return HTTP 500 for failures instead of 200.

**Files Modified**:
- `app/api/routes/context_aware_documents.py`

**Changes**:
```python
# Before: Always returned 200
return DocumentUploadResponse(**result)

# After: Return 500 for failures
if result.get('success', False):
    return DocumentUploadResponse(**result)
else:
    raise HTTPException(
        status_code=500, 
        detail=result.get('message', 'Document upload failed')
    )
```

### **2. Enhanced Error Logging**
**Problem**: Limited error information made debugging difficult.
**Fix**: Added detailed error logging with provider information.

**Files Modified**:
- `app/infrastructure/vector_store/vector_store.py`

**Changes**:
```python
# Added detailed error information
'error_details': {
    'embedding_provider': type(self.embedding_provider).__name__,
    'vector_store_provider': type(self.vector_store_provider).__name__,
    'collection_name': self.collection_name,
    'documents_sample': [doc.get('id', 'no_id') for doc in documents[:3]],
    'embedding_provider_config': getattr(self.embedding_provider, 'api_url', 'unknown'),
    'vector_store_provider_config': getattr(self.vector_store_provider, 'api_url', 'unknown')
}
```

### **3. Provider Health Check**
**Problem**: No way to verify if providers are working correctly.
**Fix**: Added a health check endpoint for providers.

**Files Modified**:
- `app/api/routes/context_aware_documents.py`

**New Endpoint**: `GET /context-aware-documents/health`

**Response**:
```json
{
    "status": "healthy",
    "embedding_provider": "working",
    "vector_store_provider": "working",
    "collection_stats": {...},
    "embedding_dimensions": 1536
}
```

## 🚀 **How to Use the Fixes**

### **1. Test Provider Health**
```bash
# Check if providers are working
curl http://localhost:8000/context-aware-documents/health
```

### **2. Test Context Options**
```bash
# Get available context options
curl http://localhost:8000/context-aware-documents/context-options
```

### **3. Test Text Upload**
```bash
# Upload text with context
curl -X POST "http://localhost:8000/context-aware-documents/upload-text" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=This is a test document" \
  -d "context_type=technical" \
  -d "content_domain=api_documentation" \
  -d "document_category=user_guide"
```

### **4. Test File Upload**
```bash
# Upload file with context
curl -X POST "http://localhost:8000/context-aware-documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_document.txt" \
  -F "context_type=technical" \
  -F "content_domain=api_documentation" \
  -F "document_category=user_guide"
```

### **5. Run Test Script**
```bash
# Run comprehensive tests
python scripts/test_context_aware_upload.py
```

## 🔍 **Debugging Steps**

### **Step 1: Check Server Status**
```bash
# Verify server is running
curl http://localhost:8000/health
```

### **Step 2: Check Provider Health**
```bash
# Check if providers are configured correctly
curl http://localhost:8000/context-aware-documents/health
```

### **Step 3: Check Environment Variables**
Make sure your `.env` file has the correct configuration:

```env
# For OpenAI providers
OPENAI_API_KEY=your_openai_api_key_here
PROVIDER_EMBEDDING_TYPE=openai
PROVIDER_LLM_TYPE=openai
PROVIDER_VECTOR_STORE_TYPE=qdrant

# For Qdrant vector store
QDRANT_API_KEY=your_qdrant_api_key_here
VECTOR_INSERT_API_URL=https://your-cluster.qdrant.io:6333/collections/documents/points
VECTOR_SEARCH_API_URL=https://your-cluster.qdrant.io:6333/collections/documents/points/search
VECTOR_COLLECTION_URL=https://your-cluster.qdrant.io:6333/collections/documents

# For testing with mock providers
PROVIDER_EMBEDDING_TYPE=mock
PROVIDER_LLM_TYPE=mock
PROVIDER_VECTOR_STORE_TYPE=mock
```

### **Step 4: Check Server Logs**
Look for detailed error messages in the server logs:

```bash
# Start server with debug logging
python scripts/run.py
```

### **Step 5: Use Test Configuration**
For testing without real APIs, use the test configuration:

```bash
# Copy test configuration
cp config/test_config.env .env

# Start server with test config
python scripts/run.py
```

## 📋 **Common Issues and Solutions**

### **Issue 1: "Failed to fetch" in Swagger UI**
**Solution**: 
1. Check CORS configuration
2. Verify server is running on correct port
3. Clear browser cache

### **Issue 2: Provider Health Check Fails**
**Solution**:
1. Check API keys in `.env` file
2. Verify provider URLs are correct
3. Test with mock providers first

### **Issue 3: Vector Store Insertion Fails**
**Solution**:
1. Check Qdrant API key and URLs
2. Verify collection exists
3. Check network connectivity

### **Issue 4: Embedding Generation Fails**
**Solution**:
1. Check OpenAI API key
2. Verify embedding model name
3. Check API rate limits

## 🧪 **Testing with Mock Providers**

For development and testing, you can use mock providers that don't require real API keys:

```env
# Use mock providers
PROVIDER_EMBEDDING_TYPE=mock
PROVIDER_LLM_TYPE=mock
PROVIDER_VECTOR_STORE_TYPE=mock
```

Mock providers will:
- Generate fake embeddings
- Simulate vector store operations
- Return mock responses
- Allow testing without API costs

## 📊 **Monitoring and Logging**

The fixes include enhanced logging for better monitoring:

### **Log Events**:
- `context_aware_document_upload_start`
- `context_aware_document_upload_success`
- `context_aware_document_upload_failure`
- `context_aware_document_upload_error`
- `provider_health_check_start`
- `provider_health_check_success`
- `provider_health_check_failure`

### **Log Fields**:
- `correlation_id`: Request tracking
- `filename`: Uploaded file name
- `context_type`: Document context
- `documents_added`: Number of documents processed
- `error`: Error details
- `error_type`: Exception type
- `error_details`: Provider-specific error information

## 🎯 **Expected Behavior After Fixes**

### **Successful Upload**:
- HTTP 200 status code
- Response with `success: true`
- Document count in response
- Context information included

### **Failed Upload**:
- HTTP 500 status code
- Detailed error message
- Provider information in logs
- Specific failure reason

### **Health Check**:
- Provider status information
- Collection statistics
- Embedding dimensions
- Error details if unhealthy

## 🔄 **Next Steps**

1. **Test the fixes** using the provided test script
2. **Configure your environment** with correct API keys
3. **Monitor logs** for any remaining issues
4. **Use the health endpoint** to verify provider status
5. **Test with real documents** once mock providers work

The fixes ensure proper error handling, detailed logging, and better debugging capabilities for the context-aware document upload functionality. 