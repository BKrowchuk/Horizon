from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from agents.embedding_agent import embed_transcript, search_similar_chunks

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/embedding", tags=["embedding"])

class EmbeddingRequest(BaseModel):
    meeting_id: str

class EmbeddingResponse(BaseModel):
    meeting_id: str
    num_chunks: int
    vector_index_path: str
    meta_path: str
    status: str = "completed"

class SearchRequest(BaseModel):
    meeting_id: str
    query_text: str
    top_k: Optional[int] = 5

class SearchResult(BaseModel):
    rank: int
    chunk_id: int
    text: str
    similarity_score: float
    distance: float

class SearchResponse(BaseModel):
    meeting_id: str
    query_text: str
    results: List[SearchResult]
    total_results: int

@router.post("/embed", response_model=EmbeddingResponse)
async def embed_meeting_transcript(request: EmbeddingRequest):
    """
    Embed a meeting transcript using OpenAI's embedding API and store in FAISS index
    """
    try:
        logger.info(f"Starting embedding for meeting_id: {request.meeting_id}")
        
        result = embed_transcript(request.meeting_id)
        
        logger.info(f"Embedding completed for meeting_id: {request.meeting_id}")
        return EmbeddingResponse(**result)
        
    except FileNotFoundError as e:
        logger.error(f"Transcript file not found for meeting_id {request.meeting_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Transcript not found: {str(e)}")
        
    except Exception as e:
        logger.error(f"Embedding failed for meeting_id {request.meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {str(e)}")

@router.post("/search", response_model=SearchResponse)
async def search_similar_chunks_api(request: SearchRequest):
    """
    Search for similar chunks in the embedding index
    """
    try:
        logger.info(f"Searching for query: '{request.query_text}' in meeting_id: {request.meeting_id}")
        
        results = search_similar_chunks(
            meeting_id=request.meeting_id,
            query_text=request.query_text,
            top_k=request.top_k
        )
        
        # Convert results to SearchResult objects
        search_results = [
            SearchResult(
                rank=result["rank"],
                chunk_id=result["chunk_id"],
                text=result["text"],
                similarity_score=result["similarity_score"],
                distance=result["distance"]
            )
            for result in results
        ]
        
        logger.info(f"Search completed for meeting_id: {request.meeting_id}, found {len(results)} results")
        
        return SearchResponse(
            meeting_id=request.meeting_id,
            query_text=request.query_text,
            results=search_results,
            total_results=len(search_results)
        )
        
    except FileNotFoundError as e:
        logger.error(f"Embedding files not found for meeting_id {request.meeting_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Embedding index not found: {str(e)}")
        
    except Exception as e:
        logger.error(f"Search failed for meeting_id {request.meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/status/{meeting_id}")
async def get_embedding_status(meeting_id: str):
    """
    Check if embedding exists for a meeting
    """
    from pathlib import Path
    
    vector_index_path = Path(f"storage/vectors/{meeting_id}.index")
    meta_file_path = Path(f"storage/vectors/{meeting_id}_meta.json")
    
    if vector_index_path.exists() and meta_file_path.exists():
        try:
            # Load metadata to get additional info
            import json
            with open(meta_file_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            return {
                "meeting_id": meeting_id,
                "status": "embedded",
                "num_chunks": metadata.get("num_chunks", 0),
                "embedding_model": metadata.get("embedding_model", "unknown"),
                "created_at": metadata.get("created_at")
            }
        except Exception as e:
            logger.error(f"Error reading embedding metadata for {meeting_id}: {str(e)}")
            return {
                "meeting_id": meeting_id,
                "status": "embedded",
                "error": "Could not read metadata"
            }
    else:
        return {
            "meeting_id": meeting_id,
            "status": "not_embedded"
        } 