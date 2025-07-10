from fastapi import APIRouter, HTTPException
from models.transcribe import TranscriptionRequest, TranscriptionResponse
from pathlib import Path
import json
from agents.transcription_agent import transcribe_audio_file

router = APIRouter()

@router.post("/transcribe", response_model=TranscriptionResponse, summary="Transcribe audio file", tags=["transcribe"])
async def transcribe_audio(request: TranscriptionRequest):
    """
    Transcribe an uploaded audio file
    
    - **request**: Transcription request with file_id
    - **returns**: Transcription response with transcript data
    """
    try:
        # Check if file exists
        file_path = Path(f"storage/audio/{request.file_id}")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # TODO: Implement actual transcription logic
        # This is a placeholder for the transcription service
        
        # Create transcripts directory
        transcripts_dir = Path("storage/transcripts")
        transcripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Save transcription result
        transcript_path = transcripts_dir / f"{request.file_id}.json"
        transcript_data = {
            "file_id": request.file_id,
            "transcript": "This is a placeholder transcript. Implement actual transcription logic.",
            "confidence": 0.95,
            "language": "en",
            "duration": 120.5
        }
        
        with open(transcript_path, "w") as f:
            json.dump(transcript_data, f)
        
        return TranscriptionResponse(
            success=True,
            file_id=request.file_id,
            transcript=transcript_data["transcript"],
            confidence=transcript_data["confidence"],
            language=transcript_data["language"],
            duration=transcript_data["duration"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.get("/transcribe/status/{file_id}", summary="Get transcription status", tags=["transcribe"])
async def get_transcription_status(file_id: str):
    """
    Get the status of a transcription job
    
    - **file_id**: ID of the file to check status for
    - **returns**: Transcription status information
    """
    transcript_path = Path(f"storage/transcripts/{file_id}.json")
    if transcript_path.exists():
        with open(transcript_path, "r") as f:
            data = json.load(f)
        return {"status": "completed", "file_id": file_id, "data": data}
    else:
        return {"status": "pending", "file_id": file_id}

@router.post("/transcribe/meeting", summary="Transcribe meeting using OpenAI Whisper", tags=["transcribe"])
async def transcribe_meeting(request: dict):
    """
    Transcribe a meeting audio file using OpenAI Whisper API
    
    - **request**: Dictionary containing meeting_id
    - **returns**: Transcript data from OpenAI Whisper
    """
    try:
        meeting_id = request.get("meeting_id")
        if not meeting_id:
            raise HTTPException(status_code=400, detail="meeting_id is required")
        
        # Call the transcription agent
        transcript_path = transcribe_audio_file(meeting_id)
        
        # Load and return the transcript data
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_data = json.load(f)
        
        return transcript_data
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")