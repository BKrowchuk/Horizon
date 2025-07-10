from pydantic import BaseModel
from typing import List, Dict, Optional

class FlowchartRequest(BaseModel):
    """Request model for flowchart generation"""
    file_id: str
    flowchart_type: str = "process"
    style: Optional[str] = "default"

class FlowchartResponse(BaseModel):
    """Response model for flowchart generation"""
    success: bool
    file_id: str
    flowchart_type: str
    nodes: List[Dict]
    edges: List[Dict]
    svg_data: str
    png_url: str 