#!/usr/bin/env python3
"""
Test runner for all tests in the tests directory
"""
import sys
import subprocess
from pathlib import Path

def run_all_tests():
    """Run all test files in the tests directory"""
    tests_dir = Path(__file__).parent
    test_files = list(tests_dir.glob("test_*.py"))
    
    print(f"🧪 Running {len(test_files)} tests...")
    print("=" * 50)
    
    results = []
    
    for test_file in test_files:
        if test_file.name == "run_tests.py":
            continue
            
        print(f"\n📋 Running: {test_file.name}")
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
                print("✅ PASSED")
                results.append((test_file.name, True, result.stdout))
            else:
                print("❌ FAILED")
                print(f"Error: {result.stderr}")
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
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 