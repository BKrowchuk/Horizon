import openai
import faiss
import numpy as np
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def query_meeting(meeting_id: str, query: str) -> Dict[str, Any]:
    """
    Query a meeting using semantic search and OpenAI chat completion
    
    Args:
        meeting_id (str): The meeting ID to query
        query (str): The user's question
        
    Returns:
        Dict[str, Any]: Query result with answer and sources
    """
    try:
        logger.info(f"Starting query for meeting_id: {meeting_id}, query: '{query}'")
        
        # Construct file paths
        base_path = Path(__file__).parent.parent
        vector_index_path = base_path / f"storage/vectors/{meeting_id}.index"
        meta_file_path = base_path / f"storage/vectors/{meeting_id}_meta.json"
        transcript_file_path = base_path / f"storage/transcripts/{meeting_id}.json"
        queries_file_path = base_path / f"storage/outputs/{meeting_id}_queries.json"
        
        # Check if vector index exists
        if not vector_index_path.exists():
            raise FileNotFoundError(f"Vector index not found for meeting_id: {meeting_id}")
        
        if not meta_file_path.exists():
            raise FileNotFoundError(f"Vector metadata not found for meeting_id: {meeting_id}")
        
        # Load FAISS index
        logger.info(f"Loading FAISS index from {vector_index_path}")
        index = faiss.read_index(str(vector_index_path))
        
        # Load metadata
        logger.info(f"Loading metadata from {meta_file_path}")
        with open(meta_file_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        
        # Load original transcript for additional context
        transcript_data = {}
        if transcript_file_path.exists():
            logger.info(f"Loading transcript from {transcript_file_path}")
            with open(transcript_file_path, "r", encoding="utf-8") as f:
                transcript_data = json.load(f)
        
        # Generate embedding for the query
        logger.info("Generating embedding for user query")
        embedding_response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=query
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Convert query embedding to numpy array
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        # Search for similar chunks using FAISS
        logger.info("Searching for similar chunks")
        distances, indices = index.search(query_vector, k=5)  # Get top 5 results
        
        # Get relevant chunks from metadata
        vectors_data = metadata.get("vectors", [])
        relevant_chunks = []
        
        for i, (distance, chunk_idx) in enumerate(zip(distances[0], indices[0])):
            if chunk_idx < len(vectors_data):
                chunk_data = vectors_data[chunk_idx]
                similarity_score = 1.0 / (1.0 + distance)  # Convert distance to similarity
                
                relevant_chunks.append({
                    "chunk_id": chunk_idx,
                    "similarity_score": similarity_score,
                    "text": chunk_data["text"],
                    "text_preview": chunk_data["text"][:100] + "..." if len(chunk_data["text"]) > 100 else chunk_data["text"]
                })
        
        # Sort by similarity score (highest first)
        relevant_chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # If no relevant chunks found, return no information response
        if not relevant_chunks:
            logger.warning("No relevant chunks found for query")
            result = {
                "meeting_id": meeting_id,
                "query": query,
                "answer": "I don't have enough information to answer this question based on the meeting content.",
                "sources": [],
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Prepare context for OpenAI
            context_chunks = "\n\n".join([f"Chunk {i+1}: {chunk['text']}" for i, chunk in enumerate(relevant_chunks[:3])])
            
            # Call OpenAI Chat Completion API
            logger.info("Calling OpenAI Chat Completion API")
            chat_response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that answers questions about meeting content. Use only the provided meeting transcript chunks to answer the question. If the answer isn't contained in the chunks, say you don't have enough information. Be specific and cite relevant parts of the transcript."
                    },
                    {
                        "role": "user",
                        "content": f"Question: {query}\n\nMeeting transcript chunks:\n{context_chunks}"
                    }
                ],
                temperature=0.2,
                max_tokens=800
            )
            
            answer = chat_response.choices[0].message.content
            
            # Prepare sources
            sources = [
                {
                    "chunk_id": chunk["chunk_id"],
                    "similarity_score": chunk["similarity_score"],
                    "text_preview": chunk["text_preview"]
                }
                for chunk in relevant_chunks[:3]  # Top 3 sources
            ]
            
            result = {
                "meeting_id": meeting_id,
                "query": query,
                "answer": answer,
                "sources": sources,
                "timestamp": datetime.now().isoformat()
            }
        
        # Save query and response to file
        logger.info(f"Saving query result to {queries_file_path}")
        queries_data = []
        
        # Load existing queries if file exists
        if queries_file_path.exists():
            try:
                with open(queries_file_path, "r", encoding="utf-8") as f:
                    queries_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                queries_data = []
        
        # Append new query
        queries_data.append(result)
        
        # Ensure output directory exists
        queries_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save updated queries
        with open(queries_file_path, "w", encoding="utf-8") as f:
            json.dump(queries_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Query completed successfully for meeting_id: {meeting_id}")
        return result
        
    except FileNotFoundError as e:
        logger.error(f"File not found for meeting_id {meeting_id}: {str(e)}")
        raise Exception(f"Required files not found: {str(e)}")
        
    except Exception as e:
        logger.error(f"Query failed for meeting_id {meeting_id}: {str(e)}")
        raise Exception(f"Query failed: {str(e)}") 