import openai
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_summary(meeting_id: str) -> Dict[str, Any]:
    """
    Generate a summary of a meeting transcript using OpenAI's Chat Completion API
    
    Args:
        meeting_id (str): The meeting ID to summarize
        
    Returns:
        Dict[str, Any]: Summary data with meeting_id, project_id, created_at, and summary
    """
    # Construct file paths - use absolute path from backend directory
    backend_dir = Path(__file__).parent.parent
    transcript_file_path = backend_dir / f"storage/transcripts/{meeting_id}.json"
    summary_file_path = backend_dir / f"storage/outputs/{meeting_id}_summary.json"
    
    # Check if transcript file exists
    if not transcript_file_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_file_path}")
    
    # Create outputs directory if it doesn't exist
    summary_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info(f"Starting summary generation for meeting_id: {meeting_id}")
        
        # Load transcript data
        with open(transcript_file_path, "r", encoding="utf-8") as f:
            transcript_data = json.load(f)
        
        # Extract transcript text and metadata
        transcript_text = transcript_data.get("transcript", "")
        project_id = transcript_data.get("project_id", "unknown")
        
        if not transcript_text:
            raise ValueError("Transcript text is empty")
        
        # Call OpenAI's Chat Completion API
        response = openai.chat.completions.create(
            model="gpt-4",  # Can be changed to gpt-3.5-turbo if needed
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional meeting summarizer. Create a concise but comprehensive summary of the following meeting transcript. Focus on key discussion points, decisions made, and the overall narrative flow."
                },
                {
                    "role": "user",
                    "content": transcript_text
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Extract the generated summary
        summary_text = response.choices[0].message.content.strip()
        
        # Prepare summary data
        summary_data = {
            "meeting_id": meeting_id,
            "project_id": project_id,
            "created_at": datetime.utcnow().isoformat(),
            "summary": summary_text
        }
        
        # Save summary to file
        with open(summary_file_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Summary generation completed successfully for meeting_id: {meeting_id}")
        return summary_data
        
    except Exception as e:
        logger.error(f"Summary generation failed for meeting_id {meeting_id}: {str(e)}")
        raise Exception(f"Summary generation failed: {str(e)}") 