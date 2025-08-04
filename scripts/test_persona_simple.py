#!/usr/bin/env python3
"""
Simple test script to verify persona preservation in enhanced chat completion service
"""

import asyncio
import sys
import os
from unittest.mock import Mock, AsyncMock

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.domain.models.requests import ChatCompletionRequest, ChatMessage
from app.domain.services.enhanced_chat_completion_service import EnhancedChatCompletionService
from app.domain.services.rag_service import RAGService


async def test_persona_preservation():
    """Test persona preservation in the enhanced chat completion service"""
    print("🧪 Testing Persona Preservation in Enhanced Chat Completion Service")
    print("=" * 70)
    
    # Create mock services
    mock_rag_service = Mock(spec=RAGService)
    mock_rag_service.search_documents = AsyncMock(return_value=[])
    mock_rag_service.ask_question = AsyncMock(return_value={
        "success": True,
        "sources": [],
        "answer": "Mock answer"
    })
    
    mock_llm_provider = Mock()
    
    def mock_llm_call(**kwargs):
        # Handle return_full_response parameter
        return_full_response = kwargs.get('return_full_response', False)
        
        if return_full_response:
            return {
                "choices": [{
                    "message": {
                        "content": "Hello! I'm responding based on the persona you provided."
                    }
                }],
                "usage": {"total_tokens": 50}
            }
        else:
            return {
                "content": "Hello! I'm responding based on the persona you provided.",
                "usage": {"total_tokens": 50}
            }
    
    mock_llm_provider.call_llm_api = AsyncMock(side_effect=mock_llm_call)
    
    # Create the service
    service = EnhancedChatCompletionService(mock_rag_service, mock_llm_provider)
    
    # Test cases with different personas
    test_cases = [
        {
            "name": "Professional Doctor",
            "system_message": "You are a professional doctor. Be concise and medical.",
            "user_message": "Hello, I have a headache."
        },
        {
            "name": "Sarcastic Comedian", 
            "system_message": "You are a sarcastic comedian. Be witty and funny.",
            "user_message": "Tell me a joke."
        },
        {
            "name": "Friendly Customer Service",
            "system_message": "You are a friendly customer service agent. Be helpful and warm.",
            "user_message": "I need help with my order."
        },
        {
            "name": "Technical Expert",
            "system_message": "You are a technical expert. Be precise and detailed.",
            "user_message": "Explain how APIs work."
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"📝 Testing: {test_case['name']}")
        
        # Create request
        request = ChatCompletionRequest(
            model="gpt-3.5-turbo",
            messages=[
                ChatMessage(role="system", content=test_case["system_message"]),
                ChatMessage(role="user", content=test_case["user_message"])
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        try:
            # Process request
            response = await service.process_request(request)
            

            
            # Check if persona was preserved
            persona_preserved = response.metadata.get("persona_preserved", False)
            persona_detected = response.metadata.get("persona_detected", False)
            original_persona_length = response.metadata.get("original_persona_length", 0)
            
            # Check if LLM was called
            llm_calls = mock_llm_provider.call_llm_api.call_args_list
            llm_was_called = len(llm_calls) > 0
            
            # Verify persona is preserved in metadata
            result = {
                "name": test_case["name"],
                "status": "PASS" if persona_preserved and persona_detected and llm_was_called else "FAIL",
                "persona_preserved": persona_preserved,
                "persona_detected": persona_detected,
                "persona_length": original_persona_length,
                "llm_was_called": llm_was_called,
                "response_content": response.choices[0]["message"]["content"] if response.choices else "No response"
            }
        except Exception as e:
            print(f"      Exception occurred: {str(e)}")
            print(f"      Exception type: {type(e).__name__}")
            import traceback
            print(f"      Traceback: {traceback.format_exc()}")
            
            result = {
                "name": test_case["name"],
                "status": "FAIL",
                "error": str(e),
                "persona_preserved": False,
                "persona_detected": False,
                "persona_length": 0,
                "llm_was_called": False,
                "response_content": "Error occurred"
            }
                
        except Exception as e:
            result = {
                "name": test_case["name"],
                "status": "FAIL",
                "error": str(e),
                "persona_preserved": False,
                "persona_detected": False,
                "persona_length": 0,
                "llm_was_called": False,
                "response_content": "Error occurred"
            }
        
        results.append(result)
        
        # Print result
        if result["status"] == "PASS":
            print(f"   ✅ PASS - Persona preserved and detected")
            print(f"      Persona length: {result['persona_length']}")
            print(f"      LLM was called: {result['llm_was_called']}")
        else:
            print(f"   ❌ FAIL - {result.get('error', 'Persona not preserved')}")
            print(f"      Persona preserved: {result['persona_preserved']}")
            print(f"      Persona detected: {result['persona_detected']}")
            print(f"      LLM was called: {result['llm_was_called']}")
        
        print()
    
    # Summary
    print("=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {len(results)}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Persona preservation is working correctly.")
    else:
        print(f"\n⚠️  {failed} TESTS FAILED! Persona preservation needs attention.")
    
    return results


async def main():
    """Main function"""
    print("🚀 Starting Simple Persona Preservation Tests")
    print("=" * 70)
    
    results = await test_persona_preservation()
    
    print("\n" + "=" * 70)
    print("🎯 FINAL RESULTS")
    print("=" * 70)
    
    if all(r["status"] == "PASS" for r in results):
        print("✅ ALL TESTS PASSED! Persona preservation is working correctly.")
    else:
        print("❌ SOME TESTS FAILED! Persona preservation needs attention.")


if __name__ == "__main__":
    asyncio.run(main()) 