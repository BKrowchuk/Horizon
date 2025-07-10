#!/usr/bin/env python3
"""
Test runner for all tests in the tests directory
"""
import sys
import subprocess
from pathlib import Path

def check_server_running():
    """Check if the server is running on localhost:8000"""
    try:
        import requests
        response = requests.get("http://localhost:8000/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_all_tests():
    """Run all test files in the tests directory"""
    tests_dir = Path(__file__).parent
    test_files = list(tests_dir.glob("test_*.py"))
    
    # Filter out run_tests.py and count actual test files
    actual_test_files = [f for f in sorted(test_files) if f.name != "run_tests.py"]
    
    # Check if server is running
    print("Checking if server is running...")
    if not check_server_running():
        print("Server is not running on localhost:8000")
        print("Please start the server with: python main.py")
        return False
    
    print("Server is running!")
    print(f"Running {len(actual_test_files)} tests...")
    print("=" * 50)
    
    results = []
    
    for test_file in actual_test_files:
        
        print(f"\nRunning: {test_file.name}")
        print("-" * 30)
        
        try:
            # Run the test file
            result = subprocess.run(
                [sys.executable, str(test_file)],
                capture_output=True,
                text=True,
                cwd=tests_dir.parent  # Run from backend directory
            )
            
            if result.returncode == 0:
                print("PASSED")
                if result.stdout.strip():
                    print(f"Output: {result.stdout.strip()}")
                results.append((test_file.name, True, result.stdout))
            else:
                print("FAILED")
                if result.stderr.strip():
                    print(f"Error: {result.stderr.strip()}")
                if result.stdout.strip():
                    print(f"Output: {result.stdout.strip()}")
                results.append((test_file.name, False, result.stderr))
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append((test_file.name, False, str(e)))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, output in results:
        status = "PASSED" if success else "FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed!")
        return True
    else:
        print("Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 