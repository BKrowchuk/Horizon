from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from agents.summary_agent import generate_summary

router = APIRouter()

class SummarizeRequest(BaseModel):
    """Request model for summarization"""
    meeting_id: str

@router.post("/summarize", summary="Generate meeting summary", tags=["summarize"])
async def summarize_meeting(request: SummarizeRequest) -> Dict[str, Any]:
    """
    Generate a summary of a meeting transcript using OpenAI
    
    - **request**: Summarize request with meeting_id
    - **returns**: Summary data with meeting_id, project_id, created_at, and summary
    """
    try:
        # Call the summary agent
        summary_data = generate_summary(request.meeting_id)
        
        return summary_data
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")