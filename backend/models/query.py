from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    """Request model for content querying"""
    file_id: str
    query_text: str
    query_type: Optional[str] = "general"

class QueryResponse(BaseModel):
    """Response model for content querying"""
    success: bool
    file_id: str
    query_type: str
    query_text: str
    result: str
    confidence: float
    sources: List[str] 