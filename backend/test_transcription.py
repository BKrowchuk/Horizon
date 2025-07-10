#!/usr/bin/env python3
"""
Test script for the transcription pipeline
"""
import requests
import json
from pathlib import Path

def test_transcription():
    """Test the transcription endpoint"""
    
    # Test data
    meeting_id = "bbd45fb8-a2a9-4708-b929-a9acb2fda37e"
    
    # Check if audio file exists
    audio_path = Path(f"storage/audio/{meeting_id}_audio.mp3")
    if not audio_path.exists():
        print(f"❌ Audio file not found: {audio_path}")
        return False
    
    print(f"✅ Audio file found: {audio_path}")
    
    # Test the API endpoint
    url = "http://localhost:8000/api/v1/transcribe"
    payload = {"meeting_id": meeting_id}
    
    try:
        print(f"📡 Making POST request to {url}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Transcription successful!")
            print(f"📄 Response data: {json.dumps(data, indent=2)}")
            
            # Check if transcript file was created
            transcript_path = Path(f"storage/transcripts/{meeting_id}.json")
            if transcript_path.exists():
                print(f"✅ Transcript file created: {transcript_path}")
                return True
            else:
                print(f"❌ Transcript file not found: {transcript_path}")
                return False
        else:
            print(f"❌ Transcription failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing transcription pipeline...")
    success = test_transcription()
    
    if success:
        print("\n🎉 All tests passed! The transcription pipeline is working correctly.")
    else:
        print("\n💥 Tests failed. Please check the implementation.") 