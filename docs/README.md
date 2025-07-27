# RAG LLM API Documentation

Welcome to the comprehensive documentation for the RAG LLM API - a production-ready Retrieval-Augmented Generation API built with FastAPI, LangChain, and Qdrant Cloud.

## 📚 Documentation Structure

### **API Documentation** (`/api/`)
- [API Overview](api/overview.md) - Introduction to the API
- [Endpoints](api/endpoints.md) - Complete API endpoint reference
- [Models](api/models.md) - Request and response models
- [Authentication](api/authentication.md) - API authentication guide
- [Examples](api/examples.md) - Usage examples and code samples

### **Development Documentation** (`/development/`)
- [Setup Guide](development/setup.md) - Development environment setup
- [Architecture](development/architecture.md) - System architecture overview
- [Contributing](development/contributing.md) - Contribution guidelines
- [Testing](development/testing.md) - Testing strategy and guidelines
- [Deployment](development/deployment.md) - Deployment instructions

### **Implementation Guides** (`/implementation/`)
- [RAG Chat Completions](implementation/RAG_CHAT_COMPLETIONS_IMPLEMENTATION.md) - RAG-enhanced chat implementation

### **Tutorials** (`/tutorials/`)
- [Getting Started](tutorials/getting_started.md) - Quick start guide
- [Troubleshooting](tutorials/troubleshooting.md) - Common issues and solutions

### **Changelog** (`/changelog/`)
- [CHANGELOG](changelog/CHANGELOG.md) - Version history
- [Migration Guides](changelog/migration_guides.md) - Version migration instructions

## 🚀 Quick Start

1. **Setup**: Follow the [Setup Guide](development/setup.md)
2. **API Reference**: Check [Endpoints](api/endpoints.md)
3. **Examples**: See [Usage Examples](api/examples.md)
4. **Testing**: Review [Testing Guide](development/testing.md)

## 🏗️ Architecture Overview

The RAG LLM API follows a **Domain-Driven Design** architecture with clear separation of concerns:

```
app/
├── api/          # API layer (routes, middleware)
├── core/         # Core configuration and utilities
├── domain/       # Business logic and models
├── infrastructure/ # External integrations
└── utils/        # Helper functions
```

## 🧪 Testing Strategy

The project uses a comprehensive testing strategy:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Test system performance

## 📖 Key Features

- ✅ **Multi-Agentic Support**: Preserve agent personas in chat completions
- ✅ **RAG Integration**: Automatic knowledge base enhancement
- ✅ **External API Support**: OpenAI, Qdrant, and other services
- ✅ **Production Ready**: Comprehensive error handling and validation
- ✅ **Scalable Architecture**: Clean, maintainable code structure
- ✅ **Comprehensive Testing**: Full test coverage with multiple test types

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Browse this documentation
- **Issues**: Report bugs and feature requests
- **Discussions**: Join community discussions
- **Examples**: Check the [Examples](api/examples.md) section 