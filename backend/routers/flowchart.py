from fastapi import APIRouter, HTTPException
from models.flowchart import FlowchartRequest, FlowchartResponse
from pathlib import Path
import json

router = APIRouter()

@router.post("/flowchart", response_model=FlowchartResponse, summary="Generate flowchart from content", tags=["flowchart"])
async def generate_flowchart(request: FlowchartRequest):
    """
    Generate a flowchart from content
    
    - **request**: Flowchart request with file_id and flowchart type
    - **returns**: Flowchart response with nodes, edges, and visualization data
    """
    try:
        # Check if transcript exists
        transcript_path = Path(f"storage/transcripts/{request.file_id}.json")
        if not transcript_path.exists():
            raise HTTPException(status_code=404, detail="Transcript not found")
        
        # Load transcript
        with open(transcript_path, "r") as f:
            transcript_data = json.load(f)
        
        # TODO: Implement actual flowchart generation logic
        # This is a placeholder for the flowchart service
        
        # Create outputs directory
        outputs_dir = Path("storage/outputs")
        outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Save flowchart result
        flowchart_path = outputs_dir / f"{request.file_id}_flowchart.json"
        flowchart_data = {
            "file_id": request.file_id,
            "flowchart_type": request.flowchart_type,
            "nodes": [
                {"id": "1", "label": "Start", "type": "start"},
                {"id": "2", "label": "Process", "type": "process"},
                {"id": "3", "label": "Decision", "type": "decision"},
                {"id": "4", "label": "End", "type": "end"}
            ],
            "edges": [
                {"from": "1", "to": "2", "label": "Next"},
                {"from": "2", "to": "3", "label": "Check"},
                {"from": "3", "to": "4", "label": "Complete"}
            ],
            "svg_data": "<svg>...</svg>",
            "png_url": f"/api/v1/flowchart/{request.file_id}/image"
        }
        
        with open(flowchart_path, "w") as f:
            json.dump(flowchart_data, f)
        
        return FlowchartResponse(
            success=True,
            file_id=request.file_id,
            flowchart_type=flowchart_data["flowchart_type"],
            nodes=flowchart_data["nodes"],
            edges=flowchart_data["edges"],
            svg_data=flowchart_data["svg_data"],
            png_url=flowchart_data["png_url"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flowchart generation failed: {str(e)}")

@router.get("/flowchart/{file_id}", summary="Get flowchart for file", tags=["flowchart"])
async def get_flowchart(file_id: str):
    """
    Get flowchart for a specific file
    
    - **file_id**: ID of the file to get flowchart for
    - **returns**: Flowchart data for the file
    """
    flowchart_path = Path(f"storage/outputs/{file_id}_flowchart.json")
    if flowchart_path.exists():
        with open(flowchart_path, "r") as f:
            data = json.load(f)
        return data
    else:
        raise HTTPException(status_code=404, detail="Flowchart not found")

@router.get("/flowchart/{file_id}/image", summary="Get flowchart as image", tags=["flowchart"])
async def get_flowchart_image(file_id: str):
    """
    Get flowchart as image
    
    - **file_id**: ID of the file to get flowchart image for
    - **returns**: Flowchart image data
    """
    # TODO: Implement image generation and serving
    # This is a placeholder
    return {"message": "Image generation not implemented yet"}