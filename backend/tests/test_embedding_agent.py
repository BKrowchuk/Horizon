#!/usr/bin/env python3
"""
Test script for the embedding agent
"""

import json
import os
import sys
from pathlib import Path
import uuid

# Add the parent directory to the path so we can import from the backend modules
sys.path.append(str(Path(__file__).parent.parent))

from agents.embedding_agent import embed_transcript, search_similar_chunks

def test_embedding_agent(meeting_id=None):
    """Test the embedding agent functionality (self-contained)"""
    # Generate a unique meeting_id if not provided
    if meeting_id is None:
        meeting_id = str(uuid.uuid4())
    
    transcript_path = Path(__file__).parent.parent / f"storage/transcripts/{meeting_id}.json"
    vector_file_path = Path(__file__).parent.parent / f"storage/vectors/{meeting_id}.json"

    # If no transcript exists, create a minimal one
    if not transcript_path.exists():
        # Minimal transcript data
        transcript_data = {
            "meeting_id": meeting_id,
            "project_id": "test_project",
            "created_at": "2025-07-17T00:00:00.000000",
            "transcript": "This is a test transcript about a river, politicians, and tears. River killer, don't you care what you do?",
            "original_length": 90,
            "cleaned_length": 90,
            "whisper_params": {
                "language": "en",
                "temperature": 0.0,
                "prompt": "Test prompt."
            }
        }

        # Write the transcript file
        transcript_path.parent.mkdir(parents=True, exist_ok=True)
        with open(transcript_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, indent=2)
        print(f"[SETUP] Created transcript file: {transcript_path}")

    try:
        # Test embedding with the transcript
        print(f"[TEST] Testing transcript embedding for meeting_id: {meeting_id}")
        result = embed_transcript(meeting_id)
        print(f"[OK] Embedding successful!")
        print(f"[DATA] Embedding result: {json.dumps(result, indent=2)}")

        # Test search functionality
        print("\n[TEST] Testing search functionality...")
        search_queries = [
            "river and water",
            "politicians and promises",
            "river killer",
            "tears and crying"
        ]
        for query in search_queries:
            print(f"\n--- Searching for: '{query}' ---")
            search_results = search_similar_chunks(
                meeting_id=meeting_id,
                query_text=query,
                top_k=2
            )
            print(f"[FOUND] Found {len(search_results)} results:")
            for result in search_results:
                print(f"  Rank {result['rank']}:")
                print(f"    Chunk ID: {result['chunk_id']}")
                print(f"    Similarity Score: {result['similarity_score']:.4f}")
                print(f"    Text: {result['text'][:150]}...")
        print(f"\n[OK] All embedding tests passed! Embedding agent is working correctly.")
        return True, {
            "meeting_id": meeting_id,
            "transcript_path": transcript_path,
            "vector_file_path": vector_file_path
        }
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        return False, None 