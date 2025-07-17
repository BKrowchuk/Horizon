from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from agents.query_agent import query_meeting

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class QueryRequest(BaseModel):
    """Request model for meeting queries"""
    meeting_id: str
    query: str

class Source(BaseModel):
    """Source information for query results"""
    chunk_id: int
    similarity_score: float
    text_preview: str

class QueryResponse(BaseModel):
    """Response model for meeting queries"""
    meeting_id: str
    query: str
    answer: str
    sources: List[Source]
    timestamp: str

@router.post("/query", response_model=QueryResponse, summary="Query meeting content", tags=["query"])
async def query_meeting_content(request: QueryRequest):
    """
    Query meeting content using semantic search
    
    - **meeting_id**: ID of the meeting to query
    - **query**: The question to ask about the meeting
    - **returns**: Query response with answer and sources
    """
    try:
        # Validate input
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if not request.meeting_id.strip():
            raise HTTPException(status_code=400, detail="Meeting ID cannot be empty")
        
        logger.info(f"Processing query for meeting_id: {request.meeting_id}")
        
        # Call the query agent
        result = query_meeting(request.meeting_id, request.query)
        
        # Convert sources to Source objects
        sources = [
            Source(
                chunk_id=source["chunk_id"],
                similarity_score=source["similarity_score"],
                text_preview=source["text_preview"]
            )
            for source in result["sources"]
        ]
        
        # Create response
        response = QueryResponse(
            meeting_id=result["meeting_id"],
            query=result["query"],
            answer=result["answer"],
            sources=sources,
            timestamp=result["timestamp"]
        )
        
        logger.info(f"Query completed successfully for meeting_id: {request.meeting_id}")
        return response
        
    except FileNotFoundError as e:
        logger.error(f"Files not found for meeting_id {request.meeting_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Meeting or vector index not found: {str(e)}")
        
    except Exception as e:
        logger.error(f"Query failed for meeting_id {request.meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@router.get("/query/{meeting_id}/history", summary="Get query history", tags=["query"])
async def get_query_history(meeting_id: str):
    """
    Get query history for a meeting
    
    - **meeting_id**: ID of the meeting to get query history for
    - **returns**: Query history for the meeting
    """
    try:
        from pathlib import Path
        import json
        
        queries_file_path = Path(f"storage/outputs/{meeting_id}_queries.json")
        
        if not queries_file_path.exists():
            return {"meeting_id": meeting_id, "queries": []}
        
        with open(queries_file_path, "r", encoding="utf-8") as f:
            queries_data = json.load(f)
        
        return {"meeting_id": meeting_id, "queries": queries_data}
        
    except Exception as e:
        logger.error(f"Failed to get query history for meeting_id {meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get query history: {str(e)}")

@router.get("/query/suggestions", summary="Get query suggestions", tags=["query"])
async def get_query_suggestions():
    """
    Get query suggestions
    
    - **returns**: List of suggested queries
    """
    suggestions = [
        "What are the main topics discussed?",
        "What action items were mentioned?",
        "What decisions were made?",
        "Who were the key participants?",
        "What was the overall sentiment?",
        "What challenges were identified?",
        "What solutions were proposed?",
        "What is the next meeting about?",
        "What deadlines were mentioned?",
        "What resources were discussed?"
    ]
    return {"suggestions": suggestions}