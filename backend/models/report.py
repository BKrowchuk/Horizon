from pydantic import BaseModel
from typing import Dict, List, Optional

class ReportRequest(BaseModel):
    """Request model for report generation"""
    file_id: str
    report_type: str = "comprehensive"
    format: Optional[str] = "json"

class ReportResponse(BaseModel):
    """Response model for report generation"""
    success: bool
    file_id: str
    report_type: str
    generated_at: str
    sections: Dict
    pdf_url: str
    html_url: str 