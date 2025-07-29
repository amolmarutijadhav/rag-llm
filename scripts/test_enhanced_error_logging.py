#!/usr/bin/env python3
"""
Test script for enhanced error logging functionality.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.error_logging import ErrorLogger, log_errors, error_logging_context
from app.core.logging_config import logging_config, get_logger, generate_correlation_id, set_correlation_id
from app.utils.error_utils import handle_api_errors, handle_provider_errors

# Setup logging
logging_config.setup_logging()
logger = get_logger("test_enhanced_error_logging")

def test_basic_error_logging():
    """Test basic error logging functionality."""
    print("Testing basic error logging...")
    
    try:
        # Simulate an error
        raise ValueError("Test error for enhanced logging")
    except Exception as e:
        ErrorLogger.log_exception(e, {
            'operation': 'test_basic_error_logging',
            'test_type': 'basic',
            'module': 'test_script'
        })
        print("✓ Basic error logging test completed")

@log_errors("test_decorator_function")
def test_decorator_function():
    """Test function with error logging decorator."""
    print("Testing decorator-based error logging...")
    # Simulate an error
    raise RuntimeError("Test error in decorated function")

@log_errors("test_async_decorator_function")
async def test_async_decorator_function():
    """Test async function with error logging decorator."""
    print("Testing async decorator-based error logging...")
    await asyncio.sleep(0.1)  # Simulate async work
    # Simulate an error
    raise ConnectionError("Test async error in decorated function")

@handle_api_errors
async def test_api_error_handling():
    """Test API error handling decorator."""
    print("Testing API error handling...")
    # Simulate an API error
    raise Exception("Test API error")

@handle_provider_errors
async def test_provider_error_handling():
    """Test provider error handling decorator."""
    print("Testing provider error handling...")
    # Simulate a provider error
    raise Exception("Test provider error")

def test_context_manager():
    """Test error logging context manager."""
    print("Testing context manager error logging...")
    
    with error_logging_context("test_context_operation", test_param="value"):
        # Simulate an error
        raise TypeError("Test error in context manager")

async def run_all_tests():
    """Run all error logging tests."""
    print("🚀 Starting Enhanced Error Logging Tests")
    print("=" * 50)
    
    # Set correlation ID for testing
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)
    
    print(f"Test Correlation ID: {correlation_id}")
    print()
    
    try:
        # Test 1: Basic error logging
        test_basic_error_logging()
        
        # Test 2: Decorator-based error logging
        try:
            test_decorator_function()
        except Exception:
            print("✓ Decorator error logging test completed")
        
        # Test 3: Async decorator-based error logging
        try:
            await test_async_decorator_function()
        except Exception:
            print("✓ Async decorator error logging test completed")
        
        # Test 4: API error handling
        try:
            await test_api_error_handling()
        except Exception:
            print("✓ API error handling test completed")
        
        # Test 5: Provider error handling
        try:
            await test_provider_error_handling()
        except Exception:
            print("✓ Provider error handling test completed")
        
        # Test 6: Context manager
        try:
            test_context_manager()
        except Exception:
            print("✓ Context manager error logging test completed")
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("📝 Check the logs above for detailed error information with stack traces.")
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1) 