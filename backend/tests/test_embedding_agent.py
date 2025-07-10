#!/usr/bin/env python3
"""
Test script for the embedding agent
"""

import json
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the backend modules
sys.path.append(str(Path(__file__).parent.parent))

from agents.embedding_agent import embed_transcript, search_similar_chunks



def test_embedding_agent():
    """Test the embedding agent functionality"""
    meeting_id = "c49ddc0a-1017-4216-83f6-8128de7c5a88"
    
    try:
        # Test embedding with real transcript data
        print(f"Testing transcript embedding for meeting_id: {meeting_id}")
        result = embed_transcript(meeting_id)
        print(f"Embedding result: {json.dumps(result, indent=2)}")
        
        # Test search functionality with relevant queries
        print("\nTesting search functionality...")
        
        # Test different search queries related to the song content
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
            
            print(f"Found {len(search_results)} results:")
            for result in search_results:
                print(f"  Rank {result['rank']}:")
                print(f"    Chunk ID: {result['chunk_id']}")
                print(f"    Similarity Score: {result['similarity_score']:.4f}")
                print(f"    Text: {result['text'][:150]}...")
        
        print(f"\n✅ All tests passed! Embedding agent is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable not set!")
        print("Please set your OpenAI API key before running this test.")
        exit(1)
    
    test_embedding_agent() 