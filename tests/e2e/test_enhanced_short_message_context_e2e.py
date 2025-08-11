"""
End-to-End test for enhanced short message context processing.
Demonstrates how the system handles one-word responses in multi-turn conversations.
"""

import pytest
import requests
import time
from tests.utils.provider_test_helpers import patch_all_providers

BASE_URL = "http://localhost:8000"
API_TIMEOUT = 30


class TestEnhancedShortMessageContextE2E:
    """End-to-End tests for enhanced short message context processing"""
    
    def test_short_message_context_preservation(self):
        """Test that short messages maintain conversation context"""
        print("\n🧪 Testing Enhanced Short Message Context Preservation")
        
        # Test conversation with short responses
        conversation_messages = [
            {
                "role": "system",
                "content": "You are a helpful technical assistant. Provide detailed, contextual responses."
            },
            {
                "role": "user",
                "content": "I need help with Python API development"
            },
            {
                "role": "assistant",
                "content": "I'd be happy to help you with Python API development! What specific aspect are you working on - authentication, data handling, or something else?"
            },
            {
                "role": "user",
                "content": "Authentication"
            },
            {
                "role": "assistant",
                "content": "Great! Python API authentication can be implemented in several ways. Are you looking to use OAuth, JWT tokens, or API keys?"
            },
            {
                "role": "user",
                "content": "JWT"
            },
            {
                "role": "assistant",
                "content": "JWT authentication is a popular choice! Do you want to implement JWT token generation, validation, or both?"
            },
            {
                "role": "user",
                "content": "Both"
            }
        ]
        
        chat_request = {
            "model": "gpt-3.5-turbo",
            "messages": conversation_messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
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
            
            # Check metadata for enhanced context features
            metadata = result.get("metadata", {})
            assert metadata.get("conversation_aware") is True
            assert metadata.get("enhanced_queries_count", 0) > 0
            
            # Verify that the response maintains context from the conversation
            # The response should mention JWT, authentication, and Python API
            content_lower = content.lower()
            context_keywords = ["jwt", "authentication", "python", "api", "token"]
            context_found = sum(1 for keyword in context_keywords if keyword in content_lower)
            
            # Should find at least 3 context keywords
            assert context_found >= 3, f"Expected at least 3 context keywords, found {context_found}"
            
            print(f"✅ Enhanced short message context test passed!")
            print(f"   Response: {content[:200]}...")
            print(f"   Context keywords found: {context_found}")
            print(f"   Enhanced queries count: {metadata.get('enhanced_queries_count')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Enhanced short message context test failed: {str(e)}")
            return False
    
    def test_one_word_response_context(self):
        """Test handling of one-word responses like 'Yes', 'No', 'Why'"""
        print("\n🧪 Testing One-Word Response Context Handling")
        
        # Test conversation with one-word responses
        conversation_messages = [
            {
                "role": "system",
                "content": "You are a helpful technical assistant. Provide detailed, contextual responses."
            },
            {
                "role": "user",
                "content": "Can you help me with machine learning?"
            },
            {
                "role": "assistant",
                "content": "Absolutely! Machine learning is a broad field. Are you interested in supervised learning, unsupervised learning, or deep learning?"
            },
            {
                "role": "user",
                "content": "Supervised"
            },
            {
                "role": "assistant",
                "content": "Great choice! Supervised learning involves training models with labeled data. Do you want to work with classification or regression problems?"
            },
            {
                "role": "user",
                "content": "Classification"
            },
            {
                "role": "assistant",
                "content": "Classification is perfect! Would you like to use algorithms like Random Forest, Support Vector Machines, or Neural Networks?"
            },
            {
                "role": "user",
                "content": "Why"
            }
        ]
        
        chat_request = {
            "model": "gpt-3.5-turbo",
            "messages": conversation_messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/enhanced-chat/completions",
                json=chat_request,
                timeout=API_TIMEOUT
            )
            
            assert response.status_code == 200
            result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            
            # Verify that the response to "Why" maintains context
            # Should explain why one might choose different algorithms
            content_lower = content.lower()
            context_keywords = ["algorithm", "classification", "supervised", "learning", "random", "forest", "svm", "neural"]
            context_found = sum(1 for keyword in context_keywords if keyword in content_lower)
            
            # Should find at least 4 context keywords
            assert context_found >= 4, f"Expected at least 4 context keywords, found {context_found}"
            
            print(f"✅ One-word response context test passed!")
            print(f"   Response to 'Why': {content[:200]}...")
            print(f"   Context keywords found: {context_found}")
            
            return True
            
        except Exception as e:
            print(f"❌ One-word response context test failed: {str(e)}")
            return False
    
    def test_yes_no_response_context(self):
        """Test handling of yes/no responses"""
        print("\n🧪 Testing Yes/No Response Context Handling")
        
        # Test conversation with yes/no responses
        conversation_messages = [
            {
                "role": "system",
                "content": "You are a helpful technical assistant. Provide detailed, contextual responses."
            },
            {
                "role": "user",
                "content": "I'm building a web application with React"
            },
            {
                "role": "assistant",
                "content": "Excellent! React is a great choice for web development. Are you planning to use a state management solution like Redux or Context API?"
            },
            {
                "role": "user",
                "content": "Yes"
            },
            {
                "role": "assistant",
                "content": "Great! For state management, would you prefer Redux for complex state or Context API for simpler state management?"
            },
            {
                "role": "user",
                "content": "Redux"
            },
            {
                "role": "assistant",
                "content": "Redux is powerful for complex applications! Do you want to set up Redux Toolkit for easier configuration?"
            },
            {
                "role": "user",
                "content": "No"
            }
        ]
        
        chat_request = {
            "model": "gpt-3.5-turbo",
            "messages": conversation_messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/enhanced-chat/completions",
                json=chat_request,
                timeout=API_TIMEOUT
            )
            
            assert response.status_code == 200
            result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            
            # Verify that the response to "No" maintains context
            # Should provide alternatives or explain why not to use Redux Toolkit
            content_lower = content.lower()
            context_keywords = ["redux", "toolkit", "react", "state", "management", "alternative", "setup"]
            context_found = sum(1 for keyword in context_keywords if keyword in content_lower)
            
            # Should find at least 3 context keywords
            assert context_found >= 3, f"Expected at least 3 context keywords, found {context_found}"
            
            print(f"✅ Yes/No response context test passed!")
            print(f"   Response to 'No': {content[:200]}...")
            print(f"   Context keywords found: {context_found}")
            
            return True
            
        except Exception as e:
            print(f"❌ Yes/No response context test failed: {str(e)}")
            return False


def main():
    """Run all enhanced short message context E2E tests"""
    print("🧪 Running Enhanced Short Message Context E2E Tests")
    print("=" * 60)
    
    test_suite = TestEnhancedShortMessageContextE2E()
    
    tests = [
        test_suite.test_short_message_context_preservation,
        test_suite.test_one_word_response_context,
        test_suite.test_yes_no_response_context
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All enhanced short message context E2E tests passed!")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    main()
