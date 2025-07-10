from fastapi import APIRouter, HTTPException
from models.summarize import SummarizeRequest, SummarizeResponse
from pathlib import Path
import json

router = APIRouter()

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """
    Summarize transcribed text
    """
    try:
        # Check if transcript exists
        transcript_path = Path(f"storage/transcripts/{request.file_id}.json")
        if not transcript_path.exists():
            raise HTTPException(status_code=404, detail="Transcript not found")
        
        # Load transcript
        with open(transcript_path, "r") as f:
            transcript_data = json.load(f)
        
        # TODO: Implement actual summarization logic
        # This is a placeholder for the summarization service
        
        # Create outputs directory
        outputs_dir = Path("storage/outputs")
        outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Save summary result
        summary_path = outputs_dir / f"{request.file_id}_summary.json"
        summary_data = {
            "file_id": request.file_id,
            "summary": "This is a placeholder summary. Implement actual summarization logic.",
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "word_count": len(transcript_data["transcript"].split()),
            "summary_length": 150
        }
        
        with open(summary_path, "w") as f:
            json.dump(summary_data, f)
        
        return SummarizeResponse(
            success=True,
            file_id=request.file_id,
            summary=summary_data["summary"],
            key_points=summary_data["key_points"],
            word_count=summary_data["word_count"],
            summary_length=summary_data["summary_length"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@router.get("/summarize/{file_id}")
async def get_summary(file_id: str):
    """
    Get the summary for a specific file
    """
    summary_path = Path(f"storage/outputs/{file_id}_summary.json")
    if summary_path.exists():
        with open(summary_path, "r") as f:
            data = json.load(f)
        return data
    else:
        raise HTTPException(status_code=404, detail="Summary not found") 