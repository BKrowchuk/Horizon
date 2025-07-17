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

def generate_flowchart(meeting_id: str, format_type: str = "mermaid") -> Dict[str, Any]:
    """
    Generate a flowchart from meeting transcript
    
    Args:
        meeting_id (str): The meeting ID
        format_type (str): Type of flowchart format ("mermaid" or "interactive")
        
    Returns:
        Dict[str, Any]: Flowchart data with metadata
    """
    # Validate format_type parameter
    if format_type not in ["mermaid", "interactive"]:
        raise ValueError("format_type must be 'mermaid' or 'interactive'")
    
    # Construct file paths using absolute paths
    base_path = Path(__file__).parent.parent
    transcript_file_path = base_path / f"storage/transcripts/{meeting_id}.json"
    output_file_path = base_path / f"storage/outputs/{meeting_id}_flowchart.json"
    
    # Check if transcript file exists
    if not transcript_file_path.exists():
        raise FileNotFoundError(f"Transcript file not found: {transcript_file_path}")
    
    # Create outputs directory if it doesn't exist
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        logger.info(f"Starting flowchart generation for meeting_id: {meeting_id}, format: {format_type}")
        
        # Load transcript data
        with open(transcript_file_path, "r", encoding="utf-8") as f:
            transcript_data = json.load(f)
        
        # Extract transcript text and metadata
        transcript_text = transcript_data.get("transcript", "")
        project_id = transcript_data.get("project_id", "demo_project")
        
        if not transcript_text:
            raise ValueError(f"No transcript text found for meeting_id: {meeting_id}")
        
        # Generate the requested flowchart format
        if format_type == "mermaid":
            flowchart_data = generate_mermaid_flowchart(transcript_text)
            mermaid_data = flowchart_data  # Already in mermaid format
        elif format_type == "interactive":
            flowchart_data = generate_interactive_flowchart(transcript_text)
            # Also generate mermaid version for interactive format
            mermaid_data = generate_mermaid_flowchart(transcript_text)
        else:
            raise ValueError(f"Unsupported format_type: {format_type}")
        
        # Create result structure
        result = {
            "meeting_id": meeting_id,
            "project_id": project_id,
            "created_at": datetime.now().isoformat(),
            "format_type": format_type,
            "flowchart": flowchart_data,
            "mermaid_flowchart": mermaid_data,  # Always include mermaid version
            "render_info": {
                "mermaid_version": "10.x",
                "interactive_library": "D3.js" if format_type == "interactive" else None
            }
        }
        
        # Save flowchart to storage
        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Flowchart generation completed for meeting_id: {meeting_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Flowchart generation failed for meeting_id {meeting_id}: {str(e)}")
        raise Exception(f"Flowchart generation failed: {str(e)}")

def generate_mermaid_flowchart(transcript_text: str) -> str:
    """
    Generate Mermaid.js flowchart from transcript text
    
    Args:
        transcript_text (str): The transcript text
        
    Returns:
        str: Mermaid.js flowchart syntax
    """
    try:
        system_prompt = """You are an expert at creating flowcharts from meeting discussions. Analyze this meeting transcript and create a Mermaid.js flowchart that represents the key discussion flow, decision points, and process steps discussed. Use appropriate flowchart symbols (rectangles for processes, diamonds for decisions, circles for start/end). The output should be valid Mermaid.js syntax that can be rendered directly. Start with 'flowchart TD' for top-down flow. Keep it concise but informative, focusing on the main discussion points and decisions."""

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a Mermaid.js flowchart from this meeting transcript:\n\n{transcript_text}"}
            ],
            temperature=0.3,
            max_tokens=1200
        )
        
        flowchart_code = response.choices[0].message.content.strip()
        
        # Ensure it starts with flowchart TD
        if not flowchart_code.startswith("flowchart TD"):
            flowchart_code = "flowchart TD\n" + flowchart_code
        
        return flowchart_code
        
    except Exception as e:
        logger.error(f"Mermaid flowchart generation failed: {str(e)}")
        raise Exception(f"Mermaid flowchart generation failed: {str(e)}")

def generate_interactive_flowchart(transcript_text: str) -> Dict[str, Any]:
    """
    Generate interactive flowchart JSON structure from transcript text
    
    Args:
        transcript_text (str): The transcript text
        
    Returns:
        Dict[str, Any]: Interactive flowchart structure with nodes and connections
    """
    try:
        system_prompt = """You are an expert at creating interactive flowcharts from meeting discussions. Analyze this meeting transcript and create a JSON structure representing nodes and connections for an interactive flowchart. Each node should have: id, label, type (process/decision/start/end), position (x,y coordinates), and content (detailed description). Each connection should have: from_node, to_node, label (if any). Make it clickable and informative. Return only valid JSON without any markdown formatting."""

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create an interactive flowchart JSON structure from this meeting transcript:\n\n{transcript_text}"}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        flowchart_json = response.choices[0].message.content.strip()
        
        # Parse the JSON response
        try:
            flowchart_data = json.loads(flowchart_json)
        except json.JSONDecodeError:
            # If the response isn't valid JSON, create a basic structure
            logger.warning("Invalid JSON response from OpenAI, creating basic structure")
            flowchart_data = {
                "nodes": [
                    {
                        "id": "1",
                        "label": "Meeting Start",
                        "type": "start",
                        "position": {"x": 100, "y": 50},
                        "content": "Meeting begins"
                    },
                    {
                        "id": "2",
                        "label": "Discussion",
                        "type": "process",
                        "position": {"x": 100, "y": 150},
                        "content": "Key discussion points"
                    },
                    {
                        "id": "3",
                        "label": "Decisions",
                        "type": "decision",
                        "position": {"x": 100, "y": 250},
                        "content": "Decisions made"
                    },
                    {
                        "id": "4",
                        "label": "Meeting End",
                        "type": "end",
                        "position": {"x": 100, "y": 350},
                        "content": "Meeting concludes"
                    }
                ],
                "connections": [
                    {"from_node": "1", "to_node": "2", "label": "Next"},
                    {"from_node": "2", "to_node": "3", "label": "Decide"},
                    {"from_node": "3", "to_node": "4", "label": "Complete"}
                ]
            }
        
        return flowchart_data
        
    except Exception as e:
        logger.error(f"Interactive flowchart generation failed: {str(e)}")
        raise Exception(f"Interactive flowchart generation failed: {str(e)}") 