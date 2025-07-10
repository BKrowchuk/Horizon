from pydantic import BaseModel
from typing import Dict, Optional

class ActionRequest(BaseModel):
    """Request model for action creation"""
    action_type: str
    file_id: str
    parameters: Optional[Dict] = {}

class ActionResponse(BaseModel):
    """Response model for action creation"""
    success: bool
    action_id: str
    action_type: str
    status: str
    message: str

class ActionStatus(BaseModel):
    """Model for action status update"""
    status: str 