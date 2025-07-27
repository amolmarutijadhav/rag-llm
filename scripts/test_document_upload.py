#!/usr/bin/env python3
"""
Test runner for document upload functionality.
This script runs comprehensive tests for the document upload feature.
"""

import sys
import os
import pytest
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_document_upload_tests():
    """Run document upload tests with detailed output."""
    print("🚀 Starting Document Upload Tests...")
    print("=" * 60)
    
    # Test file path
    test_file = project_root / "tests" / "integration" / "test_document_upload.py"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    # Run tests with verbose output
    args = [
        str(test_file),
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
        "-m", "document_upload",  # Only run document upload tests
        "--durations=10",  # Show top 10 slowest tests
    ]
    
    print(f"📁 Running tests from: {test_file}")
    print(f"🔧 Test arguments: {' '.join(args)}")
    print("=" * 60)
    
    # Run pytest
    exit_code = pytest.main(args)
    
    print("=" * 60)
    if exit_code == 0:
        print("✅ All document upload tests passed!")
    else:
        print(f"❌ Some document upload tests failed (exit code: {exit_code})")
    
    return exit_code == 0

def run_specific_test(test_name):
    """Run a specific document upload test."""
    print(f"🎯 Running specific test: {test_name}")
    print("=" * 60)
    
    test_file = project_root / "tests" / "integration" / "test_document_upload.py"
    
    args = [
        str(test_file),
        "-v",
        "--tb=short",
        "--color=yes",
        "-k", test_name,  # Run only tests matching the pattern
    ]
    
    exit_code = pytest.main(args)
    
    print("=" * 60)
    if exit_code == 0:
        print(f"✅ Test '{test_name}' passed!")
    else:
        print(f"❌ Test '{test_name}' failed!")
    
    return exit_code == 0

def list_available_tests():
    """List all available document upload tests."""
    print("📋 Available Document Upload Tests:")
    print("=" * 60)
    
    test_file = project_root / "tests" / "integration" / "test_document_upload.py"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return
    
    # Use pytest to collect test names
    args = [
        str(test_file),
        "--collect-only",
        "-q",
        "-m", "document_upload",
    ]
    
    # Capture output to get test names
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest"] + args,
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            test_count = 0
            for line in lines:
                if line.strip() and '::' in line and 'test_' in line:
                    test_name = line.strip().split('::')[-1]
                    print(f"  • {test_name}")
                    test_count += 1
            
            print(f"\n📊 Total tests found: {test_count}")
        else:
            print("❌ Failed to collect tests")
            print(result.stderr)
    
    except Exception as e:
        print(f"❌ Error collecting tests: {e}")

def main():
    """Main function to run document upload tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run document upload tests")
    parser.add_argument(
        "--list", 
        action="store_true", 
        help="List all available tests"
    )
    parser.add_argument(
        "--test", 
        type=str, 
        help="Run a specific test by name"
    )
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="Run all document upload tests (default)"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_available_tests()
    elif args.test:
        success = run_specific_test(args.test)
        sys.exit(0 if success else 1)
    else:
        # Default: run all tests
        success = run_document_upload_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 