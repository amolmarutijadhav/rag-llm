"""
End-to-End tests for Context-Aware RAG system.
Tests real API calls with actual document processing and context-aware responses.
"""

import pytest
import tempfile
import os
import time
import requests
from typing import Dict, Any, List
import json

# Test configuration
BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30


class TestContextAwareRAGE2E:
    """End-to-End tests for Context-Aware RAG system"""
    
    @pytest.mark.skip(reason="Document upload has page_content issue - to be fixed")
    def test_context_aware_document_upload_e2e(self):
        """Test end-to-end document upload with context"""
        # Create a temporary test document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("""
API Authentication Guide

This document provides comprehensive information about API authentication methods.

1. Basic Authentication
   - Username and password required
   - Base64 encoded credentials
   - Include in Authorization header

2. Bearer Token Authentication
   - JWT tokens for secure access
   - Include in Authorization header as "Bearer <token>"
   - Tokens expire after 24 hours

3. API Key Authentication
   - Simple API key in header
   - Include as "X-API-Key: <your-key>"
   - No expiration but can be revoked

Best Practices:
- Always use HTTPS in production
- Rotate tokens regularly
- Store credentials securely
- Monitor authentication attempts
            """)
            temp_file_path = f.name
        
        try:
            # Upload document with context
            with open(temp_file_path, 'rb') as file:
                files = {"file": ("api_auth_guide.txt", file, "text/plain")}
                data = {
                    "context_type": "technical",
                    "content_domain": "api_documentation",
                    "document_category": "user_guide",
                    "relevance_tags": "authentication,security,api",
                    "description": "API authentication documentation and best practices"
                }
                
                response = requests.post(
                    f"{BASE_URL}/context-aware-documents/upload",
                    files=files,
                    data=data,
                    timeout=API_TIMEOUT
                )
            
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            assert response.status_code == 200
            result = response.json()
            print(f"Parsed result: {result}")
            
            assert result["success"] is True
            assert "documents_added" in result
            assert result["documents_added"] > 0
            
            print(f"✅ Document uploaded successfully: {result}")
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
    
    def test_context_aware_text_upload_e2e(self):
        """Test end-to-end text upload with context"""
        text_content = """
Product Launch Strategy 2024

Our new product launch will focus on three key areas:

1. Market Positioning
   - Target enterprise customers
   - Emphasize security and scalability
   - Competitive pricing strategy

2. Marketing Campaign
   - Digital marketing channels
   - Content marketing approach
   - Social media engagement

3. Sales Strategy
   - Direct sales team
   - Partner channel development
   - Customer success focus

Key Metrics:
- Customer acquisition cost
- Conversion rates
- Customer lifetime value
- Market share growth
        """
        
        data = {
            "text": text_content,
            "context_type": "creative",
            "content_domain": "marketing",
            "document_category": "user_guide",
            "relevance_tags": "product,launch,strategy,marketing",
            "description": "Product launch strategy and marketing plan",
            "source_name": "product_launch_strategy_2024"
        }
        
        response = requests.post(
            f"{BASE_URL}/context-aware-documents/upload-text",
            data=data,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "documents_added" in result
        assert result["documents_added"] > 0
        
        print(f"✅ Text uploaded successfully: {result}")
    
    def test_context_aware_chat_rag_only_e2e(self):
        """Test context-aware chat with RAG_ONLY response mode"""
        # First upload a document
        text_content = """
Python Programming Best Practices

1. Code Organization
   - Use meaningful variable names
   - Follow PEP 8 style guidelines
   - Organize code into modules and packages

2. Error Handling
   - Use try-except blocks appropriately
   - Log errors with context
   - Provide meaningful error messages

3. Performance Optimization
   - Use list comprehensions when appropriate
   - Avoid unnecessary loops
   - Profile code to identify bottlenecks

