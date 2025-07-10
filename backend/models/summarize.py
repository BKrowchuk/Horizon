from pydantic import BaseModel
from typing import List, Optional

class SummarizeRequest(BaseModel):
    """Request model for summarization"""
    file_id: str
    max_length: Optional[int] = 150
    style: Optional[str] = "concise"

class SummarizeResponse(BaseModel):
    """Response model for summarization"""
    success: bool
    file_id: str
    summary: str
    key_points: List[str]
    word_count: int
    summary_length: int 