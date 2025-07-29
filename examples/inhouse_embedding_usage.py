"""
Example usage of the enhanced InhouseEmbeddingProvider with single text processing.

This example demonstrates how to configure and use the InhouseEmbeddingProvider with:
1. Single text processing instead of batch processing
2. Form data request format (instead of JSON)
3. Controlled concurrency and rate limiting
4. Enhanced error handling and logging
5. Multiple response format support
"""

import asyncio
import os
from typing import List, Dict, Any
from app.infrastructure.providers.inhouse_provider import InhouseEmbeddingProvider

def example_basic_configuration():
    """Example 1: Basic configuration with single text processing."""
    
    config = {
        "api_url": "https://inhouse-embeddings.company.com/api/v1/embed",
        "api_key": "your-api-key-here",
        "model": "company-embedding-v2",
        "max_concurrent_requests": 3,  # Limit concurrent requests
        "request_delay": 0.2  # 200ms delay between requests
    }
    
    return InhouseEmbeddingProvider(config)

def example_high_performance_configuration():
    """Example 2: High performance configuration for production use."""
    
    config = {
        "api_url": "https://inhouse-embeddings.company.com/api/v1/embed",
        "api_key": "your-api-key-here",
        "model": "company-embedding-v2",
        "max_concurrent_requests": 10,  # Higher concurrency
        "request_delay": 0.05  # 50ms delay between requests
    }
    
    return InhouseEmbeddingProvider(config)

def example_conservative_configuration():
    """Example 3: Conservative configuration for rate-limited APIs."""
    
    config = {
        "api_url": "https://inhouse-embeddings.company.com/api/v1/embed",
        "api_key": "your-api-key-here",
        "model": "company-embedding-v2",
        "max_concurrent_requests": 1,  # Sequential processing
        "request_delay": 1.0  # 1 second delay between requests
    }
    
    return InhouseEmbeddingProvider(config)

async def example_single_text_processing():
    """Example 4: Demonstrate single text processing capabilities."""
    
    provider = example_basic_configuration()
    
    # Example 1: Single text embedding
    print("=== Example 1: Single Text Embedding ===")
    single_text = "This is a sample text for embedding generation."
    
    try:
        embedding = await provider.get_single_embedding(single_text)
        print(f"Single embedding dimensions: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

async def example_batch_processing():
    """Example 5: Demonstrate batch processing with single text API."""
    
    provider = example_basic_configuration()
    
    # Example 1: Small batch
    print("=== Example 1: Small Batch Processing ===")
    texts = [
        "First text for embedding.",
        "Second text for embedding.",
        "Third text for embedding."
    ]
    
    try:
        embeddings = await provider.get_embeddings(texts)
        print(f"Generated {len(embeddings)} embeddings")
        for i, embedding in enumerate(embeddings):
            print(f"Text {i+1}: {len(embedding)} dimensions")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()
    
    # Example 2: Larger batch with error handling
    print("=== Example 2: Larger Batch with Error Handling ===")
    large_texts = [
        "Text 1: Machine learning is a subset of artificial intelligence.",
        "Text 2: Natural language processing helps computers understand human language.",
        "Text 3: Deep learning uses neural networks with multiple layers.",
        "Text 4: Computer vision enables machines to interpret visual information.",
        "Text 5: Reinforcement learning learns through interaction with environment.",
        "Text 6: Transfer learning applies knowledge from one task to another.",
        "Text 7: Generative AI creates new content like text, images, or music.",
        "Text 8: Large language models are trained on vast amounts of text data."
    ]
    
    try:
        embeddings = await provider.get_embeddings(large_texts)
        print(f"Generated {len(embeddings)} embeddings")
        print(f"Average dimensions: {sum(len(emb) for emb in embeddings) / len(embeddings):.1f}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

async def example_performance_comparison():
    """Example 6: Compare different configuration performances."""
    
    print("=== Performance Comparison ===")
    
    test_texts = [
        "Sample text for performance testing.",
        "Another sample text for comparison.",
        "Third text to measure processing time.",
        "Fourth text to evaluate performance.",
        "Fifth text for comprehensive testing."
    ]
    
    configs = [
        ("Conservative", example_conservative_configuration()),
        ("Basic", example_basic_configuration()),
        ("High Performance", example_high_performance_configuration())
    ]
    
    for config_name, provider in configs:
        print(f"\n--- {config_name} Configuration ---")
        print(f"Max concurrent requests: {provider.max_concurrent_requests}")
        print(f"Request delay: {provider.request_delay}s")
        
        try:
            import time
            start_time = time.time()
            embeddings = await provider.get_embeddings(test_texts)
            duration = time.time() - start_time
            
            print(f"Processing time: {duration:.2f}s")
            print(f"Average time per text: {duration/len(test_texts):.2f}s")
            print(f"Successfully processed: {len([e for e in embeddings if e])}/{len(test_texts)}")
        except Exception as e:
            print(f"Error: {e}")

async def example_error_handling():
    """Example 7: Demonstrate error handling capabilities."""
    
    provider = example_basic_configuration()
    
    print("=== Error Handling Examples ===")
    
    # Example 1: Empty text
    print("\n--- Empty Text Handling ---")
    try:
        embedding = await provider.get_single_embedding("")
        print(f"Empty text embedding: {len(embedding)} dimensions")
    except Exception as e:
        print(f"Empty text error: {e}")
    
    # Example 2: Very long text
    print("\n--- Long Text Handling ---")
    long_text = "This is a very long text. " * 1000  # ~30k characters
    try:
        embedding = await provider.get_single_embedding(long_text)
        print(f"Long text embedding: {len(embedding)} dimensions")
    except Exception as e:
        print(f"Long text error: {e}")
    
    # Example 3: Mixed batch with potential failures
    print("\n--- Mixed Batch with Failures ---")
    mixed_texts = [
        "Valid text 1",
        "",  # Empty text
        "Valid text 2",
        "x" * 100000,  # Very long text
        "Valid text 3"
    ]
    
    try:
        embeddings = await provider.get_embeddings(mixed_texts)
        print(f"Mixed batch results: {len(embeddings)} embeddings")
        for i, embedding in enumerate(embeddings):
            status = "✓" if embedding else "✗"
            print(f"Text {i+1}: {status} ({len(embedding)} dimensions)")
    except Exception as e:
        print(f"Mixed batch error: {e}")

def main():
    """Run all examples."""
    print("🚀 Enhanced InhouseEmbeddingProvider Usage Examples")
    print("=" * 60)
    print()
    
    # Run examples
    asyncio.run(example_single_text_processing())
    asyncio.run(example_batch_processing())
    asyncio.run(example_performance_comparison())
    asyncio.run(example_error_handling())
    
    print("\n✅ All examples completed!")
    print()
    print("📝 Configuration Notes:")
    print("- Set INHOUSE_EMBEDDING_API_URL in your .env file")
    print("- Configure max_concurrent_requests based on API limits")
    print("- Adjust request_delay to respect rate limits")
    print("- The provider processes texts one at a time internally")
    print("- Enhanced error handling maintains order in batch processing")
    print("- Comprehensive logging for monitoring and debugging")

if __name__ == "__main__":
    main() 