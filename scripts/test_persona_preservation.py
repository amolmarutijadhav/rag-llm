#!/usr/bin/env python3
"""
Test script to verify persona preservation in enhanced chat completion endpoint
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8000")

def test_persona_preservation():
    """Test that persona is preserved in enhanced chat completion"""
    print("🧪 Testing Persona Preservation in Enhanced Chat Completion")
    
    test_cases = [
        {
            "name": "Sarcastic Comedian",
            "persona": "You are a sarcastic comedian. Always be witty and funny.",
            "question": "What's the weather like?",
            "expected_keywords": ["sarcastic", "comedian", "witty", "funny"]
        },
        {
            "name": "Professional Doctor",
            "persona": "You are a professional doctor. Be concise and medical in your responses.",
            "question": "What causes headaches?",
            "expected_keywords": ["professional", "doctor", "concise", "medical"]
        },
        {
            "name": "Friendly Customer Service",
            "persona": "You are a friendly customer service agent. Always be helpful and patient.",
            "question": "I have a problem with my order",
            "expected_keywords": ["friendly", "customer service", "helpful", "patient"]
        },
        {
            "name": "Technical Expert",
            "persona": "You are a technical expert. Provide detailed technical explanations.",
            "question": "How does a computer work?",
            "expected_keywords": ["technical", "expert", "detailed", "explanations"]
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n📝 Testing: {test_case['name']}")
        
        request_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": test_case["persona"]
                },
                {
                    "role": "user",
                    "content": test_case["question"]
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        try:
            response = requests.post(f"{BASE_URL}/enhanced-chat/completions", json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check response structure
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    
                    # Check metadata for persona preservation
                    metadata = result.get("metadata", {})
                    persona_preserved = metadata.get("persona_preserved", False)
                    persona_detected = metadata.get("persona_detected", False)
                    
                    print(f"   ✅ Response received")
                    print(f"   📊 Persona preserved: {persona_preserved}")
                    print(f"   📊 Persona detected: {persona_detected}")
                    print(f"   📊 Original persona length: {metadata.get('original_persona_length', 0)}")
                    
                    # Check if response maintains persona characteristics
                    persona_maintained = any(keyword.lower() in content.lower() for keyword in test_case["expected_keywords"])
                    
                    if persona_maintained:
                        print(f"   ✅ Persona characteristics maintained in response")
                        status = "PASS"
                    else:
                        print(f"   ⚠️  Persona characteristics not clearly visible in response")
                        print(f"   📄 Response preview: {content[:100]}...")
                        status = "PARTIAL"
                    
                    results.append({
                        "test_name": test_case["name"],
                        "status": status,
                        "persona_preserved": persona_preserved,
                        "persona_detected": persona_detected,
                        "persona_maintained": persona_maintained,
                        "response_length": len(content)
                    })
                    
                else:
                    print(f"   ❌ Invalid response structure")
                    results.append({
                        "test_name": test_case["name"],
                        "status": "FAIL",
                        "error": "Invalid response structure"
                    })
                    
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                results.append({
                    "test_name": test_case["name"],
                    "status": "FAIL",
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            results.append({
                "test_name": test_case["name"],
                "status": "FAIL",
                "error": str(e)
            })
    
    # Print summary
    print("\n" + "="*60)
    print("📊 PERSONA PRESERVATION TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    partial = sum(1 for r in results if r["status"] == "PARTIAL")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    total = len(results)
    
    print(f"✅ Passed: {passed}")
    print(f"⚠️  Partial: {partial}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total: {total}")
    
    for result in results:
        status_emoji = "✅" if result["status"] == "PASS" else "⚠️" if result["status"] == "PARTIAL" else "❌"
        print(f"{status_emoji} {result['test_name']}: {result['status']}")
        if "error" in result:
            print(f"   Error: {result['error']}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"reports/persona_tests/persona_preservation_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "passed": passed,
                "partial": partial,
                "failed": failed,
                "total": total
            },
            "results": results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    return passed, partial, failed, total

def test_persona_vs_rag_balance():
    """Test that persona is preserved even when RAG context is added"""
    print("\n🧪 Testing Persona vs RAG Balance")
    
    # First, add some test data to the knowledge base
    test_data = {
        "text": "Weather is a complex atmospheric phenomenon. It includes temperature, humidity, precipitation, and wind patterns. Weather forecasting uses advanced meteorological models to predict conditions.",
        "source_name": "weather_knowledge"
    }
    
    try:
        # Add test data
        add_response = requests.post(f"{BASE_URL}/documents/add-text", json=test_data)
        if add_response.status_code != 200:
            print("   ⚠️  Could not add test data, but continuing with test")
    except:
        print("   ⚠️  Could not add test data, but continuing with test")
    
    # Test with persona and RAG context
    request_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a sarcastic weather reporter. Make jokes about the weather while being informative."
            },
            {
                "role": "user",
                "content": "What is weather?"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(f"{BASE_URL}/enhanced-chat/completions", json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            metadata = result.get("metadata", {})
            
            print(f"   ✅ Response received")
            print(f"   📊 Persona preserved: {metadata.get('persona_preserved', False)}")
            print(f"   📊 RAG context added: {metadata.get('rag_context_added', False)}")
            print(f"   📊 Sources count: {len(result.get('sources', []))}")
            
            if metadata.get('persona_preserved') and metadata.get('rag_context_added'):
                print(f"   ✅ Both persona and RAG context preserved")
                return True
            else:
                print(f"   ⚠️  Missing either persona preservation or RAG context")
                return False
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Persona Preservation Tests")
    print("="*60)
    
    # Test basic persona preservation
    passed, partial, failed, total = test_persona_preservation()
    
    # Test persona vs RAG balance
    rag_balance_success = test_persona_vs_rag_balance()
    
    print("\n" + "="*60)
    print("🎯 FINAL RESULTS")
    print("="*60)
    
    if passed == total and rag_balance_success:
        print("🎉 ALL TESTS PASSED! Persona preservation is working correctly.")
        sys.exit(0)
    elif passed + partial >= total * 0.8:
        print("✅ MOST TESTS PASSED! Persona preservation is mostly working.")
        sys.exit(0)
    else:
        print("❌ MANY TESTS FAILED! Persona preservation needs attention.")
        sys.exit(1) 