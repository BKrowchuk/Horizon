from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import logging
from agents.embedding_agent import embed_transcript

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vectorize", tags=["vectorize"])

class VectorizeRequest(BaseModel):
    meeting_id: str

class VectorizeResponse(BaseModel):
    meeting_id: str
    num_chunks: int
    status: str = "done"

@router.post("/", response_model=VectorizeResponse)
async def vectorize_meeting_transcript(request: VectorizeRequest):
    """
    Vectorize a meeting transcript using OpenAI's embedding API and store in FAISS index
    """
    try:
        logger.info(f"Starting vectorization for meeting_id: {request.meeting_id}")
        
        result = embed_transcript(request.meeting_id)
        
        logger.info(f"Vectorization completed for meeting_id: {request.meeting_id}")
        return VectorizeResponse(
            meeting_id=result["meeting_id"],
            num_chunks=result["num_chunks"],
            status="done"
        )
        
    except FileNotFoundError as e:
        logger.error(f"Transcript file not found for meeting_id {request.meeting_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Transcript not found: {str(e)}")
        
    except Exception as e:
        logger.error(f"Vectorization failed for meeting_id {request.meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Vectorization failed: {str(e)}")
