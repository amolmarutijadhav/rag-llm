#!/usr/bin/env python3
"""
Integration Test Runner for RAG LLM API
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_integration_tests(test_pattern=None, timeout=300, verbose=True):
    """Run integration tests with specified options."""
    
    # Base pytest command
    cmd = [
        "python", "-m", "pytest",
        "tests/integration/",
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]
    
    # Add test pattern if specified
    if test_pattern:
        cmd.append(f"*{test_pattern}*")
    
    # Add markers to exclude slow tests by default
    cmd.extend(["-m", "not slow"])
    
    # Add coverage reporting
    cmd.extend([
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--cov-report=xml"
    ])
    
    print(f"Running integration tests: {' '.join(cmd)}")
    print("=" * 60)
    print(f"Timeout: {timeout} seconds")
    print(f"Test pattern: {test_pattern or 'All integration tests'}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, check=True, timeout=timeout)
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print(f"✅ All integration tests passed!")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print("=" * 60)
        return True
        
    except subprocess.TimeoutExpired:
        print("\n" + "=" * 60)
        print(f"❌ Tests timed out after {timeout} seconds")
        print("=" * 60)
        return False
        
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print(f"❌ Integration tests failed with exit code: {e.returncode}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print("=" * 60)
        return False

def run_specific_test_files(test_files, timeout=300):
    """Run specific test files."""
    
    if not test_files:
        print("No test files specified")
        return False
    
    cmd = [
        "python", "-m", "pytest",
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]
    
    # Add test files
    cmd.extend(test_files)
    
    print(f"Running specific test files: {' '.join(cmd)}")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, check=True, timeout=timeout)
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print(f"✅ All specified tests passed!")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print("=" * 60)
        return True
        
    except subprocess.TimeoutExpired:
        print("\n" + "=" * 60)
        print(f"❌ Tests timed out after {timeout} seconds")
        print("=" * 60)
        return False
        
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print(f"❌ Tests failed with exit code: {e.returncode}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print("=" * 60)
        return False

def list_available_tests():
    """List all available integration test files."""
    integration_dir = Path("tests/integration")
    
    if not integration_dir.exists():
        print("❌ Integration tests directory not found")
        return
    
    test_files = list(integration_dir.glob("test_*.py"))
    
    print("Available integration test files:")
    print("=" * 40)
    
    for i, test_file in enumerate(test_files, 1):
        print(f"{i:2d}. {test_file.name}")
    
    print(f"\nTotal: {len(test_files)} test files")

def main():
    """Main function to handle command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run RAG LLM API integration tests")
    parser.add_argument(
        "--pattern",
        help="Test pattern to match (e.g., 'api', 'ocr', 'document')"
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Specific test files to run"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds (default: 300)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available test files"
    )
    parser.add_argument(
        "--include-slow",
        action="store_true",
        help="Include slow tests"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_available_tests()
        return
    
    # Run specific test files if provided
    if args.files:
        success = run_specific_test_files(args.files, args.timeout)
    else:
        # Run integration tests with pattern
        success = run_integration_tests(args.pattern, args.timeout)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 