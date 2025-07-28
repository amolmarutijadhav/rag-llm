#!/usr/bin/env python3
"""
End-to-End (E2E) Test Cases for Enhanced Chat Completion API
Expert QA Engineer Implementation

This test suite covers comprehensive E2E scenarios for the enhanced chat completion
implementation including conversation awareness, strategy patterns, and plugin architecture.
"""

import sys
import os
import time
import json
import requests
from datetime import datetime
from typing import Dict, Any, List

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.core.config import Config

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8000")
ADMIN_API_KEY = os.getenv("CLEAR_ENDPOINT_API_KEY", getattr(Config, "CLEAR_ENDPOINT_API_KEY", "admin-secret-key-change-me"))
CONFIRM_TOKEN = os.getenv("CLEAR_ENDPOINT_CONFIRMATION_TOKEN", getattr(Config, "CLEAR_ENDPOINT_CONFIRMATION_TOKEN", "CONFIRM_DELETE_ALL_DATA"))

class EnhancedChatCompletionE2ETestSuite:
    """Comprehensive E2E test suite for enhanced chat completion"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.test_results = []
        self.start_time = datetime.now()
    
    def log_test_result(self, test_name: str, status: str, details: str = "", duration: float = 0):
        """Log test results with detailed information"""
        result = {
            "test_name": test_name,
            "status": status,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name} - {status}")
        if details:
            print(f"   Details: {details}")
        if duration > 0:
            print(f"   Duration: {duration:.2f}s")
    
    def test_enhanced_chat_completion_basic_functionality(self):
        """Test basic enhanced chat completion functionality"""
        print("\n🔍 Testing Enhanced Chat Completion - Basic Functionality")
        start_time = time.time()
        
        test_request = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant specialized in technology topics."
                },
                {
                    "role": "user",
                    "content": "What is artificial intelligence?"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/enhanced-chat/completions", json=test_request)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate response structure
                required_fields = ["id", "object", "created", "model", "choices", "usage", "sources", "metadata"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log_test_result(
                        "Enhanced Chat Completion Basic",
                        "FAIL",
                        f"Missing required fields: {missing_fields}",
                        duration
                    )
                    return False
                
                # Validate metadata structure
                metadata = result.get("metadata", {})
                expected_metadata_fields = [
                    "conversation_aware", "strategy_used", "enhanced_queries_count",
                    "conversation_context", "processing_plugins"
                ]
                
                metadata_missing = [field for field in expected_metadata_fields if field not in metadata]
                if metadata_missing:
                    self.log_test_result(
                        "Enhanced Chat Completion Basic",
                        "FAIL",
                        f"Missing metadata fields: {metadata_missing}",
                        duration
                    )
                    return False
                
                # Validate conversation awareness
                if not metadata.get("conversation_aware"):
                    self.log_test_result(
                        "Enhanced Chat Completion Basic",
                        "FAIL",
                        "Conversation awareness not enabled",
                        duration
                    )
                    return False
                
                self.log_test_result(
                    "Enhanced Chat Completion Basic",
                    "PASS",
                    f"Response generated successfully. Strategy: {metadata.get('strategy_used')}",
                    duration
                )
                return True
                
            else:
                self.log_test_result(
                    "Enhanced Chat Completion Basic",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Enhanced Chat Completion Basic",
                "FAIL",
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_enhanced_chat_completion_conversation_context(self):
        """Test enhanced chat completion with conversation context"""
        print("\n💬 Testing Enhanced Chat Completion - Conversation Context")
        start_time = time.time()
        
        test_request = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a technical support specialist for SoftwareCorp."
                },
                {
                    "role": "user",
                    "content": "I need help with installing software"
                },
                {
                    "role": "assistant",
                    "content": "I'd be happy to help you with the installation. What specific software are you trying to install?"
                },
                {
                    "role": "user",
                    "content": "It's the new version of Office Suite"
                },
                {
                    "role": "assistant",
                    "content": "Great! Office Suite installation is straightforward. Do you have the installation file downloaded?"
                },
                {
                    "role": "user",
                    "content": "Yes, but I'm getting a permission error"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/enhanced-chat/completions", json=test_request)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                metadata = result.get("metadata", {})
                conversation_context = metadata.get("conversation_context", {})
                
                # Validate conversation context analysis
                expected_context_fields = ["topics", "entities", "context_clues", "conversation_length", "last_user_message"]
                context_missing = [field for field in expected_context_fields if field not in conversation_context]
                
                if context_missing:
                    self.log_test_result(
                        "Enhanced Chat Completion Conversation Context",
                        "FAIL",
                        f"Missing conversation context fields: {context_missing}",
                        duration
                    )
                    return False
                
                # Validate conversation length
                if conversation_context.get("conversation_length") != 6:
                    self.log_test_result(
                        "Enhanced Chat Completion Conversation Context",
                        "FAIL",
                        f"Expected conversation length 6, got {conversation_context.get('conversation_length')}",
                        duration
                    )
                    return False
                
                # Validate last user message
                if conversation_context.get("last_user_message") != "Yes, but I'm getting a permission error":
                    self.log_test_result(
                        "Enhanced Chat Completion Conversation Context",
                        "FAIL",
                        "Last user message not correctly extracted",
                        duration
                    )
                    return False
                
                self.log_test_result(
                    "Enhanced Chat Completion Conversation Context",
                    "PASS",
                    f"Conversation context analyzed successfully. Topics: {conversation_context.get('topics', [])}",
                    duration
                )
                return True
                
            else:
                self.log_test_result(
                    "Enhanced Chat Completion Conversation Context",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Enhanced Chat Completion Conversation Context",
                "FAIL",
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_enhanced_chat_completion_strategy_selection(self):
        """Test enhanced chat completion strategy selection"""
        print("\n🎯 Testing Enhanced Chat Completion - Strategy Selection")
        start_time = time.time()
        
        # Test topic tracking strategy
        topic_request = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Focus on discussing various topics."
                },
                {
                    "role": "user",
                    "content": "Tell me about machine learning and artificial intelligence"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/enhanced-chat/completions", json=topic_request)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                metadata = result.get("metadata", {})
                strategy_used = metadata.get("strategy_used")
                
                if not strategy_used:
                    self.log_test_result(
                        "Enhanced Chat Completion Strategy Selection",
                        "FAIL",
                        "No strategy used in response",
                        duration
                    )
                    return False
                
                # Validate strategy is one of the expected ones
                expected_strategies = ["topic_tracking", "entity_extraction"]
                if strategy_used not in expected_strategies:
                    self.log_test_result(
                        "Enhanced Chat Completion Strategy Selection",
                        "FAIL",
                        f"Unexpected strategy: {strategy_used}",
                        duration
                    )
                    return False
                
                self.log_test_result(
                    "Enhanced Chat Completion Strategy Selection",
                    "PASS",
                    f"Strategy selected successfully: {strategy_used}",
                    duration
                )
                return True
                
            else:
                self.log_test_result(
                    "Enhanced Chat Completion Strategy Selection",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Enhanced Chat Completion Strategy Selection",
                "FAIL",
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_enhanced_chat_completion_multi_query_rag(self):
        """Test enhanced chat completion multi-query RAG processing"""
        print("\n🔍 Testing Enhanced Chat Completion - Multi-Query RAG")
        start_time = time.time()
        
        # First, add some test data
        test_data = {
            "text": "Python is a high-level programming language known for its simplicity and readability. It was created by Guido van Rossum and released in 1991. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming. It has a large standard library and is widely used in web development, data science, artificial intelligence, and automation.",
            "source_name": "python_info"
        }
        
        try:
            # Add test data
            add_response = self.session.post(f"{BASE_URL}/documents/add-text", json=test_data)
            if add_response.status_code != 200:
                self.log_test_result(
                    "Enhanced Chat Completion Multi-Query RAG",
                    "FAIL",
                    "Failed to add test data",
                    0
                )
                return False
            
            # Test enhanced chat completion with RAG
            rag_request = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a programming expert. Use available information to answer questions."
                    },
                    {
                        "role": "user",
                        "content": "What is Python and who created it?"
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = self.session.post(f"{BASE_URL}/enhanced-chat/completions", json=rag_request)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                metadata = result.get("metadata", {})
                sources = result.get("sources", [])
                
                # Validate enhanced queries were generated
                enhanced_queries_count = metadata.get("enhanced_queries_count", 0)
                if enhanced_queries_count == 0:
                    self.log_test_result(
                        "Enhanced Chat Completion Multi-Query RAG",
                        "FAIL",
                        "No enhanced queries generated",
                        duration
                    )
                    return False
                
                # Validate sources were retrieved
                if not sources:
                    self.log_test_result(
                        "Enhanced Chat Completion Multi-Query RAG",
                        "FAIL",
                        "No sources retrieved from RAG",
                        duration
                    )
                    return False
                
                self.log_test_result(
                    "Enhanced Chat Completion Multi-Query RAG",
                    "PASS",
                    f"Multi-query RAG successful. Queries: {enhanced_queries_count}, Sources: {len(sources)}",
                    duration
                )
                return True
                
            else:
                self.log_test_result(
                    "Enhanced Chat Completion Multi-Query RAG",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Enhanced Chat Completion Multi-Query RAG",
                "FAIL",
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_enhanced_chat_completion_error_handling(self):
        """Test enhanced chat completion error handling"""
        print("\n⚠️ Testing Enhanced Chat Completion - Error Handling")
        start_time = time.time()
        
        # Test with empty messages
        empty_request = {
            "model": "gpt-3.5-turbo",
            "messages": [],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/enhanced-chat/completions", json=empty_request)
            duration = time.time() - start_time
            
            if response.status_code == 400:
                result = response.json()
                if "Messages cannot be empty" in result.get("detail", ""):
                    self.log_test_result(
                        "Enhanced Chat Completion Error Handling - Empty Messages",
                        "PASS",
                        "Correctly rejected empty messages",
                        duration
                    )
                else:
                    self.log_test_result(
                        "Enhanced Chat Completion Error Handling - Empty Messages",
                        "FAIL",
                        "Unexpected error message",
                        duration
                    )
                    return False
            else:
                self.log_test_result(
                    "Enhanced Chat Completion Error Handling - Empty Messages",
                    "FAIL",
                    f"Expected 400, got {response.status_code}",
                    duration
                )
                return False
            
            # Test with no user message
            no_user_request = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant."
                    },
                    {
                        "role": "assistant",
                        "content": "Hello! How can I help you?"
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            response = self.session.post(f"{BASE_URL}/enhanced-chat/completions", json=no_user_request)
            duration = time.time() - start_time
            
            if response.status_code == 400:
                result = response.json()
                if "No user message found" in result.get("detail", ""):
                    self.log_test_result(
                        "Enhanced Chat Completion Error Handling - No User Message",
                        "PASS",
                        "Correctly rejected request without user message",
                        duration
                    )
                    return True
                else:
                    self.log_test_result(
                        "Enhanced Chat Completion Error Handling - No User Message",
                        "FAIL",
                        "Unexpected error message",
                        duration
                    )
                    return False
            else:
                self.log_test_result(
                    "Enhanced Chat Completion Error Handling - No User Message",
                    "FAIL",
                    f"Expected 400, got {response.status_code}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Enhanced Chat Completion Error Handling",
                "FAIL",
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_enhanced_chat_completion_strategies_endpoint(self):
        """Test enhanced chat completion strategies endpoint"""
        print("\n📋 Testing Enhanced Chat Completion - Strategies Endpoint")
        start_time = time.time()
        
        try:
            response = self.session.get(f"{BASE_URL}/enhanced-chat/strategies")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate response structure
                if "strategies" not in result or "total" not in result:
                    self.log_test_result(
                        "Enhanced Chat Completion Strategies Endpoint",
                        "FAIL",
                        "Missing required fields in response",
                        duration
                    )
                    return False
                
                strategies = result.get("strategies", [])
                total = result.get("total", 0)
                
                if total != len(strategies):
                    self.log_test_result(
                        "Enhanced Chat Completion Strategies Endpoint",
                        "FAIL",
                        f"Total count mismatch: expected {total}, got {len(strategies)}",
                        duration
                    )
                    return False
                
                # Validate strategy structure
                for strategy in strategies:
                    required_fields = ["name", "description", "features"]
                    missing_fields = [field for field in required_fields if field not in strategy]
                    if missing_fields:
                        self.log_test_result(
                            "Enhanced Chat Completion Strategies Endpoint",
                            "FAIL",
                            f"Strategy missing fields: {missing_fields}",
                            duration
                        )
                        return False
                
                self.log_test_result(
                    "Enhanced Chat Completion Strategies Endpoint",
                    "PASS",
                    f"Retrieved {total} strategies successfully",
                    duration
                )
                return True
                
            else:
                self.log_test_result(
                    "Enhanced Chat Completion Strategies Endpoint",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Enhanced Chat Completion Strategies Endpoint",
                "FAIL",
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_enhanced_chat_completion_plugins_endpoint(self):
        """Test enhanced chat completion plugins endpoint"""
        print("\n🔌 Testing Enhanced Chat Completion - Plugins Endpoint")
        start_time = time.time()
        
        try:
            response = self.session.get(f"{BASE_URL}/enhanced-chat/plugins")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate response structure
                if "plugins" not in result or "total" not in result:
                    self.log_test_result(
                        "Enhanced Chat Completion Plugins Endpoint",
                        "FAIL",
                        "Missing required fields in response",
                        duration
                    )
                    return False
                
                plugins = result.get("plugins", [])
                total = result.get("total", 0)
                
                if total != len(plugins):
                    self.log_test_result(
                        "Enhanced Chat Completion Plugins Endpoint",
                        "FAIL",
                        f"Total count mismatch: expected {total}, got {len(plugins)}",
                        duration
                    )
                    return False
                
                # Validate plugin structure
                expected_plugins = ["conversation_context", "multi_query_rag", "response_enhancement"]
                plugin_names = [plugin.get("name") for plugin in plugins]
                
                for expected_plugin in expected_plugins:
                    if expected_plugin not in plugin_names:
                        self.log_test_result(
                            "Enhanced Chat Completion Plugins Endpoint",
                            "FAIL",
                            f"Missing expected plugin: {expected_plugin}",
                            duration
                        )
                        return False
                
                # Validate plugin structure
                for plugin in plugins:
                    required_fields = ["name", "description", "priority", "features"]
                    missing_fields = [field for field in required_fields if field not in plugin]
                    if missing_fields:
                        self.log_test_result(
                            "Enhanced Chat Completion Plugins Endpoint",
                            "FAIL",
                            f"Plugin missing fields: {missing_fields}",
                            duration
                        )
                        return False
                
                self.log_test_result(
                    "Enhanced Chat Completion Plugins Endpoint",
                    "PASS",
                    f"Retrieved {total} plugins successfully",
                    duration
                )
                return True
                
            else:
                self.log_test_result(
                    "Enhanced Chat Completion Plugins Endpoint",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Enhanced Chat Completion Plugins Endpoint",
                "FAIL",
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_enhanced_chat_completion_performance(self):
        """Test enhanced chat completion performance"""
        print("\n⚡ Testing Enhanced Chat Completion - Performance")
        start_time = time.time()
        
        test_request = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "What is the weather like today?"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/enhanced-chat/completions", json=test_request)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                # Performance thresholds (in seconds)
                acceptable_duration = 30.0  # 30 seconds (enhanced features take longer)
                optimal_duration = 15.0     # 15 seconds
                
                if duration <= optimal_duration:
                    performance_level = "OPTIMAL"
                elif duration <= acceptable_duration:
                    performance_level = "ACCEPTABLE"
                else:
                    performance_level = "SLOW"
                
                self.log_test_result(
                    "Enhanced Chat Completion Performance",
                    "PASS" if duration <= acceptable_duration else "FAIL",
                    f"Response time: {duration:.2f}s ({performance_level})",
                    duration
                )
                return duration <= acceptable_duration
                
            else:
                self.log_test_result(
                    "Enhanced Chat Completion Performance",
                    "FAIL",
                    f"HTTP {response.status_code}: {response.text}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Enhanced Chat Completion Performance",
                "FAIL",
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def test_enhanced_chat_completion_backward_compatibility(self):
        """Test that original chat completion still works"""
        print("\n🔄 Testing Enhanced Chat Completion - Backward Compatibility")
        start_time = time.time()
        
        test_request = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Hello, how are you?"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            # Test original endpoint
            response = self.session.post(f"{BASE_URL}/chat/completions", json=test_request)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Validate original response structure (without enhanced metadata)
                required_fields = ["id", "object", "created", "model", "choices", "usage"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    self.log_test_result(
                        "Enhanced Chat Completion Backward Compatibility",
                        "FAIL",
                        f"Original endpoint missing fields: {missing_fields}",
                        duration
                    )
                    return False
                
                # Ensure enhanced metadata is NOT present in original endpoint
                if "metadata" in result and result["metadata"] is not None:
                    self.log_test_result(
                        "Enhanced Chat Completion Backward Compatibility",
                        "FAIL",
                        "Enhanced metadata should not be present in original endpoint",
                        duration
                    )
                    return False
                
                self.log_test_result(
                    "Enhanced Chat Completion Backward Compatibility",
                    "PASS",
                    "Original endpoint works correctly without enhanced features",
                    duration
                )
                return True
                
            else:
                self.log_test_result(
                    "Enhanced Chat Completion Backward Compatibility",
                    "FAIL",
                    f"Original endpoint failed: HTTP {response.status_code}",
                    duration
                )
                return False
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_test_result(
                "Enhanced Chat Completion Backward Compatibility",
                "FAIL",
                f"Exception: {str(e)}",
                duration
            )
            return False
    
    def run_all_tests(self):
        """Run all E2E tests"""
        print("🚀 Starting Enhanced Chat Completion E2E Test Suite")
        print("=" * 60)
        
        test_methods = [
            self.test_enhanced_chat_completion_basic_functionality,
            self.test_enhanced_chat_completion_conversation_context,
            self.test_enhanced_chat_completion_strategy_selection,
            self.test_enhanced_chat_completion_multi_query_rag,
            self.test_enhanced_chat_completion_error_handling,
            self.test_enhanced_chat_completion_strategies_endpoint,
            self.test_enhanced_chat_completion_plugins_endpoint,
            self.test_enhanced_chat_completion_performance,
            self.test_enhanced_chat_completion_backward_compatibility
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    passed_tests += 1
            except Exception as e:
                self.log_test_result(
                    test_method.__name__,
                    "FAIL",
                    f"Test execution failed: {str(e)}",
                    0
                )
        
        # Generate test summary
        self.generate_test_summary(passed_tests, total_tests)
        
        return passed_tests == total_tests
    
    def generate_test_summary(self, passed_tests: int, total_tests: int):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 ENHANCED CHAT COMPLETION E2E TEST SUMMARY")
        print("=" * 60)
        
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Average Duration: {total_duration/total_tests:.2f}s per test")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_emoji} {result['test_name']} - {result['status']} ({result['duration']:.2f}s)")
            if result['details']:
                print(f"   {result['details']}")
        
        # Save results to file
        self.save_test_results()
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! Enhanced Chat Completion is ready for production.")
        else:
            print(f"\n⚠️ {total_tests - passed_tests} TESTS FAILED. Please review the issues above.")
    
    def save_test_results(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_chat_completion_e2e_results_{timestamp}.json"
        
        results_data = {
            "test_suite": "Enhanced Chat Completion E2E",
            "timestamp": datetime.now().isoformat(),
            "results": self.test_results
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=2)
            print(f"\n💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"\n⚠️ Failed to save test results: {e}")

def main():
    """Main function to run the E2E test suite"""
    print("🧪 Enhanced Chat Completion E2E Test Suite")
    print("Expert QA Engineer Implementation")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding correctly. Please ensure the server is running.")
            return False
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please ensure the server is running at:", BASE_URL)
        return False
    
    # Run test suite
    test_suite = EnhancedChatCompletionE2ETestSuite()
    success = test_suite.run_all_tests()
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 