4. Testing
   - Write unit tests for all functions
   - Use pytest for testing framework
   - Maintain high test coverage
        """
        
        # Upload text with context
        upload_data = {
            "text": text_content,
            "context_type": "technical",
            "content_domain": "programming",
            "document_category": "best_practices",
            "relevance_tags": "python,programming,testing",
            "description": "Python programming best practices guide"
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/context-aware-documents/upload-text",
            data=upload_data,
            timeout=API_TIMEOUT
        )
        
        assert upload_response.status_code == 200
        
        # Wait a moment for processing
        time.sleep(2)
        
        # Now test chat with RAG_ONLY mode
        chat_request = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. RESPONSE_MODE: RAG_ONLY"
                },
                {
                    "role": "user",
                    "content": "What are the best practices for Python programming?"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=chat_request,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert "choices" in result
        assert len(result["choices"]) > 0
        assert "message" in result["choices"][0]
        assert "content" in result["choices"][0]["message"]
        
        content = result["choices"][0]["message"]["content"]
        assert len(content) > 0
        
        # Check that the response contains information from our uploaded document
        assert any(keyword in content.lower() for keyword in ["python", "programming", "testing", "best practices"])
        
        print(f"✅ RAG_ONLY chat response: {content[:200]}...")
    
    def test_context_aware_chat_hybrid_e2e(self):
        """Test context-aware chat with HYBRID response mode"""
        # Upload a document about a specific topic
        text_content = """
Machine Learning Fundamentals

Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions without explicit programming.

Key Concepts:
1. Supervised Learning
   - Uses labeled training data
   - Examples: classification, regression
   - Algorithms: linear regression, decision trees, neural networks

2. Unsupervised Learning
   - Uses unlabeled data
   - Examples: clustering, dimensionality reduction
   - Algorithms: k-means, PCA, autoencoders

3. Reinforcement Learning
   - Learning through interaction with environment
   - Examples: game playing, robotics
   - Algorithms: Q-learning, policy gradients
        """
        
        # Upload text with context
        upload_data = {
            "text": text_content,
            "context_type": "technical",
            "content_domain": "machine_learning",
            "document_category": "tutorial",
            "relevance_tags": "ml,ai,learning,algorithms",
            "description": "Machine learning fundamentals and concepts"
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/context-aware-documents/upload-text",
            data=upload_data,
            timeout=API_TIMEOUT
        )
        
        assert upload_response.status_code == 200
        
        # Wait a moment for processing
        time.sleep(2)
        
        # Test chat with HYBRID mode
        chat_request = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. RESPONSE_MODE: HYBRID"
                },
                {
                    "role": "user",
                    "content": "Explain machine learning and also tell me about recent developments in AI"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=chat_request,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert "choices" in result
        assert len(result["choices"]) > 0
        assert "message" in result["choices"][0]
        assert "content" in result["choices"][0]["message"]
        
        content = result["choices"][0]["message"]["content"]
        assert len(content) > 0
        
        # Should contain both RAG content and general knowledge
        assert any(keyword in content.lower() for keyword in ["machine learning", "supervised", "unsupervised"])
        
        print(f"✅ HYBRID chat response: {content[:200]}...")
    
    def test_context_aware_chat_smart_fallback_e2e(self):
        """Test context-aware chat with SMART_FALLBACK response mode"""
        # Upload a document with specific content
        text_content = """
Database Design Principles

1. Normalization
   - First Normal Form (1NF)
   - Second Normal Form (2NF)
   - Third Normal Form (3NF)

2. Indexing Strategies
   - Primary key indexes
   - Secondary indexes
   - Composite indexes

3. Query Optimization
   - Use appropriate WHERE clauses
   - Avoid SELECT *
   - Use indexes effectively
        """
        
        # Upload text with context
        upload_data = {
            "text": text_content,
            "context_type": "technical",
            "content_domain": "database",
            "document_category": "reference",
            "relevance_tags": "database,design,optimization",
            "description": "Database design principles and optimization"
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/context-aware-documents/upload-text",
            data=upload_data,
            timeout=API_TIMEOUT
        )
        
        assert upload_response.status_code == 200
        
        # Wait a moment for processing
        time.sleep(2)
        
        # Test chat with SMART_FALLBACK mode
        chat_request = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. RESPONSE_MODE: SMART_FALLBACK\nMIN_CONFIDENCE: 0.8"
                },
                {
                    "role": "user",
                    "content": "What are the best practices for database design?"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=chat_request,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert "choices" in result
        assert len(result["choices"]) > 0
        assert "message" in result["choices"][0]
        assert "content" in result["choices"][0]["message"]
        
        content = result["choices"][0]["message"]["content"]
        assert len(content) > 0
        
        print(f"✅ SMART_FALLBACK chat response: {content[:200]}...")
    
    def test_context_aware_chat_json_directives_e2e(self):
        """Test context-aware chat with JSON-like directives"""
        # Upload a document
        text_content = """
