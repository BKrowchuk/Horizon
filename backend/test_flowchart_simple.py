#!/usr/bin/env python3
"""
Simple test script for flowchart functionality
"""

import json
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from agents.flowchart_agent import generate_flowchart

def test_flowchart_agent():
    """Test the flowchart agent functionality"""
    
    print("=== Testing Flowchart Agent ===")
    
    # Check if we have a test transcript
    test_transcript_path = Path("storage/transcripts")
    if not test_transcript_path.exists():
        print("No transcripts directory found. Creating a test transcript...")
        
        # Create test transcript
        test_transcript_path.mkdir(parents=True, exist_ok=True)
        test_meeting_id = "test_meeting_001"
        
        test_transcript_data = {
            "meeting_id": test_meeting_id,
            "project_id": "test_project",
            "created_at": "2024-01-01T00:00:00",
            "transcript": """
            Meeting started at 10:00 AM.
            John: Let's discuss the project timeline.
            Sarah: I think we should start with the requirements gathering phase.
            John: Good idea. Then we can move to design and development.
            Sarah: What about testing?
            John: Yes, we need to include testing phase as well.
            Sarah: And deployment?
            John: Absolutely. So the phases are: requirements, design, development, testing, and deployment.
            Meeting ended at 11:00 AM.
            """
        }
        
        with open(f"storage/transcripts/{test_meeting_id}.json", "w") as f:
            json.dump(test_transcript_data, f, indent=2)
        
        print(f"Created test transcript for meeting_id: {test_meeting_id}")
    else:
        # Find an existing transcript
        transcript_files = list(test_transcript_path.glob("*.json"))
        if transcript_files:
            test_meeting_id = transcript_files[0].stem
            print(f"Using existing transcript: {test_meeting_id}")
        else:
            print("No transcript files found. Please run the pipeline first.")
            return
    
    try:
        # Test Mermaid flowchart generation
        print("\n--- Testing Mermaid Flowchart ---")
        mermaid_result = generate_flowchart(test_meeting_id, "mermaid")
        
        print(f"✓ Mermaid flowchart generated successfully!")
        print(f"Meeting ID: {mermaid_result['meeting_id']}")
        print(f"Format Type: {mermaid_result['format_type']}")
        print(f"Flowchart (first 200 chars): {mermaid_result['flowchart'][:200]}...")
        print(f"Mermaid Flowchart (first 200 chars): {mermaid_result['mermaid_flowchart'][:200]}...")
        
        # Test Interactive flowchart generation
        print("\n--- Testing Interactive Flowchart ---")
        interactive_result = generate_flowchart(test_meeting_id, "interactive")
        
        print(f"✓ Interactive flowchart generated successfully!")
        print(f"Meeting ID: {interactive_result['meeting_id']}")
        print(f"Format Type: {interactive_result['format_type']}")
        
        if isinstance(interactive_result['flowchart'], dict):
            nodes = interactive_result['flowchart'].get('nodes', [])
            connections = interactive_result['flowchart'].get('connections', [])
            print(f"Nodes: {len(nodes)}, Connections: {len(connections)}")
            if nodes:
                print(f"First node: {nodes[0]}")
        print(f"Interactive also includes Mermaid (first 100 chars): {interactive_result['mermaid_flowchart'][:100]}...")
        
        # Check if files were created
        flowchart_file = Path(f"storage/outputs/{test_meeting_id}_flowchart.json")
        if flowchart_file.exists():
            print(f"✓ Flowchart file created: {flowchart_file}")
        else:
            print(f"✗ Flowchart file not found: {flowchart_file}")
        
        print("\n=== All tests completed successfully! ===")
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_flowchart_agent() 