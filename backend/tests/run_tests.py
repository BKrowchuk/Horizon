#!/usr/bin/env python3
"""
Test orchestrator for the Horizon backend pipeline
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from the backend modules
sys.path.append(str(Path(__file__).parent.parent))

# Import test functions
from test_upload import test_upload, test_upload_invalid_file
from test_transcription import test_transcription
from test_embedding_agent import test_embedding_agent
from test_summary_agent import test_summary_generation, test_summary_agent_direct

def check_server_running():
    """Check if the server is running on localhost:8000"""
    try:
        import requests
        response = requests.get("http://localhost:8000/docs", timeout=5)
        return response.status_code == 200
    except:
        return False

def cleanup_files(files_to_cleanup):
    """Clean up files created during testing"""
    print("\n" + "=" * 50)
    print("[CLEANUP] Cleaning up test files...")
    print("=" * 50)
    
    for file_path in files_to_cleanup:
        if file_path and file_path.exists():
            try:
                file_path.unlink()
                print(f"[CLEANUP] Deleted: {file_path}")
            except Exception as e:
                print(f"[WARNING] Failed to delete {file_path}: {str(e)}")

def run_pipeline_tests():
    """Run the complete pipeline test suite in order"""
    
    print("Horizon Backend Pipeline Test Suite")
    print("=" * 50)
    
    # Check if server is running
    print("Checking if server is running...")
    if not check_server_running():
        print("[ERROR] Server is not running on localhost:8000")
        print("[INFO] Please start the server with: python main.py")
        return False
    
    print("[OK] Server is running!")
    
    # Check if OpenAI API key is set (needed for embedding and summary)
    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY environment variable not set!")
        print("[INFO] Please set your OpenAI API key before running this test.")
        return False
    
    print("[OK] OpenAI API key is set!")
    
    # Track files to cleanup
    files_to_cleanup = []
    test_results = []
    
    try:
        # Test 1: Upload
        print("\n" + "=" * 50)
        print("[TEST] 1. Testing Upload Pipeline")
        print("=" * 50)
        
        success, upload_data = test_upload()
        test_results.append(("Upload", success))
        
        if not success:
            print("[ERROR] Upload test failed!")
            return False
        
        # Test invalid upload
        success_invalid, _ = test_upload_invalid_file()
        test_results.append(("Upload (Invalid)", success_invalid))
        
        if upload_data:
            files_to_cleanup.append(upload_data["file_path"])
        
        # Test 2: Transcription
        print("\n" + "=" * 50)
        print("[TEST] 2. Testing Transcription Pipeline")
        print("=" * 50)
        
        success, transcription_data = test_transcription(upload_data["meeting_id"])
        test_results.append(("Transcription", success))
        
        if not success:
            print("[ERROR] Transcription test failed!")
            return False
        
        if transcription_data:
            files_to_cleanup.append(transcription_data["transcript_path"])
            # Add the uploaded file from the upload test to cleanup
            files_to_cleanup.append(upload_data["file_path"])
        
        # Test 3: Embedding
        print("\n" + "=" * 50)
        print("[TEST] 3. Testing Embedding Pipeline")
        print("=" * 50)
        
        success, embedding_data = test_embedding_agent(transcription_data["meeting_id"])
        test_results.append(("Embedding", success))
        
        if not success:
            print("[ERROR] Embedding test failed!")
            return False
        
        if embedding_data:
            files_to_cleanup.append(embedding_data["vector_file_path"])
        
        # Test 4: Summary Generation
        print("\n" + "=" * 50)
        print("[TEST] 4. Testing Summary Generation Pipeline")
        print("=" * 50)
        
        # Test API endpoint
        success, summary_data = test_summary_generation(transcription_data["meeting_id"])
        test_results.append(("Summary (API)", success))
        
        if not success:
            print("[ERROR] Summary API test failed!")
            return False
        
        # Test direct agent
        success_direct, summary_direct_data = test_summary_agent_direct(transcription_data["meeting_id"])
        test_results.append(("Summary (Direct)", success_direct))
        
        if not success_direct:
            print("[ERROR] Summary direct test failed!")
            return False
        
        if summary_data:
            files_to_cleanup.append(summary_data["summary_path"])
        if summary_direct_data:
            files_to_cleanup.append(summary_direct_data["summary_path"])
        
        # All tests passed!
        print("\n" + "=" * 50)
        print("[SUCCESS] All Pipeline Tests Passed!")
        print("=" * 50)
        
        for test_name, success in test_results:
            status = "PASSED" if success else "FAILED"
            print(f"{test_name}: {status}")
        
        print(f"\n[STATS] Results: {sum(1 for _, success in test_results if success)}/{len(test_results)} tests passed")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test suite failed with exception: {str(e)}")
        return False
    
    # finally:
        # Cleanup all files
        cleanup_files(files_to_cleanup)

if __name__ == "__main__":
    success = run_pipeline_tests()
    sys.exit(0 if success else 1) 