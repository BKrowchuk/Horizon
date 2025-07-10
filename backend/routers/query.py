from fastapi import APIRouter, HTTPException
from models.query import QueryRequest, QueryResponse
from pathlib import Path
import json

router = APIRouter()

@router.post("/query", response_model=QueryResponse, summary="Query processed content", tags=["query"])
async def query_content(request: QueryRequest):
    """
    Query processed content and data
    
    - **request**: Query request with file_id and query parameters
    - **returns**: Query response with results and confidence scores
    """
    try:
        # Check if file exists
        file_path = Path(f"storage/audio/{request.file_id}")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # TODO: Implement actual query processing logic
        # This is a placeholder for the query service
        
        # Load available data
        transcript_path = Path(f"storage/transcripts/{request.file_id}.json")
        summary_path = Path(f"storage/outputs/{request.file_id}_summary.json")
        insights_path = Path(f"storage/outputs/{request.file_id}_insights.json")
        
        available_data = {}
        
        if transcript_path.exists():
            with open(transcript_path, "r") as f:
                available_data["transcript"] = json.load(f)
        
        if summary_path.exists():
            with open(summary_path, "r") as f:
                available_data["summary"] = json.load(f)
        
        if insights_path.exists():
            with open(insights_path, "r") as f:
                available_data["insights"] = json.load(f)
        
        # Process query based on type
        query_result = {
            "file_id": request.file_id,
            "query_type": request.query_type,
            "query_text": request.query_text,
            "result": f"Query result for: {request.query_text}",
            "confidence": 0.85,
            "sources": list(available_data.keys())
        }
        
        return QueryResponse(
            success=True,
            file_id=request.file_id,
            query_type=query_result["query_type"],
            query_text=query_result["query_text"],
            result=query_result["result"],
            confidence=query_result["confidence"],
            sources=query_result["sources"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@router.get("/query/{file_id}/history", summary="Get query history", tags=["query"])
async def get_query_history(file_id: str):
    """
    Get query history for a file
    
    - **file_id**: ID of the file to get query history for
    - **returns**: Query history for the file
    """
    # TODO: Implement query history tracking
    return {"file_id": file_id, "queries": []}

@router.get("/query/suggestions", summary="Get query suggestions", tags=["query"])
async def get_query_suggestions():
    """
    Get query suggestions
    
    - **returns**: List of suggested queries
    """
    suggestions = [
        "What are the main topics discussed?",
        "What is the sentiment of the content?",
        "What are the key entities mentioned?",
        "What are the main action items?",
        "What is the overall summary?"
    ]
    return {"suggestions": suggestions}