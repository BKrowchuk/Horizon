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

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__]) 