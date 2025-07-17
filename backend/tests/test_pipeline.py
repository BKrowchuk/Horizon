import pytest
import os
import json
from pathlib import Path
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_pipeline_endpoint():
    """Test the pipeline endpoint with a sample audio file"""
    
    # Check if test audio file exists
    test_audio_path = Path("tests/RiverKiller.mp3")
    if not test_audio_path.exists():
        pytest.skip("Test audio file not found")
    
    # Test the pipeline endpoint
    with open(test_audio_path, "rb") as audio_file:
        files = {"file": ("RiverKiller.mp3", audio_file, "audio/mpeg")}
        response = client.post("/api/v1/pipeline/process-sync", files=files)
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "meeting_id" in data
    assert "filename" in data
    assert "status" in data
    assert "steps_completed" in data
    
    # Verify all steps were completed
    expected_steps = ["upload", "transcribe", "summarize", "embed"]
    assert all(step in data["steps_completed"] for step in expected_steps)
    
    # Verify data was generated
    assert data["transcript"] is not None
    assert data["summary"] is not None
    assert data["embedding"] is not None
    
    # Verify files were created
    meeting_id = data["meeting_id"]
    assert Path(f"storage/audio/{meeting_id}_audio.mp3").exists()
    assert Path(f"storage/transcripts/{meeting_id}.json").exists()
    assert Path(f"storage/outputs/{meeting_id}_summary.json").exists()
    assert Path(f"storage/vectors/{meeting_id}.index").exists()
    assert Path(f"storage/vectors/{meeting_id}_meta.json").exists()
    
    # Test flowchart generation for both formats
    test_flowchart_generation(meeting_id)
    
    # Test query functionality
    test_query_functionality(meeting_id)

def test_flowchart_generation(meeting_id: str):
    """Test flowchart generation for both mermaid and interactive formats"""
    
    print(f"\n=== Testing Flowchart Generation for meeting_id: {meeting_id} ===")
    
    # Test Mermaid flowchart generation
    print("\n--- Testing Mermaid Flowchart ---")
    mermaid_response = client.post("/api/v1/flowchart/", json={
        "meeting_id": meeting_id,
        "format_type": "mermaid"
    })
    
    assert mermaid_response.status_code == 200
    mermaid_data = mermaid_response.json()
    
    # Verify mermaid response structure
    assert mermaid_data["meeting_id"] == meeting_id
    assert mermaid_data["format_type"] == "mermaid"
    assert "flowchart" in mermaid_data
    assert "mermaid_flowchart" in mermaid_data
    assert isinstance(mermaid_data["flowchart"], str)
    assert isinstance(mermaid_data["mermaid_flowchart"], str)
    assert mermaid_data["flowchart"].startswith("flowchart TD")
    assert mermaid_data["mermaid_flowchart"].startswith("flowchart TD")
    
    # Display mermaid flowchart (truncated)
    mermaid_flowchart = mermaid_data["flowchart"]
    print(f"Mermaid Flowchart (first 200 chars): {mermaid_flowchart[:200]}...")
    
    # Test Interactive flowchart generation
    print("\n--- Testing Interactive Flowchart ---")
    interactive_response = client.post("/api/v1/flowchart/", json={
        "meeting_id": meeting_id,
        "format_type": "interactive"
    })
    
    assert interactive_response.status_code == 200
    interactive_data = interactive_response.json()
    
    # Verify interactive response structure
    assert interactive_data["meeting_id"] == meeting_id
    assert interactive_data["format_type"] == "interactive"
    assert "flowchart" in interactive_data
    assert "mermaid_flowchart" in interactive_data
    assert isinstance(interactive_data["flowchart"], dict)
    assert isinstance(interactive_data["mermaid_flowchart"], str)
    assert "nodes" in interactive_data["flowchart"]
    assert "connections" in interactive_data["flowchart"]
    assert interactive_data["mermaid_flowchart"].startswith("flowchart TD")
    
    # Display interactive flowchart structure
    nodes = interactive_data["flowchart"]["nodes"]
    connections = interactive_data["flowchart"]["connections"]
    print(f"Interactive Flowchart - Nodes: {len(nodes)}, Connections: {len(connections)}")
    print(f"First node: {nodes[0] if nodes else 'No nodes'}")
    print(f"Interactive also includes Mermaid (first 100 chars): {interactive_data['mermaid_flowchart'][:100]}...")
    
    # Verify flowchart files were created
    assert Path(f"storage/outputs/{meeting_id}_flowchart.json").exists()
    
    print("✓ Flowchart generation tests completed successfully!")

