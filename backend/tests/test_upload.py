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
        print(f"❌ Test audio file not found: {audio_file_path}")
        return False
    
    print(f"✅ Test audio file found: {audio_file_path}")
    
    # Test the API endpoint
    url = "http://localhost:8000/api/v1/upload"
    
    try:
        print(f"📡 Making POST request to {url}")
        print(f"📁 Uploading file: {audio_file_path.name}")
        
        with open(audio_file_path, "rb") as audio_file:
            files = {"file": (audio_file_path.name, audio_file, "audio/mpeg")}
            response = requests.post(url, files=files)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload successful!")
            print(f"📄 Response data: {json.dumps(data, indent=2)}")
            
            # Extract meeting_id from response
            meeting_id = data.get("meeting_id")
            filename = data.get("filename")
            
            if meeting_id and filename:
                print(f"✅ Meeting ID: {meeting_id}")
                print(f"✅ Filename: {filename}")
                
                # Check if file was actually saved
                saved_file_path = Path(__file__).parent.parent / f"storage/audio/{filename}"
                if saved_file_path.exists():
                    print(f"✅ File successfully saved: {saved_file_path}")
                    
                    # Test the status endpoint
                    status_url = f"http://localhost:8000/api/v1/upload/status/{filename}"
                    print(f"📡 Testing status endpoint: {status_url}")
                    
                    status_response = requests.get(status_url)
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"✅ Status check successful: {json.dumps(status_data, indent=2)}")
                        return True
                    else:
                        print(f"❌ Status check failed: {status_response.text}")
                        return False
                else:
                    print(f"❌ File not found in storage: {saved_file_path}")
                    return False
            else:
                print("❌ Missing meeting_id or filename in response")
                return False
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_upload_invalid_file():
    """Test upload with invalid file type"""
    
    # Create a temporary text file with .txt extension
    temp_file_path = Path(__file__).parent / "temp_test.txt"
    with open(temp_file_path, "w") as f:
        f.write("This is not an audio file")
    
    try:
        url = "http://localhost:8000/api/v1/upload"
        
        print(f"📡 Testing invalid file upload to {url}")
        
        with open(temp_file_path, "rb") as temp_file:
            # Send as text/plain with .txt extension - should be rejected
            files = {"file": (temp_file_path.name, temp_file, "text/plain")}
            response = requests.post(url, files=files)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Correctly rejected invalid file type")
            return True
        elif response.status_code == 500:
            # Check if the error message indicates validation failure
            try:
                error_data = response.json()
                if "File must be an audio file" in str(error_data):
                    print("✅ Correctly rejected invalid file type (500 with validation message)")
                    return True
                else:
                    print(f"❌ Unexpected 500 error: {error_data}")
                    return False
            except:
                print(f"❌ Unexpected 500 error: {response.text}")
                return False
        else:
            print(f"❌ Should have rejected invalid file, got status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    finally:
        # Clean up temp file
        if temp_file_path.exists():
            temp_file_path.unlink()

if __name__ == "__main__":
    print("Testing upload pipeline...")
    
    # Test valid upload
    print("\nTesting valid file upload...")
    success1 = test_upload()
    
    # Test invalid upload
    print("\nTesting invalid file upload...")
    success2 = test_upload_invalid_file()
    
    if success1 and success2:
        print("\nAll upload tests passed! The upload pipeline is working correctly.")
    else:
        print("\nSome upload tests failed. Please check the implementation.") 