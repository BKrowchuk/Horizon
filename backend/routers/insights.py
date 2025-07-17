from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from pathlib import Path
import json
from agents.insights_agent import generate_insights

router = APIRouter()

class InsightsRequest(BaseModel):
    """Request model for insights generation"""
    file_id: str  # Using file_id to match existing model pattern

@router.post("/insights", summary="Generate meeting insights with audio analysis", tags=["insights"])
async def generate_meeting_insights(request: InsightsRequest) -> Dict[str, Any]:
    """
    Generate insights from a meeting transcript and audio recording using OpenAI
    
    - **request**: Insights request with file_id
    - **returns**: Insights data with meeting_id, project_id, created_at, insights, and important_moments
    """
    try:
        # Construct audio file path
        backend_dir = Path(__file__).parent.parent
        audio_file_path = backend_dir / f"storage/audio/{request.file_id}_audio.m4a"
        
        # Call the insights agent with audio file if it exists
        if audio_file_path.exists():
            insights_data = generate_insights(request.file_id, str(audio_file_path))
        else:
            # Fall back to transcript-only analysis
            insights_data = generate_insights(request.file_id)
        
        return insights_data
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@router.get("/insights/{file_id}", summary="Get insights for file", tags=["insights"])
async def get_insights(file_id: str):
    """
    Get insights for a specific file
    
    - **file_id**: ID of the file to get insights for
    - **returns**: Insights data for the file
    """
    insights_path = Path(f"storage/outputs/{file_id}_insights.json")
    if insights_path.exists():
        with open(insights_path, "r") as f:
            data = json.load(f)
        return data
    else:
        raise HTTPException(status_code=404, detail="Insights not found")