#!/usr/bin/env python3
"""
End-to-end tests for document processing workflow
"""

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import requests
import json
import tempfile
from datetime import datetime
from io import BytesIO
from app.core.config import Config

BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8000")
ADMIN_API_KEY = os.getenv("CLEAR_ENDPOINT_API_KEY", getattr(Config, "CLEAR_ENDPOINT_API_KEY", "admin-secret-key-change-me"))
CONFIRM_TOKEN = os.getenv("CLEAR_ENDPOINT_CONFIRMATION_TOKEN", getattr(Config, "CLEAR_ENDPOINT_CONFIRMATION_TOKEN", "CONFIRM_DELETE_ALL_DATA"))

def create_comprehensive_test_document():
    """Create a comprehensive test document with various content types"""
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as temp_file:
        temp_file.write("Comprehensive Document Processing Test\n")
        temp_file.write("=" * 50 + "\n\n")
        temp_file.write("1. Introduction\n")
        temp_file.write("This document tests the complete document processing workflow.\n")
        temp_file.write("It includes various sections to test chunking and retrieval.\n\n")
        temp_file.write("2. Technical Details\n")
        temp_file.write("The system processes documents through several stages:\n")
        temp_file.write("- Document upload and validation\n")
        temp_file.write("- Text extraction and preprocessing\n")
        temp_file.write("- Chunking into smaller segments\n")
        temp_file.write("- Vector embedding generation\n")
        temp_file.write("- Storage in vector database\n\n")
        temp_file.write("3. OCR Capabilities\n")
        temp_file.write("The system supports OCR for extracting text from images.\n")
        temp_file.write("This includes PDF and DOCX documents with embedded images.\n")
        temp_file.write("Tesseract OCR engine is used for text extraction.\n\n")
        temp_file.write("4. Search and Retrieval\n")
        temp_file.write("Documents are indexed for semantic search.\n")
        temp_file.write("Questions can be asked about uploaded content.\n")
        temp_file.write("Relevant chunks are retrieved and used for answers.\n\n")
        temp_file.write("5. Conclusion\n")
        temp_file.write("This comprehensive test validates the entire workflow.\n")
        temp_file.write("From upload to retrieval, all components are tested.\n")
        return temp_file.name

