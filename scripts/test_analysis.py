#!/usr/bin/env python3
"""
Integration Test Analysis Script
Analyzes which integration tests are working and which are not.
"""

import subprocess
import sys
import time
from pathlib import Path

def test_single_test_file(test_file, timeout=30):
    """Test a single test file and return results."""
    print(f"Testing {test_file}...")
    
    cmd = [
        "python", "-m", "pytest",
        test_file,
        "-v",
        "--tb=short",
        "--disable-warnings",
        "-q"  # Quiet mode for cleaner output
    ]
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, check=True, timeout=timeout, capture_output=True, text=True)
        end_time = time.time()
        duration = end_time - start_time
        
        # Parse the output to get test count
        output_lines = result.stdout.split('\n')
        test_count = 0
        for line in output_lines:
            if 'passed' in line and 'failed' in line:
                # Extract test count from line like "5 passed, 0 failed"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.isdigit() and i > 0 and parts[i-1] == 'passed':
                        test_count = int(part)
                        break
                break
        
        return {
            'status': 'PASSED',
            'duration': duration,
            'test_count': test_count,
            'error': None
        }
        
    except subprocess.TimeoutExpired:
        return {
            'status': 'TIMEOUT',
            'duration': timeout,
            'test_count': 0,
            'error': f'Timed out after {timeout} seconds'
        }
        
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'status': 'FAILED',
            'duration': duration,
            'test_count': 0,
            'error': f'Exit code: {e.returncode}'
        }

def analyze_integration_tests():
    """Analyze all integration test files."""
    integration_dir = Path("tests/integration")
    
    if not integration_dir.exists():
        print("❌ Integration tests directory not found")
        return
    
    test_files = list(integration_dir.glob("test_*.py"))
    
    print("🔍 Analyzing Integration Tests")
    print("=" * 60)
    
    working_tests = []
    failing_tests = []
    timeout_tests = []
    
    for test_file in test_files:
        result = test_single_test_file(test_file)
        
        if result['status'] == 'PASSED':
            working_tests.append((test_file.name, result))
            print(f"✅ {test_file.name}: {result['test_count']} tests passed in {result['duration']:.2f}s")
        elif result['status'] == 'TIMEOUT':
            timeout_tests.append((test_file.name, result))
            print(f"⏰ {test_file.name}: TIMEOUT after {result['duration']}s")
        else:
            failing_tests.append((test_file.name, result))
            print(f"❌ {test_file.name}: FAILED - {result['error']}")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    print(f"✅ Working Tests: {len(working_tests)}")
    for test_name, result in working_tests:
        print(f"   - {test_name}: {result['test_count']} tests, {result['duration']:.2f}s")
    
    print(f"\n⏰ Hanging/Timeout Tests: {len(timeout_tests)}")
    for test_name, result in timeout_tests:
        print(f"   - {test_name}: {result['error']}")
    
    print(f"\n❌ Failing Tests: {len(failing_tests)}")
    for test_name, result in failing_tests:
        print(f"   - {test_name}: {result['error']}")
    
    print(f"\n📈 Total Test Files: {len(test_files)}")
    print(f"🎯 Success Rate: {len(working_tests)/len(test_files)*100:.1f}%")
    
    # Recommendations
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATIONS")
    print("=" * 60)
    
    if timeout_tests:
        print("🔧 For hanging/timeout tests:")
        print("   - These tests are likely using the real app with middleware")
        print("   - Consider creating minimal versions like test_api_endpoints_minimal.py")
        print("   - Mock external dependencies (OpenAI, Qdrant)")
        print("   - Use TestClient instead of AsyncClient for simple tests")
    
    if failing_tests:
        print("🔧 For failing tests:")
        print("   - Check for missing environment variables")
        print("   - Verify all dependencies are installed")
        print("   - Review test setup and teardown")
    
    print("\n🚀 Recommended for CI/CD:")
    for test_name, result in working_tests:
        print(f"   - {test_name}")

def main():
    """Main function."""
    analyze_integration_tests()

if __name__ == "__main__":
    main() 