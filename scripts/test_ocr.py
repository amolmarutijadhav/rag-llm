#!/usr/bin/env python3
"""
OCR Testing Script
Runs comprehensive OCR functionality tests and provides detailed reporting.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n🔍 {description}")
    print(f"Command: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=Path(__file__).parent.parent
        )
        
        print(f"Exit Code: {result.returncode}")
        if result.stdout:
            print(f"Output:\n{result.stdout}")
        if result.stderr:
            print(f"Errors:\n{result.stderr}")
            
        return result.returncode == 0, result.stdout, result.stderr
        
    except Exception as e:
        print(f"Error running command: {e}")
        return False, "", str(e)

def check_ocr_dependencies():
    """Check if OCR dependencies are available."""
    print("🔧 Checking OCR Dependencies...")
    print("=" * 60)
    
    dependencies = [
        ("pytesseract", "Python OCR wrapper"),
        ("PIL", "Image processing"),
        ("pdf2image", "PDF to image conversion"),
        ("python-docx", "DOCX processing")
    ]
    
    missing_deps = []
    available_deps = []
    
    for dep, description in dependencies:
        try:
            if dep == "PIL":
                import PIL
                available_deps.append(f"✅ {dep} ({description})")
            else:
                __import__(dep)
                available_deps.append(f"✅ {dep} ({description})")
        except ImportError:
            missing_deps.append(f"❌ {dep} ({description})")
    
    print("Available Dependencies:")
    for dep in available_deps:
        print(f"  {dep}")
    
    if missing_deps:
        print("\nMissing Dependencies:")
        for dep in missing_deps:
            print(f"  {dep}")
        print("\n⚠️  Some OCR tests may fail due to missing dependencies.")
    else:
        print("\n✅ All OCR dependencies are available!")
    
    return len(missing_deps) == 0

def run_ocr_tests():
    """Run comprehensive OCR tests."""
    print("\n🚀 Running OCR Functionality Tests...")
    print("=" * 60)
    
    test_commands = [
        ("pytest tests/integration/test_real_ocr.py -v -m real_ocr", "Real OCR Functionality Tests"),
        ("pytest tests/integration/test_real_ocr.py -v -m ocr_batch", "Batch OCR Processing Tests"),
        ("pytest tests/integration/test_real_ocr.py -v -m ocr_accuracy", "OCR Accuracy Tests"),
        ("pytest tests/integration/test_real_ocr.py -v -m ocr_integration", "OCR Integration Tests"),
        ("pytest tests/integration/test_real_ocr.py -v -m ocr_performance", "OCR Performance Tests"),
        ("pytest tests/integration/test_document_upload.py -v -m document_upload", "Document Upload Tests (includes OCR)"),
    ]
    
    results = {}
    
    for command, description in test_commands:
        success, stdout, stderr = run_command(command, description)
        results[description] = {
            "success": success,
            "stdout": stdout,
            "stderr": stderr
        }
        
        if success:
            print(f"✅ {description}: PASSED")
        else:
            print(f"❌ {description}: FAILED")
    
    return results

def generate_ocr_report(results):
    """Generate a comprehensive OCR test report."""
    print("\n📊 OCR Test Report")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result["success"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Test Categories: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"  {test_name}: {status}")
        
        if not result["success"] and result["stderr"]:
            print(f"    Error: {result['stderr'][:200]}...")
    
    return passed_tests, failed_tests

def run_specific_ocr_test(test_type):
    """Run a specific type of OCR test."""
    test_map = {
        "real": "pytest tests/integration/test_real_ocr.py -v -m real_ocr",
        "batch": "pytest tests/integration/test_real_ocr.py -v -m ocr_batch",
        "accuracy": "pytest tests/integration/test_real_ocr.py -v -m ocr_accuracy",
        "integration": "pytest tests/integration/test_real_ocr.py -v -m ocr_integration",
        "performance": "pytest tests/integration/test_real_ocr.py -v -m ocr_performance",
        "upload": "pytest tests/integration/test_document_upload.py -v -m document_upload",
        "all": None  # Will run all tests
    }
    
    if test_type not in test_map:
        print(f"❌ Unknown test type: {test_type}")
        print(f"Available types: {', '.join(test_map.keys())}")
        return False
    
    if test_type == "all":
        return run_ocr_tests()
    else:
        command = test_map[test_type]
        success, stdout, stderr = run_command(command, f"OCR {test_type.title()} Tests")
        return success

def main():
    """Main function to run OCR tests."""
    print("🔍 OCR Functionality Testing Suite")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("app") or not os.path.exists("tests"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == "help":
            print("Usage: python scripts/test_ocr.py [test_type]")
            print("Available test types:")
            print("  real      - Real OCR functionality tests")
            print("  batch     - Batch OCR processing tests")
            print("  accuracy  - OCR accuracy tests")
            print("  integration - OCR integration tests")
            print("  performance - OCR performance tests")
            print("  upload    - Document upload tests (includes OCR)")
            print("  all       - All OCR tests (default)")
            print("  help      - Show this help message")
            sys.exit(0)
        
        # Check dependencies first
        deps_available = check_ocr_dependencies()
        
        # Run specific test
        success = run_specific_ocr_test(test_type)
        sys.exit(0 if success else 1)
    
    # Run all tests by default
    print("Running comprehensive OCR test suite...")
    
    # Check dependencies
    deps_available = check_ocr_dependencies()
    
    # Run all tests
    results = run_ocr_tests()
    
    # Generate report
    passed, failed = generate_ocr_report(results)
    
    # Final summary
    print(f"\n🎯 Final Summary:")
    print(f"  OCR Dependencies: {'✅ Available' if deps_available else '❌ Missing'}")
    print(f"  Tests Passed: {passed}")
    print(f"  Tests Failed: {failed}")
    
    if failed == 0:
        print(f"🎉 All OCR tests passed!")
        sys.exit(0)
    else:
        print(f"⚠️  Some OCR tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 