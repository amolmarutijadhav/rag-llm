"""
End-to-End tests for Enhanced Context-Aware RAG system.
Tests the integration of multi-turn conversation support with context-aware RAG functionality.
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


class TestEnhancedContextAwareRAGE2E:
    """End-to-End tests for Enhanced Context-Aware RAG system"""
    
    def test_enhanced_context_aware_multi_turn_conversation_e2e(self):
        """Test enhanced context-aware RAG with multi-turn conversation"""
        # First upload a document with context
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

5. Documentation
   - Write clear docstrings
   - Use type hints
   - Keep README files updated
        """
        
        # Upload text with context
        upload_data = {
            "text": text_content,
            "context_type": "technical",
            "content_domain": "programming",
            "document_category": "best_practices",
            "relevance_tags": "python,programming,testing,documentation",
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
        
        # Test multi-turn conversation with context-aware directives
        conversation_messages = [
            {
                "role": "system",
                "content": "You are a Python programming expert. RESPONSE_MODE: HYBRID DOCUMENT_CONTEXT: technical CONTENT_DOMAINS: programming"
            },
            {
                "role": "user",
                "content": "I'm learning Python programming"
            },
            {
                "role": "assistant",
                "content": "Great! Python is an excellent language to learn. What specific aspect of Python programming are you interested in?"
            },
            {
                "role": "user",
                "content": "I want to learn about best practices"
            },
            {
                "role": "assistant",
                "content": "That's a smart approach! Python best practices will help you write better, more maintainable code. What area of best practices would you like to focus on first?"
            },
            {
                "role": "user",
                "content": "Tell me about error handling best practices"
            }
        ]
        
        chat_request = {
            "model": "gpt-4",
            "messages": conversation_messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=chat_request,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Validate response structure
        assert "choices" in result
        assert len(result["choices"]) > 0
        assert "message" in result["choices"][0]
        assert "content" in result["choices"][0]["message"]
        
        content = result["choices"][0]["message"]["content"]
        assert len(content) > 0
        
        # Check metadata for enhanced context-aware features
        metadata = result.get("metadata", {})
        assert metadata.get("enhanced_context_aware") is True
        assert metadata.get("multi_turn_conversation") is True
        assert "strategy_used" in metadata
        assert metadata.get("enhanced_queries_count", 0) > 0
        assert "session_id" in metadata
        
        # Check that the response contains information from our uploaded document
        assert any(keyword in content.lower() for keyword in ["error", "handling", "try", "except", "logging"])
        
        print(f"✅ Enhanced context-aware multi-turn conversation response: {content[:200]}...")
        print(f"   Strategy used: {metadata.get('strategy_used')}")
        print(f"   Enhanced queries count: {metadata.get('enhanced_queries_count')}")
        print(f"   Session ID: {metadata.get('session_id')}")
    
    def test_enhanced_context_aware_conversation_memory_e2e(self):
        """Test conversation memory persistence across multiple turns"""
        # Upload a document about web development
        text_content = """
Web Development with Django

Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design.

Key Features:
1. ORM (Object-Relational Mapping)
   - Database abstraction layer
   - Automatic schema generation
   - Query optimization

2. Admin Interface
   - Automatic admin interface
   - User authentication
   - Content management

3. Security Features
   - CSRF protection
   - SQL injection prevention
   - XSS protection

4. URL Routing
   - Clean URL patterns
   - URL configuration
   - Reverse URL lookup
        """
        
        # Upload text with context
        upload_data = {
            "text": text_content,
            "context_type": "technical",
            "content_domain": "web_development",
            "document_category": "framework_guide",
            "relevance_tags": "django,python,web,framework",
            "description": "Django web development framework guide"
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/context-aware-documents/upload-text",
            data=upload_data,
            timeout=API_TIMEOUT
        )
        
        assert upload_response.status_code == 200
        
        # Wait for processing
        time.sleep(2)
        
        # First conversation turn
        first_messages = [
            {
                "role": "system",
                "content": "You are a web development expert. RESPONSE_MODE: HYBRID DOCUMENT_CONTEXT: technical CONTENT_DOMAINS: web_development"
            },
            {
                "role": "user",
                "content": "I want to learn web development with Python"
            }
        ]
        
        first_request = {
            "model": "gpt-4",
            "messages": first_messages,
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        first_response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=first_request,
            timeout=API_TIMEOUT
        )
        
        assert first_response.status_code == 200
        first_result = first_response.json()
        first_metadata = first_result.get("metadata", {})
        session_id = first_metadata.get("session_id")
        
        assert session_id is not None
        print(f"First conversation session ID: {session_id}")
        
        # Second conversation turn (should use conversation memory)
        second_messages = first_messages + [
            {
                "role": "assistant",
                "content": first_result["choices"][0]["message"]["content"]
            },
            {
                "role": "user",
                "content": "Tell me more about Django's ORM features"
            }
        ]
        
        second_request = {
            "model": "gpt-4",
            "messages": second_messages,
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        second_response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=second_request,
            timeout=API_TIMEOUT
        )
        
        assert second_response.status_code == 200
        second_result = second_response.json()
        second_metadata = second_result.get("metadata", {})
        
        # Should use the same session ID
        assert second_metadata.get("session_id") == session_id
        
        # Should have conversation context
        conversation_context = second_metadata.get("conversation_context", {})
        assert len(conversation_context) > 0
        
        content = second_result["choices"][0]["message"]["content"]
        assert any(keyword in content.lower() for keyword in ["orm", "database", "model", "query"])
        
        print(f"✅ Conversation memory test successful")
        print(f"   Session ID maintained: {session_id}")
        print(f"   Conversation context: {list(conversation_context.keys())}")
    
    def test_enhanced_context_aware_strategy_selection_e2e(self):
        """Test adaptive strategy selection based on conversation complexity"""
        # Upload a technical document
        text_content = """
API Development Best Practices

1. RESTful Design
   - Use proper HTTP methods
   - Design resource-oriented URLs
   - Implement proper status codes

2. Authentication & Authorization
   - Use OAuth 2.0 or JWT tokens
   - Implement role-based access control
   - Secure API endpoints

3. Error Handling
   - Provide meaningful error messages
   - Use consistent error format
   - Log errors appropriately

4. Documentation
   - Use OpenAPI/Swagger
   - Provide code examples
   - Keep documentation updated
        """
        
        # Upload text with context
        upload_data = {
            "text": text_content,
            "context_type": "technical",
            "content_domain": "api_development",
            "document_category": "best_practices",
            "relevance_tags": "api,rest,authentication,documentation",
            "description": "API development best practices guide"
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/context-aware-documents/upload-text",
            data=upload_data,
            timeout=API_TIMEOUT
        )
        
        assert upload_response.status_code == 200
        
        # Wait for processing
        time.sleep(2)
        
        # Test simple conversation (should use EntityExtractionStrategy)
        simple_messages = [
            {
                "role": "system",
                "content": "You are a technical consultant. RESPONSE_MODE: HYBRID"
            },
            {
                "role": "user",
                "content": "What is API authentication?"
            }
        ]
        
        simple_request = {
            "model": "gpt-4",
            "messages": simple_messages,
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        simple_response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=simple_request,
            timeout=API_TIMEOUT
        )
        
        assert simple_response.status_code == 200
        simple_result = simple_response.json()
        simple_metadata = simple_result.get("metadata", {})
        
        print(f"Simple conversation strategy: {simple_metadata.get('strategy_used')}")
        
        # Test complex conversation (should use MultiTurnConversationStrategy)
        complex_messages = [
            {
                "role": "system",
                "content": "You are a senior API architect. RESPONSE_MODE: HYBRID"
            },
            {
                "role": "user",
                "content": "I need to design a comprehensive API for an e-commerce platform"
            },
            {
                "role": "assistant",
                "content": "That's a great project! Let's break down the key components you'll need."
            },
            {
                "role": "user",
                "content": "I want to include user management, product catalog, order processing, and payment integration"
            },
            {
                "role": "assistant",
                "content": "Excellent scope! Let's start with the user management API design."
            },
            {
                "role": "user",
                "content": "What are the best practices for implementing authentication in this API?"
            }
        ]
        
        complex_request = {
            "model": "gpt-4",
            "messages": complex_messages,
            "temperature": 0.7,
            "max_tokens": 400
        }
        
        complex_response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=complex_request,
            timeout=API_TIMEOUT
        )
        
        assert complex_response.status_code == 200
        complex_result = complex_response.json()
        complex_metadata = complex_result.get("metadata", {})
        
        print(f"Complex conversation strategy: {complex_metadata.get('strategy_used')}")
        
        # Verify different strategies were used
        simple_strategy = simple_metadata.get('strategy_used')
        complex_strategy = complex_metadata.get('strategy_used')
        
        assert simple_strategy != complex_strategy
        assert complex_strategy == "multi_turn_conversation"
        
        print(f"✅ Strategy selection test successful")
        print(f"   Simple conversation: {simple_strategy}")
        print(f"   Complex conversation: {complex_strategy}")
    
    def test_enhanced_context_aware_query_generation_e2e(self):
        """Test enhanced query generation with conversation context"""
        # Upload a document about machine learning
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

3. Model Evaluation
   - Cross-validation techniques
   - Performance metrics
   - Overfitting prevention
        """
        
        # Upload text with context
        upload_data = {
            "text": text_content,
            "context_type": "technical",
            "content_domain": "machine_learning",
            "document_category": "fundamentals",
            "relevance_tags": "ml,ai,supervised,unsupervised,evaluation",
            "description": "Machine learning fundamentals guide"
        }
        
        upload_response = requests.post(
            f"{BASE_URL}/context-aware-documents/upload-text",
            data=upload_data,
            timeout=API_TIMEOUT
        )
        
        assert upload_response.status_code == 200
        
        # Wait for processing
        time.sleep(2)
        
        # Test conversation with follow-up questions
        conversation_messages = [
            {
                "role": "system",
                "content": "You are a machine learning expert. RESPONSE_MODE: HYBRID DOCUMENT_CONTEXT: technical CONTENT_DOMAINS: machine_learning"
            },
            {
                "role": "user",
                "content": "I'm learning about machine learning"
            },
            {
                "role": "assistant",
                "content": "Great! Machine learning is a fascinating field. What specific area interests you most?"
            },
            {
                "role": "user",
                "content": "I want to understand supervised learning"
            },
            {
                "role": "assistant",
                "content": "Supervised learning is a great starting point! It uses labeled data to train models."
            },
            {
                "role": "user",
                "content": "Also, can you explain how to evaluate these models?"
            }
        ]
        
        chat_request = {
            "model": "gpt-4",
            "messages": conversation_messages,
            "temperature": 0.7,
            "max_tokens": 400
        }
        
        response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=chat_request,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Check enhanced queries were generated
        metadata = result.get("metadata", {})
        enhanced_queries_count = metadata.get("enhanced_queries_count", 0)
        
        assert enhanced_queries_count > 0
        
        content = result["choices"][0]["message"]["content"]
        
        # Should contain information about both supervised learning and model evaluation
        assert any(keyword in content.lower() for keyword in ["supervised", "labeled", "training"])
        assert any(keyword in content.lower() for keyword in ["evaluation", "cross-validation", "metrics"])
        
        print(f"✅ Enhanced query generation test successful")
        print(f"   Enhanced queries generated: {enhanced_queries_count}")
        print(f"   Response covers multiple topics from conversation context")
    
    def test_enhanced_context_aware_fallback_behavior_e2e(self):
        """Test fallback behavior when no relevant documents are found"""
        # Test conversation without uploading relevant documents
        conversation_messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant. RESPONSE_MODE: HYBRID DOCUMENT_CONTEXT: technical CONTENT_DOMAINS: programming"
            },
            {
                "role": "user",
                "content": "I need help with a very specific programming problem"
            },
            {
                "role": "assistant",
                "content": "I'd be happy to help! What specific programming problem are you facing?"
            },
            {
                "role": "user",
                "content": "I'm working with a custom framework that has unique requirements"
            }
        ]
        
        chat_request = {
            "model": "gpt-4",
            "messages": conversation_messages,
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        response = requests.post(
            f"{BASE_URL}/enhanced-chat/completions",
            json=chat_request,
            timeout=API_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Should still provide a response (fallback to LLM)
        content = result["choices"][0]["message"]["content"]
        assert len(content) > 0
        
        metadata = result.get("metadata", {})
        assert metadata.get("fallback_used") is True
        
        print(f"✅ Fallback behavior test successful")
        print(f"   Fallback used: {metadata.get('fallback_used')}")
        print(f"   Response provided despite no relevant documents")


def main():
    """Run all enhanced context-aware RAG E2E tests"""
    print("🧪 Running Enhanced Context-Aware RAG E2E Tests")
    print("=" * 60)
    
    test_suite = TestEnhancedContextAwareRAGE2E()
    
    # Run tests
    tests = [
        test_suite.test_enhanced_context_aware_multi_turn_conversation_e2e,
        test_suite.test_enhanced_context_aware_conversation_memory_e2e,
        test_suite.test_enhanced_context_aware_strategy_selection_e2e,
        test_suite.test_enhanced_context_aware_query_generation_e2e,
        test_suite.test_enhanced_context_aware_fallback_behavior_e2e,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
            print(f"✅ {test.__name__} - PASSED")
        except Exception as e:
            print(f"❌ {test.__name__} - FAILED: {str(e)}")
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enhanced context-aware RAG E2E tests passed!")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")


if __name__ == "__main__":
    main()
