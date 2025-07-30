#!/usr/bin/env python3
"""
Test script to demonstrate enhanced metadata transparency for all response modes.
This script shows how the new metadata structure provides clear visibility into decision-making.
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add the project root directory to the Python path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)

from app.domain.services.context_aware_rag_service import ContextAwareRAGService
from app.domain.services.rag_service import RAGService
from app.domain.models.requests import SystemMessageDirective, ResponseMode
from app.infrastructure.providers.service_locator import ServiceLocator

class MockRAGService:
    """Mock RAG service for testing"""
    
    def __init__(self, should_succeed: bool = True, sources_count: int = 3):
        self.should_succeed = should_succeed
        self.sources_count = sources_count
    
    async def ask_question(self, question: str, top_k: int = None) -> Dict[str, Any]:
        if self.should_succeed:
            sources = [
                {
                    "content": f"Sample content {i}",
                    "source": f"document_{i}.pdf",
                    "score": 0.8 + (i * 0.05)
                }
                for i in range(self.sources_count)
            ]
            return {
                "success": True,
                "answer": f"Answer based on {self.sources_count} documents",
                "sources": sources,
                "question": question
            }
        else:
            return {
                "success": False,
                "answer": "No relevant documents found",
                "sources": [],
                "question": question
            }

class MockLLMProvider:
    """Mock LLM provider for testing"""
    
    async def call_llm(self, messages: list) -> str:
        return "This is a response from the LLM based on general knowledge."

def print_metadata_analysis(metadata: Dict[str, Any], mode: str):
    """Print detailed analysis of metadata"""
    print(f"\n{'='*60}")
    print(f"METADATA ANALYSIS: {mode}")
    print(f"{'='*60}")
    
    # Core metadata
    print(f"Response Mode: {metadata.get('response_mode', 'unknown')}")
    print(f"Context Used: {metadata.get('context_used', 'unknown')}")
    print(f"Decision Reason: {metadata.get('decision_reason', 'unknown')}")
    print(f"RAG Sources Count: {metadata.get('rag_sources_count', 0)}")
    print(f"RAG Confidence: {metadata.get('rag_confidence', 0.0):.2f}")
    print(f"LLM Fallback Used: {metadata.get('llm_fallback_used', False)}")
    
    if metadata.get('fallback_reason'):
        print(f"Fallback Reason: {metadata['fallback_reason']}")
    
    if metadata.get('confidence_score') is not None:
        print(f"Confidence Score: {metadata['confidence_score']:.2f}")
    
    # Decision transparency
    transparency = metadata.get('decision_transparency', {})
    if transparency:
        print(f"\nDecision Transparency:")
        print(f"  RAG Attempted: {transparency.get('rag_attempted', False)}")
        print(f"  RAG Successful: {transparency.get('rag_successful', False)}")
        print(f"  RAG Documents Found: {transparency.get('rag_documents_found', 0)}")
        print(f"  LLM Fallback Triggered: {transparency.get('llm_fallback_triggered', False)}")
        print(f"  Final Decision: {transparency.get('final_decision', 'unknown')}")
        
        if transparency.get('confidence_threshold') is not None:
            print(f"  Confidence Threshold: {transparency['confidence_threshold']:.2f}")
            print(f"  Actual Confidence: {transparency.get('actual_confidence', 0.0):.2f}")
            print(f"  Confidence Decision: {transparency.get('confidence_decision', 'unknown')}")
        
        if transparency.get('rag_keywords_detected'):
            print(f"  RAG Keywords Detected: {transparency['rag_keywords_detected']}")
        
        if transparency.get('fallback_strategy'):
            print(f"  Fallback Strategy: {transparency['fallback_strategy']}")

async def test_response_modes():
    """Test all response modes with enhanced metadata"""
    
    # Create mock services
    mock_rag_success = MockRAGService(should_succeed=True, sources_count=3)
    mock_rag_failure = MockRAGService(should_succeed=False, sources_count=0)
    mock_llm = MockLLMProvider()
    
    # Create context-aware RAG service
    service = ContextAwareRAGService(
        rag_service=mock_rag_success,
        llm_provider=mock_llm
    )
    
    question = "How do I authenticate with the API?"
    system_message = "You are a helpful assistant."
    
    print("Testing Enhanced Metadata Transparency")
    print("=" * 60)
    
    # Test 1: RAG_ONLY with successful RAG
    print("\n1. Testing RAG_ONLY with successful RAG...")
    directive = SystemMessageDirective(
        response_mode=ResponseMode.RAG_ONLY,
        fallback_strategy="refuse"
    )
    
    result = await service.response_handler._handle_rag_only(question, directive, top_k=3)
    print_metadata_analysis(result, "RAG_ONLY (Success)")
    
    # Test 2: RAG_ONLY with failed RAG and refuse strategy
    print("\n2. Testing RAG_ONLY with failed RAG and refuse strategy...")
    service.rag_service = mock_rag_failure
    
    result = await service.response_handler._handle_rag_only(question, directive, top_k=3)
    print_metadata_analysis(result, "RAG_ONLY (Failure + Refuse)")
    
    # Test 3: RAG_ONLY with failed RAG and hybrid strategy
    print("\n3. Testing RAG_ONLY with failed RAG and hybrid strategy...")
    directive.fallback_strategy = "hybrid"
    
    result = await service.response_handler._handle_rag_only(question, directive, top_k=3)
    print_metadata_analysis(result, "RAG_ONLY (Failure + Hybrid)")
    
    # Test 4: LLM_ONLY
    print("\n4. Testing LLM_ONLY...")
    result = await service.response_handler._handle_llm_only(question, system_message)
    print_metadata_analysis(result, "LLM_ONLY")
    
    # Test 5: HYBRID with successful RAG
    print("\n5. Testing HYBRID with successful RAG...")
    service.rag_service = mock_rag_success
    directive.response_mode = ResponseMode.HYBRID
    
    result = await service.response_handler._handle_hybrid(question, system_message, directive, top_k=3)
    print_metadata_analysis(result, "HYBRID (Success)")
    
    # Test 6: HYBRID with failed RAG
    print("\n6. Testing HYBRID with failed RAG...")
    service.rag_service = mock_rag_failure
    
    result = await service.response_handler._handle_hybrid(question, system_message, directive, top_k=3)
    print_metadata_analysis(result, "HYBRID (Failure)")
    
    # Test 7: SMART_FALLBACK with high confidence
    print("\n7. Testing SMART_FALLBACK with high confidence...")
    service.rag_service = mock_rag_success
    directive.response_mode = ResponseMode.SMART_FALLBACK
    directive.min_confidence = 0.7
    
    result = await service.response_handler._handle_smart_fallback(question, system_message, directive, top_k=3)
    print_metadata_analysis(result, "SMART_FALLBACK (High Confidence)")
    
    # Test 8: SMART_FALLBACK with low confidence
    print("\n8. Testing SMART_FALLBACK with low confidence...")
    # Create a mock service with lower confidence scores
    mock_rag_low_confidence = MockRAGService(should_succeed=True, sources_count=2)
    service.rag_service = mock_rag_low_confidence
    
    result = await service.response_handler._handle_smart_fallback(question, system_message, directive, top_k=3)
    print_metadata_analysis(result, "SMART_FALLBACK (Low Confidence)")
    
    # Test 9: RAG_PRIORITY with successful RAG
    print("\n9. Testing RAG_PRIORITY with successful RAG...")
    service.rag_service = mock_rag_success
    directive.response_mode = ResponseMode.RAG_PRIORITY
    
    result = await service.response_handler._handle_rag_priority(question, system_message, directive, top_k=3)
    print_metadata_analysis(result, "RAG_PRIORITY (Success)")
    
    # Test 10: RAG_PRIORITY with failed RAG
    print("\n10. Testing RAG_PRIORITY with failed RAG...")
    service.rag_service = mock_rag_failure
    
    result = await service.response_handler._handle_rag_priority(question, system_message, directive, top_k=3)
    print_metadata_analysis(result, "RAG_PRIORITY (Failure)")
    
    # Test 11: LLM_PRIORITY with RAG keywords
    print("\n11. Testing LLM_PRIORITY with RAG keywords...")
    service.rag_service = mock_rag_success
    directive.response_mode = ResponseMode.LLM_PRIORITY
    question_with_keywords = "What does the document say about API authentication?"
    
    result = await service.response_handler._handle_llm_priority(question_with_keywords, system_message, directive, top_k=3)
    print_metadata_analysis(result, "LLM_PRIORITY (With RAG Keywords)")
    
    # Test 12: LLM_PRIORITY without RAG keywords
    print("\n12. Testing LLM_PRIORITY without RAG keywords...")
    question_without_keywords = "What is the capital of France?"
    
    result = await service.response_handler._handle_llm_priority(question_without_keywords, system_message, directive, top_k=3)
    print_metadata_analysis(result, "LLM_PRIORITY (Without RAG Keywords)")

def print_summary():
    """Print summary of metadata transparency benefits"""
    print(f"\n{'='*60}")
    print("METADATA TRANSPARENCY SUMMARY")
    print(f"{'='*60}")
    
    print("\nBenefits of Enhanced Metadata Transparency:")
    print("1. Complete visibility into decision-making process")
    print("2. Clear distinction between RAG success and LLM fallback")
    print("3. Confidence scoring and threshold tracking")
    print("4. Detailed reasoning for each decision")
    print("5. Support for debugging and monitoring")
    print("6. Enhanced user trust through transparency")
    
    print("\nKey Metadata Fields:")
    print("- response_mode: Which response mode was used")
    print("- context_used: What type of context was utilized")
    print("- decision_reason: Why this specific decision was made")
    print("- rag_sources_count: Number of RAG documents found")
    print("- rag_confidence: Average confidence of RAG results")
    print("- llm_fallback_used: Whether LLM fallback was triggered")
    print("- decision_transparency: Complete decision breakdown")
    
    print("\nDecision Transparency Fields:")
    print("- rag_attempted: Whether RAG was attempted")
    print("- rag_successful: Whether RAG found relevant documents")
    print("- rag_documents_found: Number of documents found")
    print("- llm_fallback_triggered: Whether LLM fallback was used")
    print("- final_decision: The ultimate decision made")

if __name__ == "__main__":
    print("Enhanced Metadata Transparency Test")
    print("This script demonstrates the improved transparency in decision-making")
    print("for all response modes in the context-aware RAG system.")
    
    try:
        asyncio.run(test_response_modes())
        print_summary()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc() 