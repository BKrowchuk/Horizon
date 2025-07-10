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

def test_summary_generation():
    """Test the summary generation endpoint"""
    
    # Test data - use the same meeting_id as the transcription test
    meeting_id = "779b4f6b-44ff-4ec4-bdef-3eaa24bbc1d0"
    
    # Check if transcript file exists
    transcript_path = Path(__file__).parent.parent / f"storage/transcripts/{meeting_id}.json"
    if not transcript_path.exists():
        print(f"❌ Transcript file not found: {transcript_path}")
        print("💡 Please run the transcription test first to generate a transcript")
        return False
    
    print(f"✅ Transcript file found: {transcript_path}")
    
    # Test the API endpoint
    url = "http://localhost:8000/api/v1/summarize"
    payload = {"meeting_id": meeting_id}
    
    try:
        print(f"📡 Making POST request to {url}")
        print(f"📦 Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Summary generation successful!")
            print(f"📄 Response data: {json.dumps(data, indent=2)}")
            
            # Check if summary file was created
            summary_path = Path(__file__).parent.parent / f"storage/outputs/{meeting_id}_summary.json"
            if summary_path.exists():
                print(f"✅ Summary file created: {summary_path}")
                
                # Load and display the summary content
                with open(summary_path, "r") as f:
                    summary_data = json.load(f)
                print(f"📝 Summary: {summary_data.get('summary', 'No summary found')}")
                return True
            else:
                print(f"❌ Summary file not found: {summary_path}")
                return False
        else:
            print(f"❌ Summary generation failed: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_summary_agent_direct():
    """Test the summary agent directly without the API"""
    
    try:
        from agents.summary_agent import generate_summary
        
        # Test data - use the same meeting_id as the first test since we know it exists
        meeting_id = "779b4f6b-44ff-4ec4-bdef-3eaa24bbc1d0"
        
        # Check if transcript file exists
        transcript_path = Path(__file__).parent.parent / f"storage/transcripts/{meeting_id}.json"
        if not transcript_path.exists():
            print(f"❌ Transcript file not found: {transcript_path}")
            return False
        
        print(f"✅ Testing summary agent directly for meeting_id: {meeting_id}")
        
        # Call the summary agent directly
        summary_data = generate_summary(meeting_id)
        
        print("✅ Summary generation successful!")
        print(f"📄 Summary data: {json.dumps(summary_data, indent=2)}")
        
        # Check if summary file was created
        summary_path = Path(__file__).parent.parent / f"storage/outputs/{meeting_id}_summary.json"
        if summary_path.exists():
            print(f"✅ Summary file created: {summary_path}")
            return True
        else:
            print(f"❌ Summary file not found: {summary_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing summary agent directly: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing summary generation pipeline...")
    
    print("\nTesting API endpoint...")
    api_success = test_summary_generation()
    
    print("\nTesting summary agent directly...")
    direct_success = test_summary_agent_direct()
    
    if api_success and direct_success:
        print("\nAll tests passed! The summary generation pipeline is working correctly.")
    else:
        print("\nSome tests failed. Please check the implementation.") 