#!/usr/bin/env python3
"""
Simple API test script for flowchart functionality
"""

import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from fastapi.testclient import TestClient
from main import app

def test_flowchart_api():
    """Test the flowchart API endpoints"""
    
    print("=== Testing Flowchart API ===")
    
    client = TestClient(app)
    
    # Find an existing transcript
    transcript_path = Path("storage/transcripts")
    if not transcript_path.exists():
        print("No transcripts directory found. Please run the pipeline first.")
        return
    
    transcript_files = list(transcript_path.glob("*.json"))
    if not transcript_files:
        print("No transcript files found. Please run the pipeline first.")
        return
    
    test_meeting_id = transcript_files[0].stem
    print(f"Using meeting_id: {test_meeting_id}")
    
    try:
        # Test Mermaid flowchart generation
        print("\n--- Testing Mermaid Flowchart API ---")
        mermaid_response = client.post("/api/v1/flowchart/", json={
            "meeting_id": test_meeting_id,
            "format_type": "mermaid"
        })
        
        print(f"Status Code: {mermaid_response.status_code}")
        if mermaid_response.status_code == 200:
            mermaid_data = mermaid_response.json()
            print(f"✓ Mermaid API call successful!")
            print(f"Format Type: {mermaid_data['format_type']}")
            print(f"Flowchart (first 100 chars): {mermaid_data['flowchart'][:100]}...")
            print(f"Mermaid Flowchart (first 100 chars): {mermaid_data['mermaid_flowchart'][:100]}...")
        else:
            print(f"✗ Mermaid API call failed: {mermaid_response.json()}")
        
        # Test Interactive flowchart generation
        print("\n--- Testing Interactive Flowchart API ---")
        interactive_response = client.post("/api/v1/flowchart/", json={
            "meeting_id": test_meeting_id,
            "format_type": "interactive"
        })
        
        print(f"Status Code: {interactive_response.status_code}")
        if interactive_response.status_code == 200:
            interactive_data = interactive_response.json()
            print(f"✓ Interactive API call successful!")
            print(f"Format Type: {interactive_data['format_type']}")
            
            if isinstance(interactive_data['flowchart'], dict):
                nodes = interactive_data['flowchart'].get('nodes', [])
                connections = interactive_data['flowchart'].get('connections', [])
                print(f"Nodes: {len(nodes)}, Connections: {len(connections)}")
            print(f"Interactive also includes Mermaid (first 100 chars): {interactive_data['mermaid_flowchart'][:100]}...")
        else:
            print(f"✗ Interactive API call failed: {interactive_response.json()}")
        
        # Test invalid format type
        print("\n--- Testing Invalid Format Type ---")
        invalid_response = client.post("/api/v1/flowchart/", json={
            "meeting_id": test_meeting_id,
            "format_type": "invalid_format"
        })
        
        print(f"Status Code: {invalid_response.status_code}")
        if invalid_response.status_code == 400:
            print(f"✓ Invalid format type correctly rejected: {invalid_response.json()['detail']}")
        else:
            print(f"✗ Invalid format type not properly handled")
        
        # Test non-existent meeting
        print("\n--- Testing Non-existent Meeting ---")
        nonexistent_response = client.post("/api/v1/flowchart/", json={
            "meeting_id": "nonexistent_meeting",
            "format_type": "mermaid"
        })
        
        print(f"Status Code: {nonexistent_response.status_code}")
        if nonexistent_response.status_code == 404:
            print(f"✓ Non-existent meeting correctly rejected: {nonexistent_response.json()['detail']}")
        else:
            print(f"✗ Non-existent meeting not properly handled")
        
        # Test GET endpoint
        print("\n--- Testing GET Flowchart Endpoint ---")
        get_response = client.get(f"/api/v1/flowchart/{test_meeting_id}")
        
        print(f"Status Code: {get_response.status_code}")
        if get_response.status_code == 200:
            get_data = get_response.json()
            print(f"✓ GET endpoint successful!")
            print(f"Retrieved format type: {get_data.get('format_type')}")
        else:
            print(f"✗ GET endpoint failed: {get_response.json()}")
        
        # Test status endpoint
        print("\n--- Testing Status Endpoint ---")
        status_response = client.get(f"/api/v1/flowchart/{test_meeting_id}/status")
        
        print(f"Status Code: {status_response.status_code}")
        if status_response.status_code == 200:
            status_data = status_response.json()
            print(f"✓ Status endpoint successful!")
            print(f"Status: {status_data.get('status')}")
            print(f"Format Type: {status_data.get('format_type')}")
        else:
            print(f"✗ Status endpoint failed: {status_response.json()}")
        
        print("\n=== All API tests completed! ===")
        
    except Exception as e:
        print(f"✗ API test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_flowchart_api() 