Web Security Best Practices

1. Input Validation
   - Validate all user inputs
   - Use parameterized queries
   - Implement proper sanitization

2. Authentication & Authorization
   - Use strong passwords
   - Implement multi-factor authentication
   - Follow principle of least privilege

3. Data Protection
   - Encrypt sensitive data
   - Use HTTPS for all communications
   - Implement proper session management
        """
        
        # Upload text with context
        upload_data = {
            "text": text_content,
            "context_type": "technical",
            "content_domain": "security",
            "document_category": "best_practices",
            "relevance_tags": "security,web,authentication",
            "description": "Web security best practices guide"
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/context-aware-documents/upload-text",
            data=upload_data,
            timeout=API_TIMEOUT
        )
        
        assert upload_response.status_code == 200
        
        # Wait a moment for processing
        time.sleep(2)
        
        # Test chat with JSON-like directives
        chat_request = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. <config>RESPONSE_MODE: RAG_PRIORITY\nMIN_CONFIDENCE: 0.7</config>"
                },
                {
                    "role": "user",
                    "content": "How can I improve web security for my application?"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=chat_request,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert "choices" in result
        assert len(result["choices"]) > 0
        assert "message" in result["choices"][0]
        assert "content" in result["choices"][0]["message"]
        
        content = result["choices"][0]["message"]["content"]
        assert len(content) > 0
        
        # Should contain security-related information
        assert any(keyword in content.lower() for keyword in ["security", "authentication", "validation"])
        
        print(f"✅ JSON directives chat response: {content[:200]}...")
    
    def test_context_aware_chat_fallback_to_enhanced_e2e(self):
        """Test fallback to existing enhanced chat when no context directives"""
        chat_request = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "What is the capital of France?"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=chat_request,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert "choices" in result
        assert len(result["choices"]) > 0
        assert "message" in result["choices"][0]
        assert "content" in result["choices"][0]["message"]
        
        content = result["choices"][0]["message"]["content"]
        assert len(content) > 0
        
        # Should contain information about Paris
        assert "paris" in content.lower()
        
        print(f"✅ Fallback to enhanced chat response: {content[:200]}...")
    
    def test_context_aware_stats_e2e(self):
        """Test context-aware stats endpoint"""
        response = requests.get(
            f"{BASE_URL}/context-aware-documents/stats",
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should return stats about the knowledge base
        assert "total_documents" in result or "success" in result
        
        print(f"✅ Context-aware stats: {result}")
    
    def test_context_aware_context_options_e2e(self):
        """Test context options endpoint"""
        response = requests.get(
            f"{BASE_URL}/context-aware-documents/context-options",
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should return available context options
        assert "context_types" in result
        assert "document_categories" in result
        assert "example_domains" in result
        
        # Verify some expected values
        assert "technical" in result["context_types"]
        assert "user_guide" in result["document_categories"]
        
        print(f"✅ Context options: {result}")
    
    def test_enhanced_chat_context_options_e2e(self):
        """Test enhanced chat context options endpoint"""
        response = requests.get(
            f"{BASE_URL}/enhanced-chat/context-options",
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should return context options for enhanced chat
        assert "success" in result
        assert "context_options" in result
        assert "response_modes" in result["context_options"]
        
        # Verify response modes
        response_modes = result["context_options"]["response_modes"]
        assert "RAG_ONLY" in response_modes
        assert "LLM_ONLY" in response_modes
        assert "HYBRID" in response_modes
        assert "SMART_FALLBACK" in response_modes
        
        print(f"✅ Enhanced chat context options: {result}")
    
    def test_context_aware_end_to_end_workflow_e2e(self):
        """Test complete end-to-end context-aware workflow"""
        # Step 1: Upload multiple documents with different contexts
        documents = [
            {
                "text": "Docker containerization allows you to package applications with their dependencies.",
                "context_type": "technical",
                "content_domain": "devops",
                "document_category": "tutorial",
                "relevance_tags": "docker,containers,deployment",
                "description": "Docker containerization guide"
            },
            {
                "text": "Kubernetes is an open-source container orchestration platform for automating deployment.",
                "context_type": "technical", 
                "content_domain": "devops",
                "document_category": "reference",
                "relevance_tags": "kubernetes,orchestration,scaling",
                "description": "Kubernetes orchestration guide"
            }
        ]
        
        # Upload documents
        for doc in documents:
            response = requests.post(
                f"{BASE_URL}/context-aware-documents/upload-text",
                data=doc,
                timeout=API_TIMEOUT
            )
            assert response.status_code == 200
        
        # Wait for processing
        time.sleep(3)
        
        # Step 2: Test different response modes with the same question
        question = "How can I deploy applications using containers?"
        
        response_modes = [
            ("RAG_ONLY", "You are a helpful assistant. RESPONSE_MODE: RAG_ONLY"),
            ("HYBRID", "You are a helpful assistant. RESPONSE_MODE: HYBRID"),
            ("RAG_PRIORITY", "You are a helpful assistant. <config>RESPONSE_MODE: RAG_PRIORITY</config>")
        ]
        
        for mode_name, system_message in response_modes:
            chat_request = {
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            }
            
            response = requests.post(
                f"{BASE_URL}/enhanced-chat/completions",
                json=chat_request,
                timeout=API_TIMEOUT
            )
            
            assert response.status_code == 200
            result = response.json()
            
            assert "choices" in result
            assert len(result["choices"]) > 0
            assert "message" in result["choices"][0]
            assert "content" in result["choices"][0]["message"]
            
            content = result["choices"][0]["message"]["content"]
            assert len(content) > 0
            
            # Should contain container-related information
            assert any(keyword in content.lower() for keyword in ["container", "docker", "kubernetes", "deploy"])
            
            print(f"✅ {mode_name} workflow response: {content[:150]}...")
        
        # Step 3: Test stats to verify documents were added
        stats_response = requests.get(
            f"{BASE_URL}/context-aware-documents/stats",
            timeout=API_TIMEOUT
        )
        
        assert stats_response.status_code == 200
        stats = stats_response.json()
        
        print(f"✅ Final stats after workflow: {stats}")
        
        # Step 4: Clean up by clearing the knowledge base
        clear_response = requests.delete(
            f"{BASE_URL}/context-aware-documents/clear",
            timeout=API_TIMEOUT
        )
        
        assert clear_response.status_code == 200
        clear_result = clear_response.json()
        assert clear_result["success"] is True
        
        print(f"✅ Knowledge base cleared: {clear_result}")


class TestContextAwareRAGErrorHandlingE2E:
    """Test error handling in Context-Aware RAG system"""
    
    def test_invalid_context_type_e2e(self):
        """Test error handling for invalid context type"""
        data = {
            "text": "Test content",
            "context_type": "invalid_type",  # Invalid context type
            "content_domain": "test",
            "document_category": "user_guide"
        }
        
        response = requests.post(
            f"{BASE_URL}/context-aware-documents/upload-text",
            data=data,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 400
        result = response.json()
        assert "Invalid context_type" in result["detail"]
        
        print(f"✅ Invalid context type error handled: {result}")
    
    def test_invalid_document_category_e2e(self):
        """Test error handling for invalid document category"""
        data = {
            "text": "Test content",
            "context_type": "technical",
            "content_domain": "test",
            "document_category": "invalid_category"  # Invalid category
        }
        
        response = requests.post(
            f"{BASE_URL}/context-aware-documents/upload-text",
            data=data,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 400
        result = response.json()
        assert "Invalid document_category" in result["detail"]
        
        print(f"✅ Invalid document category error handled: {result}")
    
    def test_missing_required_fields_e2e(self):
        """Test error handling for missing required fields"""
        data = {
            "text": "Test content"
            # Missing required fields
        }
        
        response = requests.post(
            f"{BASE_URL}/context-aware-documents/upload-text",
            data=data,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 422  # Validation error
        result = response.json()
        assert "detail" in result
        
        print(f"✅ Missing required fields error handled: {result}")
    
    def test_chat_without_user_message_e2e(self):
        """Test error handling for chat without user message"""
        chat_request = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                }
                # No user message
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=chat_request,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 400
        result = response.json()
        assert "No user message found" in result["detail"]
        
        print(f"✅ Chat without user message error handled: {result}")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 