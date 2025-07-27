# Contributing Guidelines

## Welcome Contributors! 🎉

Thank you for your interest in contributing to the RAG LLM API project. This document provides guidelines and best practices for contributing to the project.

## Getting Started

### Prerequisites
- Python 3.8+
- Git
- Basic understanding of FastAPI, LangChain, and vector databases

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/rag-llm.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables (see `docs/development/setup.md`)

## Development Workflow

### 1. Code Style

#### Python Code Style
We use **Black** for code formatting and **Flake8** for linting:

```bash
# Format code
black app/ tests/

# Check code style
flake8 app/ tests/

# Type checking
mypy app/
```

#### Code Style Guidelines
- **Line Length**: 88 characters (Black default)
- **Imports**: Grouped and sorted
- **Docstrings**: Google style docstrings
- **Type Hints**: Use type hints for all functions

#### Example Code Style
```python
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.domain.models import QuestionRequest, QuestionResponse
from app.domain.services.rag_service import RAGService


class MyNewService:
    """Service for handling new functionality.
    
    This service provides methods for processing new features
    and integrating with existing RAG functionality.
    """
    
    def __init__(self) -> None:
        """Initialize the service with required dependencies."""
        self.rag_service = RAGService()
    
    async def process_feature(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process new feature data.
        
        Args:
            data: Input data for processing
            
        Returns:
            Processed data with results
            
        Raises:
            ValueError: If data is invalid
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        # Process the data
        result = await self._process_data(data)
        return {"success": True, "result": result}
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method for data processing."""
        # Implementation here
        return data
```

### 2. Testing

#### Test Structure
```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interactions
├── e2e/           # End-to-end tests for complete workflows
└── fixtures/      # Test data and fixtures
```

#### Writing Tests
```python
import pytest
from unittest.mock import AsyncMock, patch
from app.domain.services.rag_service import RAGService


class TestRAGService:
    """Test cases for RAGService."""
    
    @pytest.fixture
    def rag_service(self) -> RAGService:
        """Create RAGService instance for testing."""
        return RAGService()
    
    @pytest.mark.asyncio
    async def test_add_document_success(self, rag_service: RAGService) -> None:
        """Test successful document addition."""
        # Arrange
        file_path = "test_document.txt"
        
        with patch.object(rag_service.document_loader, 'load_document') as mock_load:
            mock_load.return_value = "Test document content"
            
            with patch.object(rag_service.api_service, 'call_openai_embeddings') as mock_embed:
                mock_embed.return_value = [[0.1, 0.2, 0.3]]
                
                with patch.object(rag_service.vector_store, 'insert_vectors') as mock_insert:
                    mock_insert.return_value = True
                    
                    # Act
                    result = await rag_service.add_document(file_path)
                    
                    # Assert
                    assert result["success"] is True
                    assert result["chunks_processed"] == 1
                    mock_load.assert_called_once_with(file_path)
                    mock_embed.assert_called_once()
                    mock_insert.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_document_failure(self, rag_service: RAGService) -> None:
        """Test document addition failure."""
        # Arrange
        file_path = "nonexistent.txt"
        
        with patch.object(rag_service.document_loader, 'load_document') as mock_load:
            mock_load.side_effect = FileNotFoundError("File not found")
            
            # Act & Assert
            with pytest.raises(FileNotFoundError):
                await rag_service.add_document(file_path)
```

#### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run tests in parallel
pytest -n auto
```

### 3. Documentation

#### Code Documentation
- **Docstrings**: All public functions and classes must have docstrings
- **Type Hints**: Use type hints for all function parameters and return values
- **Comments**: Add comments for complex logic

#### API Documentation
- **OpenAPI**: FastAPI automatically generates OpenAPI documentation
- **Examples**: Include usage examples in docstrings
- **Error Responses**: Document all possible error responses

#### Example Documentation
```python
from typing import List, Dict, Any
from pydantic import BaseModel


class QuestionRequest(BaseModel):
    """Request model for question answering.
    
    Attributes:
        question: The question to ask
        top_k: Number of top results to retrieve (default: 3)
    """
    question: str
    top_k: int = 3


