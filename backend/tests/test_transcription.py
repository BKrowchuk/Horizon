#!/usr/bin/env python3
"""
Test script for the transcription pipeline
"""
import requests
import json
import sys
from pathlib import Path
import uuid

# Add the parent directory to the path so we can import from the backend modules
sys.path.append(str(Path(__file__).parent.parent))

def test_transcription(meeting_id=None):
    """Test the transcription endpoint using the uploaded file from the upload test"""
    
    if meeting_id is None:
        print("[ERROR] No meeting_id provided for transcription test")
        return False, None
    
    print(f"[INFO] Using meeting_id from upload test: {meeting_id}")
    
    # Test the transcription API endpoint directly (file should already be uploaded)
    url = "http://localhost:8000/api/v1/transcribe"
    payload = {"meeting_id": meeting_id}
    
    try:
        print(f"[REQUEST] Making POST request to {url}")
        print(f"[PAYLOAD] {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        print(f"[STATUS] Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] Transcription successful!")
            print(f"[DATA] Response data: {json.dumps(data, indent=2)}")
            
            # Check if transcript file was created
            transcript_path = Path(__file__).parent.parent / f"storage/transcripts/{meeting_id}.json"
            if transcript_path.exists():
                print(f"[OK] Transcript file created: {transcript_path}")
                return True, {
                    "meeting_id": meeting_id,
                    "transcript_path": transcript_path
                }
            else:
                print(f"[ERROR] Transcript file not found: {transcript_path}")
                return False, None
        else:
            print(f"[ERROR] Transcription failed: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to server. Make sure the server is running on localhost:8000")
        return False, None
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False, None 