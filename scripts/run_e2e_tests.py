#!/usr/bin/env python3
"""
E2E Test Runner - Comprehensive end-to-end testing for RAG LLM API
"""

import subprocess
import sys
import os
import time
from datetime import datetime

def run_test_script(script_name, description):
    """Run a test script and return results"""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {description}")
    print(f"📁 Script: {script_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Run the test script
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env,
            cwd=os.getcwd()
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print(f"📤 Exit Code: {result.returncode}")
        
        # Print output
        if result.stdout:
            print("\n📋 Output:")
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ Errors:")
            print(result.stderr)
        
        success = result.returncode == 0
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status} {description}")
        
        return {
            'name': description,
            'script': script_name,
            'success': success,
            'duration': duration,
            'exit_code': result.returncode,
            'output': result.stdout,
            'error': result.stderr
        }
        
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return {
            'name': description,
            'script': script_name,
            'success': False,
            'duration': 0,
            'exit_code': -1,
            'output': '',
            'error': str(e)
        }

def check_server_status():
    """Check if the API server is running"""
    print("🔍 Checking API server status...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"⚠️ API server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API server is not running: {e}")
        print("💡 Please start the server with: python run.py")
        return False

def main():
    """Run all E2E tests"""
    # Set console encoding for Windows
    if os.name == 'nt':
        try:
            os.system('chcp 65001 > nul')
        except:
            pass
    
    print("🚀 RAG LLM API - E2E Test Suite")
    print("=" * 60)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working Directory: {os.getcwd()}")
    
    # Check server status
    if not check_server_status():
        print("\n❌ Cannot run E2E tests without a running server")
        print("💡 Please start the server first:")
        print("   python run.py")
        sys.exit(1)
    
    # Define test suites
    test_suites = [
        {
            'script': 'tests/e2e/test_apis.py',
            'description': 'Basic API Endpoints'
        },
        {
            'script': 'tests/e2e/test_file_upload.py',
            'description': 'File Upload Functionality'
        },
        {
            'script': 'tests/e2e/test_ocr_workflow.py',
            'description': 'OCR Workflow Processing'
        },
        {
            'script': 'tests/e2e/test_document_processing_workflow.py',
            'description': 'Document Processing Workflow'
        },
        {
            'script': 'tests/e2e/test_rag_with_data.py',
            'description': 'RAG with Knowledge Base Data'
        },
        {
            'script': 'tests/e2e/test_rag_chat_completions.py',
            'description': 'RAG Chat Completions'
        }
    ]
    
    # Run all test suites
    results = []
    total_start_time = time.time()
    
    for test_suite in test_suites:
        result = run_test_script(test_suite['script'], test_suite['description'])
        results.append(result)
        
        # Add a small delay between tests
        time.sleep(1)
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # Generate summary report
    print(f"\n{'='*60}")
    print("📊 E2E Test Suite Summary Report")
    print(f"{'='*60}")
    print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️ Total Duration: {total_duration:.2f} seconds")
    
    # Count results
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    print(f"\n🎯 Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Total: {len(results)}")
    
    # Detailed results
    print(f"\n📋 Detailed Results:")
    print(f"{'Test':<35} {'Status':<10} {'Duration':<10} {'Exit Code':<10}")
    print("-" * 70)
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        duration = f"{result['duration']:.2f}s"
        exit_code = str(result['exit_code'])
        print(f"{result['name']:<35} {status:<10} {duration:<10} {exit_code:<10}")
    
    # Failed tests details
    failed_tests = [r for r in results if not r['success']]
    if failed_tests:
        print(f"\n❌ Failed Tests Details:")
        for test in failed_tests:
            print(f"\n🔍 {test['name']}:")
            print(f"   Script: {test['script']}")
            print(f"   Exit Code: {test['exit_code']}")
            if test['error']:
                print(f"   Error: {test['error']}")
    
    # Success rate
    success_rate = (passed / len(results)) * 100 if results else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}%")
    
    # Final status
    if failed == 0:
        print(f"\n🎉 All E2E tests passed successfully!")
        print(f"✅ The RAG LLM API is working correctly end-to-end.")
        sys.exit(0)
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please check the details above.")
        print(f"🔧 Review the failed tests and fix any issues.")
        sys.exit(1)

if __name__ == "__main__":
    main() 