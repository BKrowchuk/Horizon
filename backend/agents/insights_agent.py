import openai
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_insights(meeting_id: str, audio_file_path: str = None) -> Dict[str, Any]:
    """
    Generate insights from a meeting transcript and audio recording using OpenAI's APIs
    
    Args:
        meeting_id (str): The meeting ID to analyze
        audio_file_path (str, optional): Path to the audio file for timestamp analysis
        
    Returns:
        Dict[str, Any]: Insights data with meeting_id, project_id, created_at, insights, and important_moments
    """
    # Construct file paths - use absolute path from backend directory
    backend_dir = Path(__file__).parent.parent
    transcript_file_path = backend_dir / f"storage/transcripts/{meeting_id}.json"
    insights_file_path = backend_dir / f"storage/outputs/{meeting_id}_insights.json"
    
    # Check if transcript file exists
    if not transcript_file_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_file_path}")
    
    # Create outputs directory if it doesn't exist
    insights_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info(f"Starting insights generation for meeting_id: {meeting_id}")
        
        # Load transcript data
        with open(transcript_file_path, "r", encoding="utf-8") as f:
            transcript_data = json.load(f)
        
        # Extract transcript text and metadata
        transcript_text = transcript_data.get("transcript", "")
        project_id = transcript_data.get("project_id", "unknown")
        
        if not transcript_text:
            raise ValueError("Transcript text is empty")
        
        # Get timestamped transcript if audio file is provided
        timestamped_segments = []
        if audio_file_path and Path(audio_file_path).exists():
            logger.info(f"Analyzing audio file for timestamps: {audio_file_path}")
            timestamped_segments = get_timestamped_transcript(audio_file_path)
        
        # Prepare context for insights analysis
        analysis_context = transcript_text
        if timestamped_segments:
            analysis_context += f"\n\nTimestamped segments:\n{format_timestamped_segments(timestamped_segments)}"
        
        # Call OpenAI's Chat Completion API for insights
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Can be changed to gpt-4 if available
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at identifying key insights from meeting transcripts and audio recordings. Analyze this transcript and extract: 1) Important moments (with timestamps if available), 2) Recurring patterns or themes, 3) Potential risks or opportunities mentioned, 4) Emotional tone or sentiment shifts. Format as bullet points under each category. For important moments, include timestamps when available."
                },
                {
                    "role": "user",
                    "content": analysis_context
                }
            ],
            temperature=0.4,
            max_tokens=1000
        )
        
        # Extract the generated insights
        insights_text = response.choices[0].message.content.strip()
        
        # Extract important moments with timestamps if available
        important_moments = extract_important_moments(insights_text, timestamped_segments)
        
        # Prepare insights data
        insights_data = {
            "meeting_id": meeting_id,
            "project_id": project_id,
            "created_at": datetime.utcnow().isoformat(),
            "insights": insights_text,
            "important_moments": important_moments
        }
        
        # Save insights to file
        with open(insights_file_path, "w", encoding="utf-8") as f:
            json.dump(insights_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Insights generation completed successfully for meeting_id: {meeting_id}")
        return insights_data
        
    except openai.APIError as e:
        logger.error(f"OpenAI API error for meeting_id {meeting_id}: {str(e)}")
        raise Exception(f"OpenAI API call failed: {str(e)}")
    except Exception as e:
        logger.error(f"Insights generation failed for meeting_id {meeting_id}: {str(e)}")
        raise Exception(f"Insights generation failed: {str(e)}")

def get_timestamped_transcript(audio_file_path: str) -> List[Any]:
    """
    Get timestamped transcript segments from audio file using OpenAI Whisper API
    
    Args:
        audio_file_path (str): Path to the audio file
        
    Returns:
        List[Any]: List of transcript segments (TranscriptionSegment objects) with timestamps
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript_response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                language="en",
                temperature=0.0,
                prompt="This is a meeting recording. Transcribe accurately with timestamps."
            )
        
        return transcript_response.segments
    except Exception as e:
        logger.error(f"Failed to get timestamped transcript: {str(e)}")
        return []

def format_timestamped_segments(segments: List[Any]) -> str:
    """
    Format timestamped segments for analysis
    
    Args:
        segments (List[Any]): List of transcript segments (TranscriptionSegment objects)
        
    Returns:
        str: Formatted timestamped segments
    """
    formatted_segments = []
    for segment in segments:
        start_time = format_timestamp(getattr(segment, "start", 0))
        end_time = format_timestamp(getattr(segment, "end", 0))
        text = getattr(segment, "text", "").strip()
        if text:
            formatted_segments.append(f"[{start_time}-{end_time}] {text}")
    
    return "\n".join(formatted_segments)

def format_timestamp(seconds: float) -> str:
    """
    Format seconds to MM:SS format
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted timestamp
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def extract_important_moments(insights_text: str, timestamped_segments: List[Any]) -> List[Dict[str, Any]]:
    """
    Extract important moments with timestamps from insights text
    
    Args:
        insights_text (str): Generated insights text
        timestamped_segments (List[Any]): Timestamped transcript segments (TranscriptionSegment objects)
        
    Returns:
        List[Dict[str, Any]]: List of important moments with timestamps
    """
    important_moments = []
    
    # Simple extraction - look for timestamp patterns in insights text
    import re
    timestamp_pattern = r'\[(\d{2}:\d{2})-(\d{2}:\d{2})\]'
    matches = re.findall(timestamp_pattern, insights_text)
    
    for start_time, end_time in matches:
        # Find corresponding segment text
        segment_text = ""
        for segment in timestamped_segments:
            seg_start = format_timestamp(getattr(segment, "start", 0))
            seg_end = format_timestamp(getattr(segment, "end", 0))
            if seg_start == start_time and seg_end == end_time:
                segment_text = getattr(segment, "text", "").strip()
                break
        
        important_moments.append({
            "start_time": start_time,
            "end_time": end_time,
            "text": segment_text,
            "description": "Important moment identified in analysis"
        })
    
    return important_moments 