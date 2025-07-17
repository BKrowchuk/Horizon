from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from agents.flowchart_agent import generate_flowchart

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/flowchart", tags=["flowchart"])

class FlowchartRequest(BaseModel):
    meeting_id: str
    format_type: str = "mermaid"  # default to mermaid

class FlowchartResponse(BaseModel):
    meeting_id: str
    project_id: str
    created_at: str
    format_type: str
    flowchart: Any  # Can be string (mermaid) or dict (interactive)
    mermaid_flowchart: str  # Always includes mermaid version
    render_info: Dict[str, Any]

@router.post("/", response_model=FlowchartResponse, summary="Generate flowchart from meeting transcript", tags=["flowchart"])
async def generate_flowchart_endpoint(request: FlowchartRequest):
    """
    Generate a flowchart from meeting transcript
    
    - **meeting_id**: ID of the meeting to generate flowchart for
    - **format_type**: Type of flowchart format ("mermaid" or "interactive")
    - **returns**: Flowchart data with metadata
    """
    try:
        logger.info(f"Starting flowchart generation for meeting_id: {request.meeting_id}, format: {request.format_type}")
        
        # Generate flowchart using the agent
        result = generate_flowchart(request.meeting_id, request.format_type)
        
        logger.info(f"Flowchart generation completed for meeting_id: {request.meeting_id}")
        
        return FlowchartResponse(**result)
        
    except FileNotFoundError as e:
        logger.error(f"Transcript not found for meeting_id {request.meeting_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Transcript not found: {str(e)}")
        
    except ValueError as e:
        logger.error(f"Invalid request for meeting_id {request.meeting_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Flowchart generation failed for meeting_id {request.meeting_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Flowchart generation failed: {str(e)}")

@router.get("/{meeting_id}", summary="Get flowchart for meeting", tags=["flowchart"])
async def get_flowchart(meeting_id: str):
    """
    Get flowchart for a specific meeting
    
    - **meeting_id**: ID of the meeting to get flowchart for
    - **returns**: Flowchart data for the meeting
    """
    from pathlib import Path
    import json
    
    flowchart_path = Path(f"storage/outputs/{meeting_id}_flowchart.json")
    if flowchart_path.exists():
        try:
            with open(flowchart_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"Error reading flowchart for meeting_id {meeting_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reading flowchart: {str(e)}")
    else:
        raise HTTPException(status_code=404, detail="Flowchart not found")

@router.get("/{meeting_id}/status", summary="Get flowchart status for meeting", tags=["flowchart"])
async def get_flowchart_status(meeting_id: str):
    """
    Check if flowchart exists for a meeting
    
    - **meeting_id**: ID of the meeting to check
    - **returns**: Status information about the flowchart
    """
    from pathlib import Path
    import json
    
    flowchart_path = Path(f"storage/outputs/{meeting_id}_flowchart.json")
    
    if flowchart_path.exists():
        try:
            with open(flowchart_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            return {
                "meeting_id": meeting_id,
                "status": "exists",
                "format_type": data.get("format_type"),
                "created_at": data.get("created_at"),
                "project_id": data.get("project_id")
            }
        except Exception as e:
            logger.error(f"Error reading flowchart status for meeting_id {meeting_id}: {str(e)}")
            return {
                "meeting_id": meeting_id,
                "status": "exists",
                "error": "Could not read metadata"
            }
    else:
        return {
            "meeting_id": meeting_id,
            "status": "not_found"
        }