import openai
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def transcribe_audio_file(meeting_id: str) -> str:
    """
    Transcribe an audio file using OpenAI's Whisper API
    
    Args:
        meeting_id (str): The meeting ID to transcribe
        
    Returns:
        str: Path to the saved transcript file
    """
    # Construct file paths
    audio_file_path = Path(f"storage/audio/{meeting_id}_audio.mp3")
    transcript_file_path = Path(f"storage/transcripts/{meeting_id}.json")
    
    # Check if audio file exists
    if not audio_file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    # Create transcripts directory if it doesn't exist
    transcript_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Transcribe using OpenAI Whisper API
        with open(audio_file_path, "rb") as audio_file:
            transcript_response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        # Prepare transcript data
        transcript_data = {
            "meeting_id": meeting_id,
            "project_id": "demo_project",
            "created_at": datetime.utcnow().isoformat(),
            "transcript": transcript_response
        }
        
        # Save transcript to file
        with open(transcript_file_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)
        
        return str(transcript_file_path)
        
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}") 