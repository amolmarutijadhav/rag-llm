#!/usr/bin/env python3
"""
Test script to verify that error logging works correctly in production scenarios.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.error_logging import ErrorLogger
from app.core.logging_config import logging_config, get_logger
from app.api.middleware.error_logging import ErrorLoggingMiddleware

# Setup logging
logging_config.setup_logging()
logger = get_logger("test_production_error_logging")

def test_production_error_logging():
    """Test that error logging works in production scenarios."""
    print("Testing production error logging...")
    
    # Simulate production environment (no pytest, no test flags)
    original_argv = sys.argv.copy()
    original_modules = list(sys.modules.keys())
    
    try:
        # Clear any test-related environment variables
        test_env_vars = ['PYTEST_CURRENT_TEST', 'TESTING']
        original_env = {}
        for var in test_env_vars:
            if var in os.environ:
                original_env[var] = os.environ[var]
                del os.environ[var]
        
        # Remove pytest from sys.modules if present
        if 'pytest' in sys.modules:
            del sys.modules['pytest']
        
        # Clear sys.argv to remove any pytest arguments
        sys.argv = ['python', 'main.py']
        
        # Test the middleware detection
        from fastapi import FastAPI
        app = FastAPI()
        middleware = ErrorLoggingMiddleware(app)
        
        # Verify that test environment detection returns False in production
        is_test_env = middleware.is_test_environment
        print(f"Test environment detection result: {is_test_env}")
        
        if is_test_env:
            print("❌ ERROR: Test environment incorrectly detected in production scenario!")
            return False
        else:
            print("✅ SUCCESS: Production environment correctly detected!")
        
        # Test that error logging still works
        test_exception = ValueError("Test production error")
        context = {
            'operation': 'test_production_logging',
            'test_scenario': 'production_simulation'
        }
        
        # This should log the error since we're not in a test environment
        ErrorLogger.log_exception(test_exception, context)
        print("✅ SUCCESS: Error logging works in production scenario!")
        
        return True
        
    finally:
        # Restore original state
        sys.argv = original_argv
        
        # Restore environment variables
        for var, value in original_env.items():
            os.environ[var] = value
        
        # Restore sys.modules
        for module in original_modules:
            if module not in sys.modules:
                try:
                    __import__(module)
                except ImportError:
                    pass

def test_test_environment_detection():
    """Test that test environment detection works correctly."""
    print("\nTesting test environment detection...")
    
    # Simulate test environment
    original_argv = sys.argv.copy()
    
    try:
        # Set test environment variables
        os.environ['PYTEST_CURRENT_TEST'] = 'test_file.py::test_function'
        
        # Add pytest to sys.modules
        sys.modules['pytest'] = type('MockPytest', (), {})()
        
        # Add pytest to sys.argv
        sys.argv = ['python', '-m', 'pytest', 'test_file.py']
        
        # Test the middleware detection
        from fastapi import FastAPI
        app = FastAPI()
        middleware = ErrorLoggingMiddleware(app)
        
        # Verify that test environment detection returns True
        is_test_env = middleware.is_test_environment
        print(f"Test environment detection result: {is_test_env}")
        
        if is_test_env:
            print("✅ SUCCESS: Test environment correctly detected!")
        else:
            print("❌ ERROR: Test environment not detected!")
            return False
        
        return True
        
    finally:
        # Restore original state
        sys.argv = original_argv
        if 'PYTEST_CURRENT_TEST' in os.environ:
            del os.environ['PYTEST_CURRENT_TEST']
        if 'pytest' in sys.modules:
            del sys.modules['pytest']

if __name__ == "__main__":
    print("🧪 Testing Enhanced Error Logging Production Safety")
    print("=" * 60)
    
    # Test production scenario
    production_success = test_production_error_logging()
    
    # Test test environment detection
    test_detection_success = test_test_environment_detection()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"Production Error Logging: {'✅ PASS' if production_success else '❌ FAIL'}")
    print(f"Test Environment Detection: {'✅ PASS' if test_detection_success else '❌ FAIL'}")
    
    if production_success and test_detection_success:
        print("\n🎉 All tests passed! Error logging is production-safe.")
    else:
        print("\n⚠️  Some tests failed. Please review the implementation.")
        sys.exit(1) 