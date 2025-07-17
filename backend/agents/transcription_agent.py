import openai
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
import logging
import tempfile
import shutil

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transcribe_audio_file(meeting_id: str) -> Dict[str, Any]:
    """
    Transcribe an audio file using OpenAI's Whisper API with optimized parameters
    
    Args:
        meeting_id (str): The meeting ID to transcribe
        
    Returns:
        Dict[str, Any]: Transcript data with meeting_id, project_id, created_at, and transcript
    """
    # Construct file paths - try different audio extensions
    audio_dir = Path("storage/audio")
    transcript_file_path = Path(f"storage/transcripts/{meeting_id}.json")
    
    # Look for the audio file with any supported extension
    audio_file_path = None
    supported_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.mp4', '.mpeg', '.mpga', '.oga', '.webm']
    
    for ext in supported_extensions:
        potential_path = audio_dir / f"{meeting_id}_audio{ext}"
        if potential_path.exists():
            audio_file_path = potential_path
            break
    
    # Check if audio file exists
    if not audio_file_path:
        raise FileNotFoundError(f"Audio file not found for meeting_id: {meeting_id}")
    
    # Create transcripts directory if it doesn't exist
    transcript_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info(f"Starting transcription for meeting_id: {meeting_id}")
        
        # Transcribe using OpenAI Whisper API with optimized parameters
        with open(audio_file_path, "rb") as audio_file:
            transcript_response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language="en",  # Specify language to improve accuracy
                temperature=0.0,  # Lower temperature for more consistent output
                prompt="This is a song or music recording. Transcribe the lyrics accurately."
            )
        
        # Clean up the transcript to remove any remaining repetitions
        cleaned_transcript = clean_transcript(transcript_response)
        
        # Prepare transcript data
        transcript_data = {
            "meeting_id": meeting_id,
            "project_id": "demo_project",
            "created_at": datetime.utcnow().isoformat(),
            "transcript": cleaned_transcript,
            "original_length": len(transcript_response),
            "cleaned_length": len(cleaned_transcript),
            "whisper_params": {
                "language": "en",
                "temperature": 0.0,
                "prompt": "This is a song or music recording. Transcribe the lyrics accurately."
            }
        }
        
        # Save transcript to file
        with open(transcript_file_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Transcription completed successfully for meeting_id: {meeting_id}")
        return transcript_data
        
    except Exception as e:
        logger.error(f"Transcription failed for meeting_id {meeting_id}: {str(e)}")
        raise Exception(f"Transcription failed: {str(e)}")

def clean_transcript(transcript: str) -> str:
    """
    Clean the transcript to remove obvious repetitions and improve readability
    
    Args:
        transcript (str): Raw transcript from Whisper API
        
    Returns:
        str: Cleaned transcript
    """
    if not transcript:
        return transcript
    
    # Split into sentences
    sentences = transcript.split('.')
    
    # Remove empty sentences and strip whitespace
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Remove consecutive duplicate sentences
    cleaned_sentences = []
    for i, sentence in enumerate(sentences):
        if i == 0 or sentence != sentences[i-1]:
            cleaned_sentences.append(sentence)
    
    # Join back together
    cleaned_transcript = '. '.join(cleaned_sentences)
    
    # Add final period if missing
    if cleaned_transcript and not cleaned_transcript.endswith('.'):
        cleaned_transcript += '.'
    
    return cleaned_transcript 