def test_query_functionality(meeting_id: str):
    """Test query functionality with sample questions"""
    
    print(f"\n=== Testing Query Functionality for meeting_id: {meeting_id} ===")
    
    # Test first query: "What were the main topics discussed?"
    print("\n--- Testing Query 1: Main Topics ---")
    query1_response = client.post("/api/v1/query/query", json={
        "meeting_id": meeting_id,
        "query": "What were the main topics discussed?"
    })
    
    assert query1_response.status_code == 200
    query1_data = query1_response.json()
    
    # Verify query1 response structure
    assert query1_data["meeting_id"] == meeting_id
    assert query1_data["query"] == "What were the main topics discussed?"
    assert "answer" in query1_data
    assert "sources" in query1_data
    assert "timestamp" in query1_data
    assert isinstance(query1_data["sources"], list)
    
    # Display query1 results
    print(f"Query 1 Answer: {query1_data['answer'][:200]}...")
    print(f"Query 1 Sources: {len(query1_data['sources'])} sources found")
    for i, source in enumerate(query1_data['sources'][:2]):  # Show first 2 sources
        print(f"  Source {i+1}: Score {source['similarity_score']:.3f}, Preview: {source['text_preview'][:100]}...")
    
    # Test second query: "What action items were mentioned?"
    print("\n--- Testing Query 2: Action Items ---")
    query2_response = client.post("/api/v1/query/query", json={
        "meeting_id": meeting_id,
        "query": "What action items were mentioned?"
    })
    
    assert query2_response.status_code == 200
    query2_data = query2_response.json()
    
    # Verify query2 response structure
    assert query2_data["meeting_id"] == meeting_id
    assert query2_data["query"] == "What action items were mentioned?"
    assert "answer" in query2_data
    assert "sources" in query2_data
    assert "timestamp" in query2_data
    assert isinstance(query2_data["sources"], list)
    
    # Display query2 results
    print(f"Query 2 Answer: {query2_data['answer'][:200]}...")
    print(f"Query 2 Sources: {len(query2_data['sources'])} sources found")
    for i, source in enumerate(query2_data['sources'][:2]):  # Show first 2 sources
        print(f"  Source {i+1}: Score {source['similarity_score']:.3f}, Preview: {source['text_preview'][:100]}...")
    
    # Verify query history file was created
    queries_file_path = Path(f"storage/outputs/{meeting_id}_queries.json")
    assert queries_file_path.exists()
    
    # Load and verify query history
    with open(queries_file_path, "r", encoding="utf-8") as f:
        queries_data = json.load(f)
    
    assert len(queries_data) >= 2
    assert queries_data[0]["query"] == "What were the main topics discussed?"
    assert queries_data[1]["query"] == "What action items were mentioned?"
    
    print("✓ Query functionality tests completed successfully!")

def test_pipeline_status_endpoint():
    """Test the pipeline status endpoint"""
    
    # First, process a file
    test_audio_path = Path("tests/RiverKiller.mp3")
    if not test_audio_path.exists():
        pytest.skip("Test audio file not found")
    
    with open(test_audio_path, "rb") as audio_file:
        files = {"file": ("RiverKiller.mp3", audio_file, "audio/mpeg")}
        response = client.post("/api/v1/pipeline/process-sync", files=files)
    
    assert response.status_code == 200
    meeting_id = response.json()["meeting_id"]
    
    # Check status
    status_response = client.get(f"/api/v1/pipeline/status/{meeting_id}")
    assert status_response.status_code == 200
    
    status_data = status_response.json()
    assert status_data["meeting_id"] == meeting_id
    assert status_data["status"] == "completed"
    assert len(status_data["steps_completed"]) == 4

def test_pipeline_invalid_file():
    """Test pipeline with invalid file type"""
    
    # Create a dummy text file
    dummy_file_content = b"This is not an audio file"
    
    files = {"file": ("test.txt", dummy_file_content, "text/plain")}
    response = client.post("/api/v1/pipeline/process-sync", files=files)
    
    assert response.status_code == 400
    assert "File must be an audio file" in response.json()["detail"]

def test_flowchart_invalid_format():
    """Test flowchart generation with invalid format type"""
    
    # First, process a file to get a meeting_id
    test_audio_path = Path("tests/RiverKiller.mp3")
    if not test_audio_path.exists():
        pytest.skip("Test audio file not found")
    
    with open(test_audio_path, "rb") as audio_file:
        files = {"file": ("RiverKiller.mp3", audio_file, "audio/mpeg")}
        response = client.post("/api/v1/pipeline/process-sync", files=files)
    
    assert response.status_code == 200
    meeting_id = response.json()["meeting_id"]
    
    # Test with invalid format type
    invalid_response = client.post("/api/v1/flowchart/", json={
        "meeting_id": meeting_id,
        "format_type": "invalid_format"
    })
    
    assert invalid_response.status_code == 400
    assert "format_type must be 'mermaid' or 'interactive'" in invalid_response.json()["detail"]

def test_flowchart_nonexistent_meeting():
    """Test flowchart generation with non-existent meeting"""
    
    response = client.post("/api/v1/flowchart/", json={
        "meeting_id": "nonexistent_meeting",
        "format_type": "mermaid"
    })
    
    assert response.status_code == 404
    assert "Transcript not found" in response.json()["detail"]

def test_query_invalid_meeting():
    """Test query with non-existent meeting"""
    
    response = client.post("/api/v1/query/query", json={
        "meeting_id": "nonexistent_meeting",
        "query": "What were the main topics?"
    })
    
    assert response.status_code == 404
    assert "Meeting or vector index not found" in response.json()["detail"]

def test_query_empty_query():
    """Test query with empty query string"""
    
    response = client.post("/api/v1/query/query", json={
        "meeting_id": "test_meeting",
        "query": ""
    })
    
    assert response.status_code == 400
    assert "Query cannot be empty" in response.json()["detail"]

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__]) 