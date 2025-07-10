from fastapi import APIRouter, HTTPException
from models.insights import InsightsRequest, InsightsResponse
from pathlib import Path
import json

router = APIRouter()

@router.post("/insights", response_model=InsightsResponse)
async def generate_insights(request: InsightsRequest):
    """
    Generate insights from transcribed content
    """
    try:
        # Check if transcript exists
        transcript_path = Path(f"storage/transcripts/{request.file_id}.json")
        if not transcript_path.exists():
            raise HTTPException(status_code=404, detail="Transcript not found")
        
        # Load transcript
        with open(transcript_path, "r") as f:
            transcript_data = json.load(f)
        
        # TODO: Implement actual insights generation logic
        # This is a placeholder for the insights service
        
        # Create outputs directory
        outputs_dir = Path("storage/outputs")
        outputs_dir.mkdir(parents=True, exist_ok=True)
        
        # Save insights result
        insights_path = outputs_dir / f"{request.file_id}_insights.json"
        insights_data = {
            "file_id": request.file_id,
            "sentiment": "positive",
            "topics": ["technology", "innovation", "business"],
            "entities": ["AI", "machine learning", "startup"],
            "key_phrases": ["artificial intelligence", "digital transformation"],
            "confidence_scores": {
                "sentiment": 0.85,
                "topic_detection": 0.92,
                "entity_recognition": 0.88
            }
        }
        
        with open(insights_path, "w") as f:
            json.dump(insights_data, f)
        
        return InsightsResponse(
            success=True,
            file_id=request.file_id,
            sentiment=insights_data["sentiment"],
            topics=insights_data["topics"],
            entities=insights_data["entities"],
            key_phrases=insights_data["key_phrases"],
            confidence_scores=insights_data["confidence_scores"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

@router.get("/insights/{file_id}")
async def get_insights(file_id: str):
    """
    Get insights for a specific file
    """
    insights_path = Path(f"storage/outputs/{file_id}_insights.json")
    if insights_path.exists():
        with open(insights_path, "r") as f:
            data = json.load(f)
        return data
    else:
        raise HTTPException(status_code=404, detail="Insights not found") 