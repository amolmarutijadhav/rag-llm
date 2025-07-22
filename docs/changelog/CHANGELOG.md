# Changelog

All notable changes to the RAG LLM API project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-20

### Added
- **Robust Field Handling**: Added support for both `"content"` and `"page_content"` field names in vector database payloads
- **VECTOR_COLLECTION_URL**: New environment variable for dedicated collection management operations
- **Debug Tools**: Added `debug_search.py` script for troubleshooting search functionality
- **Enhanced Error Handling**: Improved error handling for missing or malformed payloads in search results
- **Comprehensive API Testing**: Added `test_apis.py` script for end-to-end API testing

### Changed
- **VectorStore.search()**: Updated to handle inconsistent field names gracefully
- **ExternalAPIService**: Updated collection operations to use dedicated `VECTOR_COLLECTION_URL`
- **Configuration**: Added `VECTOR_COLLECTION_URL` to environment variables and config
- **Documentation**: Updated README.md and API_DOCUMENTATION.md with latest changes and fixes

### Fixed
- **Search Functionality**: Fixed `Error searching documents: 'content'` issue caused by inconsistent field names
- **Collection Stats**: Fixed get stats endpoint to use correct collection URL instead of deriving from insert URL
- **404 Errors**: Resolved 404 errors related to incorrect Qdrant Cloud API URL construction
- **Field Compatibility**: Ensured backward compatibility with existing data using different field naming conventions

### Technical Details
- **Field Handling Logic**: 
  - Primary field: `"content"` (standard)
  - Fallback field: `"page_content"` (compatibility)
  - Graceful handling of missing fields
- **URL Configuration**: All external API endpoints now use complete URLs without path appending
- **Error Resilience**: Improved error handling and logging throughout the search pipeline

## [1.0.0] - 2024-12-19

### Added
- **Initial Release**: Production-ready RAG LLM API with FastAPI, LangChain, and Qdrant Cloud
- **Document Upload**: Support for PDF, TXT, and DOCX files
- **Text Input**: Add raw text to the knowledge base
- **Question Answering**: Ask questions and get AI-generated answers using RAG
- **Vector Search**: Semantic search using Qdrant Cloud
- **RESTful API**: Clean, documented API endpoints
- **Auto-generated Docs**: Interactive API documentation
- **Externalized APIs**: Complete URL configuration for all external services
- **Comprehensive Testing**: Unit tests, API tests, and integration tests

### Features
- **External API Configuration**: All external API endpoints fully configurable via environment variables
- **No Path Appending**: URLs used directly without modification
- **Flexible Provider Support**: Easy switching between different service providers
- **Collection Management**: Automatic collection creation and management
- **Error Handling**: Comprehensive error handling and validation
- **Performance**: Optimized for production use with configurable timeouts and retries

### Technical Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: Framework for developing applications with LLMs
- **Qdrant Cloud**: Vector database for storing and searching embeddings
- **OpenAI**: Embeddings and LLM services
- **Pytest**: Comprehensive testing framework
- **Uvicorn**: ASGI server for production deployment

---

## Version History

### Version 1.1.0 (Current)
- **Focus**: Bug fixes and robustness improvements
- **Key Fix**: Search functionality with field name compatibility
- **Impact**: Improved reliability and backward compatibility

### Version 1.0.0 (Initial Release)
- **Focus**: Core RAG functionality and API endpoints
- **Key Features**: Document processing, vector search, question answering
- **Impact**: Production-ready RAG API with externalized configuration

---

## Migration Guide

### From 1.0.0 to 1.1.0

#### Environment Variables
Add the new `VECTOR_COLLECTION_URL` environment variable:

```bash
# Add this to your .env file
VECTOR_COLLECTION_URL=https://your-cluster-id.us-east-1-0.aws.cloud.qdrant.io:6333/collections/documents
```

#### No Breaking Changes
- All existing functionality remains the same
- Improved compatibility with existing data
- Enhanced error handling and robustness

#### Benefits
- **Better Search Reliability**: Handles inconsistent field names
- **Improved Error Handling**: More graceful handling of edge cases
- **Enhanced Debugging**: Better tools for troubleshooting
- **Backward Compatibility**: Works with existing data structures

---

## Contributing

When contributing to this project, please:

1. Update this changelog with your changes
2. Follow the existing format and style
3. Include both user-facing and technical changes
4. Add migration notes if there are breaking changes
5. Include version numbers and dates

---

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the logs for error details
3. Ensure your environment variables are correctly configured
4. Run tests to verify your setup: `python run_tests.py`
5. Use the debug tools: `python debug_search.py` for search issues 