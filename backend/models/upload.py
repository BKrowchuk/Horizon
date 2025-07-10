from pydantic import BaseModel
from typing import Optional

class UploadRequest(BaseModel):
    """Request model for file upload"""
    filename: str
    content_type: str

class UploadResponse(BaseModel):
    """Response model for file upload"""
    meeting_id: str
    filename: str 