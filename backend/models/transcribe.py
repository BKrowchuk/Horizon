from pydantic import BaseModel
from typing import Optional

class TranscriptionRequest(BaseModel):
    """Request model for transcription"""
    file_id: str
    language: Optional[str] = "en"
    model: Optional[str] = "default"

class TranscriptionResponse(BaseModel):
    """Response model for transcription"""
    success: bool
    file_id: str
    transcript: str
    confidence: float
    language: str
    duration: float 