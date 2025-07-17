#!/usr/bin/env python3
"""
Test script for the upload pipeline
"""
import requests
import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the backend modules
sys.path.append(str(Path(__file__).parent.parent))

def test_upload():
    """Test the upload endpoint"""
    
    # Test data - use the RiverKiller.mp3 file in the tests directory
    audio_file_path = Path(__file__).parent / "RiverKiller.mp3"
    
    if not audio_file_path.exists():
        print(f"[ERROR] Test audio file not found: {audio_file_path}")
        return False, None
    
    print(f"[OK] Test audio file found: {audio_file_path}")
    
    # Test the API endpoint
    url = "http://localhost:8000/api/v1/upload"
    
    try:
        print(f"[REQUEST] Making POST request to {url}")
        print(f"[FILE] Uploading file: {audio_file_path.name}")
        
        with open(audio_file_path, "rb") as audio_file:
            files = {"file": (audio_file_path.name, audio_file, "audio/mpeg")}
            response = requests.post(url, files=files)
        
        print(f"[STATUS] Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] Upload successful!")
            print(f"[DATA] Response data: {json.dumps(data, indent=2)}")
            
            # Extract meeting_id from response
            meeting_id = data.get("meeting_id")
            filename = data.get("filename")
            
            if meeting_id and filename:
                print(f"[OK] Meeting ID: {meeting_id}")
                print(f"[OK] Filename: {filename}")
                
                # Check if file was actually saved
                saved_file_path = Path(__file__).parent.parent / f"storage/audio/{filename}"
                
                if saved_file_path.exists():
                    print(f"[OK] File successfully saved: {saved_file_path}")
                    
                    # Test the status endpoint
                    status_url = f"http://localhost:8000/api/v1/upload/status/{filename}"
                    print(f"[REQUEST] Testing status endpoint: {status_url}")
                    
                    status_response = requests.get(status_url)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"[OK] Status check successful: {json.dumps(status_data, indent=2)}")
                        return True, {"meeting_id": meeting_id, "filename": filename, "file_path": saved_file_path}
                    else:
                        print(f"[ERROR] Status check failed: {status_response.text}")
                        return False, None
                else:
                    print(f"[ERROR] File not found in storage: {saved_file_path}")
                    return False, None
            else:
                print("[ERROR] Missing meeting_id or filename in response")
                return False, None
        else:
            print(f"[ERROR] Upload failed: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to server. Make sure the server is running on localhost:8000")
        return False, None
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False, None

def test_upload_invalid_file():
    """Test upload with invalid file type"""
    
    # Create a temporary text file with .txt extension
    temp_file_path = Path(__file__).parent / "temp_test.txt"
    with open(temp_file_path, "w") as f:
        f.write("This is not an audio file")
    
    try:
        url = "http://localhost:8000/api/v1/upload"
        
        print(f"[REQUEST] Testing invalid file upload to {url}")
        
        with open(temp_file_path, "rb") as temp_file:
            # Send as text/plain with .txt extension - should be rejected
            files = {"file": (temp_file_path.name, temp_file, "text/plain")}
            response = requests.post(url, files=files)
        
        print(f"[STATUS] Response status: {response.status_code}")
        
        if response.status_code == 400:
            print("[OK] Correctly rejected invalid file type")
            return True, None
        elif response.status_code == 500:
            # Check if the error message indicates validation failure
            try:
                error_data = response.json()
                if "File must be an audio file" in str(error_data):
                    print("[OK] Correctly rejected invalid file type (500 with validation message)")
                    return True, None
                else:
                    print(f"[ERROR] Unexpected 500 error: {error_data}")
                    return False, None
            except:
                print(f"[ERROR] Unexpected 500 error: {response.text}")
                return False, None
        else:
            print(f"[ERROR] Should have rejected invalid file, got status: {response.status_code}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to server. Make sure the server is running on localhost:8000")
        return False, None
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False, None
    finally:
        # Clean up temp file
        if temp_file_path.exists():
            temp_file_path.unlink() 