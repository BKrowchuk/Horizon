from fastapi import APIRouter, HTTPException
from models.actions import ActionRequest, ActionResponse, ActionStatus
from pathlib import Path
import json
from datetime import datetime

router = APIRouter()

@router.post("/actions", response_model=ActionResponse)
async def create_action(request: ActionRequest):
    """
    Create a new action/task
    """
    try:
        # Create actions directory
        actions_dir = Path("storage/outputs")
        actions_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate action ID
        action_id = f"action_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save action data
        action_path = actions_dir / f"{action_id}.json"
        action_data = {
            "action_id": action_id,
            "action_type": request.action_type,
            "file_id": request.file_id,
            "parameters": request.parameters,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        with open(action_path, "w") as f:
            json.dump(action_data, f)
        
        return ActionResponse(
            success=True,
            action_id=action_id,
            action_type=request.action_type,
            status="pending",
            message="Action created successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action creation failed: {str(e)}")

@router.get("/actions/{action_id}")
async def get_action(action_id: str):
    """
    Get action details
    """
    action_path = Path(f"storage/outputs/{action_id}.json")
    if action_path.exists():
        with open(action_path, "r") as f:
            data = json.load(f)
        return data
    else:
        raise HTTPException(status_code=404, detail="Action not found")

@router.put("/actions/{action_id}/status")
async def update_action_status(action_id: str, status: ActionStatus):
    """
    Update action status
    """
    try:
        action_path = Path(f"storage/outputs/{action_id}.json")
        if not action_path.exists():
            raise HTTPException(status_code=404, detail="Action not found")
        
        with open(action_path, "r") as f:
            data = json.load(f)
        
        data["status"] = status.status
        data["updated_at"] = datetime.now().isoformat()
        
        with open(action_path, "w") as f:
            json.dump(data, f)
        
        return {"success": True, "action_id": action_id, "status": status.status}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status update failed: {str(e)}")

@router.get("/actions")
async def list_actions():
    """
    List all actions
    """
    try:
        actions_dir = Path("storage/outputs")
        actions = []
        
        if actions_dir.exists():
            for file_path in actions_dir.glob("action_*.json"):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    actions.append(data)
        
        return {"actions": actions}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list actions: {str(e)}") 