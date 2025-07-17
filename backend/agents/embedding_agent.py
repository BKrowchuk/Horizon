import openai
import json
import os
import uuid
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv
import logging
import numpy as np
import faiss
import re

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def embed_transcript(meeting_id: str) -> Dict[str, Any]:
    """
    Embed transcript text into vector representations
    
    Args:
        meeting_id (str): The meeting ID
        
    Returns:
        Dict[str, Any]: Embedding metadata with meeting_id, num_chunks, vector_index_path, meta_path
    """
    # Construct file paths using absolute paths
    base_path = Path(__file__).parent.parent
    transcript_file_path = base_path / f"storage/transcripts/{meeting_id}.json"
    vector_index_path = base_path / f"storage/vectors/{meeting_id}.index"
    meta_file_path = base_path / f"storage/vectors/{meeting_id}_meta.json"
    
    # Check if transcript file exists
    if not transcript_file_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_file_path}")
    
    # Create vectors directory if it doesn't exist
    vector_index_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info(f"Starting embedding for meeting_id: {meeting_id}")
        
        # Load transcript data
        with open(transcript_file_path, "r", encoding="utf-8") as f:
            transcript_data = json.load(f)
        
        # Extract transcript text
        transcript_text = transcript_data.get("transcript", "")
        if not transcript_text:
            raise ValueError(f"No transcript text found for meeting_id: {meeting_id}")
        
        # Split transcript into chunks
        chunks = split_transcript_into_chunks(transcript_text)
        logger.info(f"Split transcript into {len(chunks)} chunks")
        
        # Generate embeddings for each chunk
        vectors_data = []
        embeddings_list = []
        
        for chunk_id, chunk_text in enumerate(chunks):
            logger.info(f"Generating embedding for chunk {chunk_id + 1}/{len(chunks)}")
            
            # Generate embedding using OpenAI API
            embedding_response = openai.embeddings.create(
                model="text-embedding-ada-002",
                input=chunk_text
            )
            
            embedding_vector = embedding_response.data[0].embedding
            
            # Store chunk data
            chunk_data = {
                "chunk_id": chunk_id,
                "text": chunk_text,
                "embedding": embedding_vector
            }
            vectors_data.append(chunk_data)
            embeddings_list.append(embedding_vector)
        
        # Convert embeddings to numpy array for FAISS
        embeddings_array = np.array(embeddings_list, dtype=np.float32)
        
        # Create FAISS index
        dimension = len(embeddings_array[0])
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings_array)
        
        # Save FAISS index
        faiss.write_index(index, str(vector_index_path))
        
        # Save metadata
        meta_data = {
            "meeting_id": meeting_id,
            "project_id": transcript_data.get("project_id", "demo_project"),
            "created_at": transcript_data.get("created_at"),
            "num_chunks": len(chunks),
            "chunk_size_words": 500,
            "overlap_words": 50,
            "embedding_model": "text-embedding-ada-002",
            "index_type": "IndexFlatL2",
            "dimension": dimension,
            "vectors": vectors_data
        }
        
        with open(meta_file_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Embedding completed successfully for meeting_id: {meeting_id}")
        
        return {
            "meeting_id": meeting_id,
            "num_chunks": len(chunks),
            "vector_index_path": str(vector_index_path),
            "meta_path": str(meta_file_path)
        }
        
    except Exception as e:
        logger.error(f"Embedding failed for meeting_id {meeting_id}: {str(e)}")
        raise Exception(f"Embedding failed: {str(e)}")

def split_transcript_into_chunks(text: str, chunk_size_words: int = 500, overlap_words: int = 50) -> List[str]:
    """
    Split transcript text into chunks with overlap
    
    Args:
        text (str): The transcript text to split
        chunk_size_words (int): Target number of words per chunk
        overlap_words (int): Number of words to overlap between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    if not text:
        return []
    
    # Split text into words
    words = text.split()
    
    if len(words) <= chunk_size_words:
        return [text]
    
    chunks = []
    start_idx = 0
    
    while start_idx < len(words):
        # Calculate end index for current chunk
        end_idx = min(start_idx + chunk_size_words, len(words))
        
        # Extract chunk
        chunk_words = words[start_idx:end_idx]
        chunk_text = " ".join(chunk_words)
        chunks.append(chunk_text)
        
        # Move start index for next chunk (with overlap)
        start_idx = end_idx - overlap_words
        
        # If we're at the end, break
        if end_idx >= len(words):
            break
    
    return chunks

def load_embedding_index(meeting_id: str) -> tuple:
    """
    Load FAISS index and metadata for a meeting
    
    Args:
        meeting_id (str): The meeting ID
        
    Returns:
        tuple: (faiss_index, metadata_dict)
    """
    base_path = Path(__file__).parent.parent
    vector_index_path = base_path / f"storage/vectors/{meeting_id}.index"
    meta_file_path = base_path / f"storage/vectors/{meeting_id}_meta.json"
    
    if not vector_index_path.exists() or not meta_file_path.exists():
        raise FileNotFoundError(f"Embedding files not found for meeting_id: {meeting_id}")
    
    # Load FAISS index
    index = faiss.read_index(str(vector_index_path))
    
    # Load metadata
    with open(meta_file_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    return index, metadata

def search_similar_chunks(meeting_id: str, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search for similar chunks in the embedding index
    
    Args:
        meeting_id (str): The meeting ID to search in
        query_text (str): The query text to search for
        top_k (int): Number of top results to return
        
    Returns:
        List[Dict[str, Any]]: List of similar chunks with scores
    """
    try:
        # Load index and metadata
        index, metadata = load_embedding_index(meeting_id)
        
        # Generate embedding for query
        query_embedding_response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=query_text
        )
        query_embedding = np.array([query_embedding_response.data[0].embedding], dtype=np.float32)
        
        # Search in FAISS index
        distances, indices = index.search(query_embedding, top_k)
        
        # Get results
        results = []
        vectors_data = metadata.get("vectors", [])
        
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(vectors_data):
                chunk_data = vectors_data[idx]
                results.append({
                    "rank": i + 1,
                    "chunk_id": chunk_data["chunk_id"],
                    "text": chunk_data["text"],
                    "similarity_score": 1.0 / (1.0 + distance),  # Convert distance to similarity
                    "distance": float(distance)
                })
        
        return results
        
    except Exception as e:
        logger.error(f"Search failed for meeting_id {meeting_id}: {str(e)}")
        raise Exception(f"Search failed: {str(e)}") 