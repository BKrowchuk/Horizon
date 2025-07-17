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
    """Test the transcription endpoint using RiverKiller.mp3 in the tests folder"""
    
    # Use provided meeting_id or generate a unique one
    if meeting_id is None:
        meeting_id = str(uuid.uuid4())
    
    # Use RiverKiller.mp3 in the current tests directory
    audio_path = Path(__file__).parent / "RiverKiller.mp3"
    if not audio_path.exists():
        print(f"Audio file not found: {audio_path}")
        return False, None
    print(f"Audio file found: {audio_path}")
    
    # Upload the file first
    upload_url = "http://localhost:8000/api/v1/upload"
    uploaded_filename = None
    try:
        with open(audio_path, "rb") as audio_file:
            files = {"file": (audio_path.name, audio_file, "audio/mpeg")}
            upload_response = requests.post(upload_url, files=files)
        if upload_response.status_code != 200:
            print(f"Upload failed: {upload_response.text}")
            return False, None
        upload_data = upload_response.json()
        uploaded_filename = upload_data.get("filename")
        if not uploaded_filename:
            print("Upload response missing filename")
            return False, None
        print(f"File uploaded as: {uploaded_filename}")
        # Extract meeting_id from filename
        meeting_id = uploaded_filename.split("_audio")[0]
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return False, None
    
    # Test the API endpoint
    url = "http://localhost:8000/api/v1/transcribe"
    payload = {"meeting_id": meeting_id}
    try:
        print(f"Making POST request to {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        response = requests.post(url, json=payload)
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Transcription successful!")
            print(f"Response data: {json.dumps(data, indent=2)}")
            # Check if transcript file was created
            transcript_path = Path(__file__).parent.parent / f"storage/transcripts/{meeting_id}.json"
            if transcript_path.exists():
                print(f"Transcript file created: {transcript_path}")
                return True, {
                    "meeting_id": meeting_id,
                    "uploaded_filename": uploaded_filename,
                    "transcript_path": transcript_path
                }
            else:
                print(f"Transcript file not found: {transcript_path}")
                return False, None
        else:
            print(f"Transcription failed: {response.text}")
            return False, None
    except requests.exceptions.ConnectionError:
        print("Could not connect to server. Make sure the server is running on localhost:8000")
        return False, None
    except Exception as e:
        print(f"Error: {str(e)}")
        return False, None 