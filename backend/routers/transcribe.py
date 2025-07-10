from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from agents.transcription_agent import transcribe_audio_file

router = APIRouter()

class TranscriptionRequest(BaseModel):
    """Request model for transcription"""
    meeting_id: str

@router.post("/transcribe", summary="Transcribe audio file using OpenAI Whisper", tags=["transcribe"])
async def transcribe_audio(request: TranscriptionRequest) -> Dict[str, Any]:
    """
    Transcribe an audio file using OpenAI Whisper API
    
    - **request**: Transcription request with meeting_id
    - **returns**: Transcript data with meeting_id, project_id, created_at, and transcript
    """
    try:
        # Call the transcription agent
        transcript_data = transcribe_audio_file(request.meeting_id)
        
        return transcript_data
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")