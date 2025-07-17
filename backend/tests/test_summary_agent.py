#!/usr/bin/env python3
"""
Test script for the summary agent
"""
import requests
import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the backend modules
sys.path.append(str(Path(__file__).parent.parent))

def test_summary_generation(meeting_id):
    """Test the summary generation endpoint"""
    
    # Check if transcript file exists
    transcript_path = Path(__file__).parent.parent / f"storage/transcripts/{meeting_id}.json"
    if not transcript_path.exists():
        print(f"[ERROR] Transcript file not found: {transcript_path}")
        print("[INFO] Please run the transcription test first to generate a transcript")
        return False, None
    
    print(f"[OK] Transcript file found: {transcript_path}")
    
    # Test the API endpoint
    url = "http://localhost:8000/api/v1/summarize"
    payload = {"meeting_id": meeting_id}
    
    try:
        print(f"[INFO] Making POST request to {url}")
        print(f"[INFO] Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        
        print(f"[INFO] Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("[OK] Summary generation successful!")
            print(f"[INFO] Response data: {json.dumps(data, indent=2)}")
            
            # Check if summary file was created
            summary_path = Path(__file__).parent.parent / f"storage/outputs/{meeting_id}_summary.json"
            if summary_path.exists():
                print(f"[OK] Summary file created: {summary_path}")
                
                # Load and display the summary content
                with open(summary_path, "r") as f:
                    summary_data = json.load(f)
                print(f"[INFO] Summary: {summary_data.get('summary', 'No summary found')}")
                return True, {"meeting_id": meeting_id, "summary_path": summary_path}
            else:
                print(f"[ERROR] Summary file not found: {summary_path}")
                return False, None
        else:
            print(f"[ERROR] Summary generation failed: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to server. Make sure the server is running on localhost:8000")
        return False, None
    except Exception as e:
        print(f"[ERROR] Error: {str(e)}")
        return False, None

def test_summary_agent_direct(meeting_id):
    """Test the summary agent directly without the API"""
    
    try:
        from agents.summary_agent import generate_summary
        
        # Check if transcript file exists
        transcript_path = Path(__file__).parent.parent / f"storage/transcripts/{meeting_id}.json"
        if not transcript_path.exists():
            print(f"[ERROR] Transcript file not found: {transcript_path}")
            return False, None
        
        print(f"[OK] Testing summary agent directly for meeting_id: {meeting_id}")
        
        # Call the summary agent directly
        summary_data = generate_summary(meeting_id)
        
        print("[OK] Summary generation successful!")
        print(f"[INFO] Summary data: {json.dumps(summary_data, indent=2)}")
        
        # Check if summary file was created
        summary_path = Path(__file__).parent.parent / f"storage/outputs/{meeting_id}_summary.json"
        if summary_path.exists():
            print(f"[OK] Summary file created: {summary_path}")
            return True, {"meeting_id": meeting_id, "summary_path": summary_path}
        else:
            print(f"[ERROR] Summary file not found: {summary_path}")
            return False, None
            
    except Exception as e:
        print(f"[ERROR] Error testing summary agent directly: {str(e)}")
        return False, None 