async def ask_question(request: QuestionRequest) -> Dict[str, Any]:
    """Ask a question and get an answer using RAG.
    
    This endpoint processes user questions, searches for relevant
    context in the knowledge base, and generates AI-powered answers.
    
    Args:
        request: QuestionRequest containing the question and parameters
        
    Returns:
        Dictionary containing the answer, sources, and context used
        
    Raises:
        HTTPException: If processing fails or no relevant context is found
        
    Example:
        >>> request = QuestionRequest(question="What is Python?", top_k=3)
        >>> result = await ask_question(request)
        >>> print(result["answer"])
        "Python is a high-level programming language..."
    """
    # Implementation here
    pass
```

### 4. Git Workflow

#### Branch Naming
- **Feature branches**: `feature/description-of-feature`
- **Bug fixes**: `fix/description-of-bug`
- **Documentation**: `docs/description-of-docs`
- **Refactoring**: `refactor/description-of-refactor`

#### Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

**Examples:**
```
feat(rag): add support for PDF document processing
fix(api): resolve CORS issues in production
docs(api): add comprehensive usage examples
test(rag): add unit tests for document loader
```

#### Pull Request Process
1. **Create Feature Branch**: `git checkout -b feature/your-feature`
2. **Make Changes**: Implement your feature/fix
3. **Write Tests**: Add tests for new functionality
4. **Update Documentation**: Update relevant documentation
5. **Run Tests**: Ensure all tests pass
6. **Format Code**: Run Black and Flake8
7. **Commit Changes**: Use conventional commit format
8. **Push Branch**: `git push origin feature/your-feature`
9. **Create PR**: Submit pull request with detailed description

### 5. Pull Request Guidelines

#### PR Description Template
```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally
- [ ] Manual testing completed

## Checklist
- [ ] Code follows the project's style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)

## Screenshots (if applicable)
Add screenshots for UI changes.

## Additional Notes
Any additional information or context.
```

## Code Review Guidelines

### Review Checklist
- [ ] **Functionality**: Does the code work as intended?
- [ ] **Testing**: Are there adequate tests?
- [ ] **Documentation**: Is the code well-documented?
- [ ] **Performance**: Are there any performance concerns?
- [ ] **Security**: Are there any security vulnerabilities?
- [ ] **Style**: Does the code follow style guidelines?

### Review Comments
- **Be Constructive**: Provide helpful, actionable feedback
- **Be Specific**: Point to specific lines and explain issues
- **Be Respectful**: Maintain a positive, collaborative tone
- **Suggest Solutions**: Offer specific suggestions for improvements

## Issue Reporting

### Bug Reports
When reporting bugs, please include:
- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: OS, Python version, dependencies
- **Screenshots**: If applicable

### Feature Requests
When requesting features, please include:
- **Description**: Clear description of the feature
- **Use Case**: Why this feature is needed
- **Proposed Solution**: How you think it should work
- **Alternatives**: Any alternative solutions considered

## Community Guidelines

### Code of Conduct
- **Be Respectful**: Treat all contributors with respect
- **Be Inclusive**: Welcome contributors from all backgrounds
- **Be Collaborative**: Work together to improve the project
- **Be Professional**: Maintain professional communication

### Communication Channels
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and discussions
- **Pull Requests**: For code contributions and reviews

## Recognition

### Contributors
All contributors will be recognized in:
- **README.md**: List of contributors
- **CHANGELOG.md**: Credit for significant contributions
- **GitHub**: Contributor statistics and profile

### Contribution Levels
- **Bug Fixes**: Small fixes and improvements
- **Features**: New functionality and enhancements
- **Documentation**: Documentation improvements
- **Testing**: Test coverage and quality improvements
- **Infrastructure**: Build, deployment, and tooling improvements

## Getting Help

### Resources
- **Documentation**: Check the `/docs` directory
- **Issues**: Search existing issues for similar problems
- **Discussions**: Ask questions in GitHub Discussions
- **Code Examples**: See `/docs/api/examples.md`

### Mentorship
- **New Contributors**: Experienced contributors can mentor new contributors
- **Pair Programming**: Collaborate on complex features
- **Code Reviews**: Learn from feedback and suggestions

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to the RAG LLM API project! 🚀 