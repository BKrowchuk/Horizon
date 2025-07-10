from pydantic import BaseModel
from typing import List, Dict, Optional

class InsightsRequest(BaseModel):
    """Request model for insights generation"""
    file_id: str
    analysis_types: Optional[List[str]] = ["sentiment", "topics", "entities"]

class InsightsResponse(BaseModel):
    """Response model for insights generation"""
    success: bool
    file_id: str
    sentiment: str
    topics: List[str]
    entities: List[str]
    key_phrases: List[str]
    confidence_scores: Dict[str, float] 