def test_complete_document_workflow():
    """Test complete document processing workflow"""
    print("🔄 Testing complete document processing workflow...")
    
    doc_path = create_comprehensive_test_document()
    
    try:
        # Step 1: Upload document
        print("   📤 Step 1: Uploading document...")
        with open(doc_path, 'rb') as f:
            files = {"file": ("comprehensive_test.txt", f, "text/plain")}
            upload_response = requests.post(f"{BASE_URL}/documents/upload", files=files)
        
        if upload_response.status_code != 200:
            print(f"   ❌ Upload failed: {upload_response.text}")
            return False
        
        upload_result = upload_response.json()
        print(f"   ✅ Upload successful: {upload_result.get('chunks_processed', 0)} chunks processed")
        
        # Step 2: Verify document was processed
        print("   📊 Step 2: Checking document processing...")
        stats_response = requests.get(f"{BASE_URL}/questions/stats")
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"   ✅ Stats retrieved: {json.dumps(stats, indent=2)}")
        else:
            print(f"   ⚠️ Stats failed: {stats_response.text}")
        
        # Step 3: Test various questions
        print("   ❓ Step 3: Testing question answering...")
        
        questions = [
            "What are the main stages of document processing?",
            "What OCR capabilities does the system have?",
            "How does the search and retrieval work?",
            "What is the conclusion of the document?"
        ]
        
        for i, question in enumerate(questions, 1):
            question_data = {
                "question": question,
                "top_k": 3
            }
            
            q_response = requests.post(
                f"{BASE_URL}/questions/ask",
                json=question_data,
                headers={"Content-Type": "application/json"}
            )
            
            if q_response.status_code == 200:
                result = q_response.json()
                print(f"   ✅ Q{i}: {question}")
                print(f"      Answer: {result.get('answer', 'N/A')[:100]}...")
            else:
                print(f"   ❌ Q{i} failed: {q_response.text}")
        
        # Step 4: Test chat completions
        print("   💬 Step 4: Testing chat completions...")
        
        chat_data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that can answer questions about uploaded documents."
                },
                {
                    "role": "user",
                    "content": "Summarize the main capabilities of this document processing system."
                }
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        chat_response = requests.post(
            f"{BASE_URL}/chat/completions",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        
        if chat_response.status_code == 200:
            result = chat_response.json()
            print("   ✅ Chat completions working")
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                print(f"   Response: {content[:150]}...")
        else:
            print(f"   ❌ Chat completions failed: {chat_response.text}")
        
        # Step 5: Clear documents
        print("   🗑️ Step 5: Clearing documents...")
        
        clear_response = requests.delete(
            f"{BASE_URL}/documents/clear-secure",
            headers={"Authorization": f"Bearer {ADMIN_API_KEY}", "Content-Type": "application/json"},
            json={"confirmation_token": CONFIRM_TOKEN, "reason": "E2E workflow cleanup"}
        )
        
        if clear_response.status_code == 200:
            print("   ✅ Documents cleared successfully")
        else:
            print(f"   ❌ Clear failed: {clear_response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Complete workflow test - Error: {e}")
        return False
    finally:
        # Clean up temporary file
        try:
            os.unlink(doc_path)
        except:
            pass

def test_multiple_document_types():
    """Test processing multiple document types"""
    print("\n📚 Testing multiple document types...")
    
    documents = []
    success_count = 0
    
    try:
        # Create different types of test documents
        test_docs = [
            ("technical.txt", "Technical documentation about API endpoints and configuration."),
            ("user_guide.txt", "User guide explaining how to use the system features."),
            ("faq.txt", "Frequently asked questions about the platform and troubleshooting.")
        ]
        
        for filename, content in test_docs:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as temp_file:
                temp_file.write(content)
                documents.append(temp_file.name)
        
        # Upload all documents
        for i, doc_path in enumerate(documents):
            with open(doc_path, 'rb') as f:
                files = {"file": (f"test_doc_{i}.txt", f, "text/plain")}
                response = requests.post(f"{BASE_URL}/documents/upload", files=files)
            
            if response.status_code == 200:
                success_count += 1
                print(f"   ✅ Document {i+1} uploaded successfully")
            else:
                print(f"   ❌ Document {i+1} upload failed")
        
        # Test cross-document question
        if success_count > 0:
            question_data = {
                "question": "What types of documents are available in the system?",
                "top_k": 5
            }
            
            q_response = requests.post(
                f"{BASE_URL}/questions/ask",
                json=question_data,
                headers={"Content-Type": "application/json"}
            )
            
            if q_response.status_code == 200:
                result = q_response.json()
                print("   ✅ Cross-document question answered")
                print(f"   Answer: {result.get('answer', 'N/A')}")
            else:
                print(f"   ❌ Cross-document question failed: {q_response.text}")
        
        return success_count == len(test_docs)
        
    except Exception as e:
        print(f"❌ Multiple document types test - Error: {e}")
        return False
    finally:
        # Clean up temporary files
        for doc_path in documents:
            try:
                os.unlink(doc_path)
            except:
                pass

def test_document_chunking():
    """Test document chunking functionality"""
    print("\n✂️ Testing document chunking...")
    
    # Create a large document to test chunking
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as temp_file:
        # Create content that should be chunked
        for i in range(20):
            temp_file.write(f"Section {i+1}: This is a test section with detailed content. ")
            temp_file.write("It contains multiple sentences to ensure proper chunking. ")
            temp_file.write("The chunking algorithm should split this into manageable pieces. ")
            temp_file.write("Each chunk should be optimized for vector search and retrieval.\n\n")
        
        doc_path = temp_file.name
    
    try:
        # Upload large document
        with open(doc_path, 'rb') as f:
            files = {"file": ("chunking_test.txt", f, "text/plain")}
            upload_response = requests.post(f"{BASE_URL}/documents/upload", files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ Large document upload failed: {upload_response.text}")
            return False
        
        upload_result = upload_response.json()
        chunks_processed = upload_result.get('chunks_processed', 0)
        print(f"   ✅ Document chunked into {chunks_processed} pieces")
        
        # Test retrieval from different chunks
        questions = [
            "What is in section 1?",
            "What is in section 10?",
            "What is in section 20?"
        ]
        
        for question in questions:
            question_data = {
                "question": question,
                "top_k": 2
            }
            
            q_response = requests.post(
                f"{BASE_URL}/questions/ask",
                json=question_data,
                headers={"Content-Type": "application/json"}
            )
            
            if q_response.status_code == 200:
                result = q_response.json()
                print(f"   ✅ {question}: {result.get('answer', 'N/A')[:80]}...")
            else:
                print(f"   ❌ {question} failed: {q_response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Document chunking test - Error: {e}")
        return False
    finally:
        # Clean up temporary file
        try:
            os.unlink(doc_path)
        except:
            pass

def test_document_retrieval_accuracy():
    """Test document retrieval accuracy"""
    print("\n🎯 Testing document retrieval accuracy...")
    
    # Create a document with specific facts
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w') as temp_file:
        temp_file.write("Document Retrieval Accuracy Test\n")
        temp_file.write("The capital of France is Paris.\n")
        temp_file.write("The largest planet in our solar system is Jupiter.\n")
        temp_file.write("The chemical symbol for gold is Au.\n")
        temp_file.write("The speed of light is approximately 299,792 kilometers per second.\n")
        temp_file.write("The human body has 206 bones.\n")
        doc_path = temp_file.name
    
    try:
        # Upload document
        with open(doc_path, 'rb') as f:
            files = {"file": ("accuracy_test.txt", f, "text/plain")}
            upload_response = requests.post(f"{BASE_URL}/documents/upload", files=files)
        
        if upload_response.status_code != 200:
            print(f"❌ Accuracy test document upload failed: {upload_response.text}")
            return False
        
        print("   ✅ Accuracy test document uploaded")
        
        # Test specific fact retrieval
        test_questions = [
            ("What is the capital of France?", "Paris"),
            ("What is the largest planet?", "Jupiter"),
            ("What is the chemical symbol for gold?", "Au"),
            ("How fast is light?", "299,792"),
            ("How many bones does the human body have?", "206")
        ]
        
        correct_answers = 0
        
        for question, expected in test_questions:
            question_data = {
                "question": question,
                "top_k": 1
            }
            
            q_response = requests.post(
                f"{BASE_URL}/questions/ask",
                json=question_data,
                headers={"Content-Type": "application/json"}
            )
            
            if q_response.status_code == 200:
                result = q_response.json()
                answer = result.get('answer', '').lower()
                if expected.lower() in answer:
                    correct_answers += 1
                    print(f"   ✅ {question}: Correct")
                else:
                    print(f"   ❌ {question}: Expected '{expected}', got '{answer[:50]}...'")
            else:
                print(f"   ❌ {question} failed: {q_response.text}")
        
        accuracy = (correct_answers / len(test_questions)) * 100
        print(f"   📊 Retrieval Accuracy: {accuracy:.1f}% ({correct_answers}/{len(test_questions)})")
        
        return accuracy >= 80  # 80% accuracy threshold
        
    except Exception as e:
        print(f"❌ Document retrieval accuracy test - Error: {e}")
        return False
    finally:
        # Clean up temporary file
        try:
            os.unlink(doc_path)
        except:
            pass

def main():
    """Run all document processing workflow e2e tests"""
    print("🚀 Starting Document Processing Workflow E2E Tests")
    print("=" * 70)
    
    test_results = []
    
    # Test complete workflows
    test_results.append(("Complete Document Workflow", test_complete_document_workflow()))
    test_results.append(("Multiple Document Types", test_multiple_document_types()))
    test_results.append(("Document Chunking", test_document_chunking()))
    test_results.append(("Document Retrieval Accuracy", test_document_retrieval_accuracy()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Document Processing Workflow E2E Test Results:")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print("=" * 70)
    print(f"🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All document processing workflow e2e tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("=" * 70)

if __name__ == "__main__":
    main() 