from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
import shutil
import uuid
from pathlib import Path
import logging
from agents.transcription_agent import transcribe_audio_file
from agents.summary_agent import generate_summary
from agents.embedding_agent import embed_transcript
from agents.insights_agent import generate_insights

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class PipelineResponse(BaseModel):
    """Response model for pipeline processing"""
    meeting_id: str
    filename: str
    status: str
    steps_completed: list
    transcript: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    embedding: Optional[Dict[str, Any]] = None
    insights: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class PipelineStatusResponse(BaseModel):
    """Response model for pipeline status check"""
    meeting_id: str
    status: str
    steps_completed: list
    progress: Dict[str, Any]
    error: Optional[str] = None

@router.post("/pipeline/process", response_model=PipelineResponse, summary="Process audio file through entire pipeline", tags=["pipeline"])
async def process_audio_pipeline(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    Process an audio file through the entire pipeline:
    1. Upload and store the file
    2. Transcribe the audio
    3. Generate summary
    4. Create embeddings
    
    - **file**: Audio file to process (mp3, wav, m4a, flac, ogg, aac)
    - **returns**: Pipeline response with meeting ID and processing status
    """
    try:
        # Validate file type
        is_audio_content = file.content_type and file.content_type.startswith('audio/')
        is_audio_extension = file.filename and file.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.mp4', '.mpeg', '.mpga', '.oga', '.webm'))
        
        if not (is_audio_content or is_audio_extension):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Generate meeting ID
        meeting_id = str(uuid.uuid4())
        
        # Get file extension - preserve original extension if valid
        original_filename = file.filename or "audio"
        file_extension = Path(original_filename).suffix.lower()
        supported_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.mp4', '.mpeg', '.mpga', '.oga', '.webm']
        print(f"[DEBUG] Incoming filename: {original_filename}")
        print(f"[DEBUG] Detected extension: {file_extension}")
        # Only default to mp3 if extension is missing or unsupported
        if not file_extension or file_extension not in supported_extensions:
            print(f"[DEBUG] Extension not supported or missing, defaulting to .mp3")
            file_extension = '.mp3'  # Default to mp3 if no valid extension
        # Create filename with meeting ID prefix
        filename = f"{meeting_id}_audio{file_extension}"
        print(f"[DEBUG] Final saved filename: {filename}")
        
        # Create storage directory if it doesn't exist
        storage_dir = Path("storage/audio")
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = storage_dir / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Start background processing
        if background_tasks:
            background_tasks.add_task(run_pipeline_steps, meeting_id)
            return PipelineResponse(
                meeting_id=meeting_id,
                filename=filename,
                status="processing",
                steps_completed=["upload"]
            )
        else:
            # Run pipeline synchronously
            return await run_pipeline_steps_sync(meeting_id, filename)
    
    except Exception as e:
        logger.error(f"Pipeline processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {str(e)}")

async def run_pipeline_steps_sync(meeting_id: str, filename: str) -> PipelineResponse:
    """Run pipeline steps synchronously"""
    steps_completed = ["upload"]
    transcript_data = None
    summary_data = None
    embedding_data = None
    insights_data = None
    error = None
    try:
        # Step 1: Transcribe
        logger.info(f"Starting transcription for meeting_id: {meeting_id}")
        transcript_data = transcribe_audio_file(meeting_id)
        steps_completed.append("transcribe")
        logger.info(f"Transcription completed for meeting_id: {meeting_id}")
        
        # Step 2: Generate summary
        logger.info(f"Starting summary generation for meeting_id: {meeting_id}")
        summary_data = generate_summary(meeting_id)
        steps_completed.append("summarize")
        logger.info(f"Summary generation completed for meeting_id: {meeting_id}")
        
        # Step 3: Create embeddings
        logger.info(f"Starting embedding for meeting_id: {meeting_id}")
        embedding_data = embed_transcript(meeting_id)
        steps_completed.append("embed")
        logger.info(f"Embedding completed for meeting_id: {meeting_id}")
        
        # Step 4: Generate insights
        logger.info(f"Starting insights generation for meeting_id: {meeting_id}")
        audio_file_path = Path(f"storage/audio/{meeting_id}_audio.mp3")
        if not audio_file_path.exists():
            audio_file_path = Path(f"storage/audio/{meeting_id}_audio.m4a")
        if audio_file_path.exists():
            insights_data = generate_insights(meeting_id, str(audio_file_path))
        else:
            insights_data = generate_insights(meeting_id)
        steps_completed.append("insights")
        logger.info(f"Insights generation completed for meeting_id: {meeting_id}")
        
        return PipelineResponse(
            meeting_id=meeting_id,
            filename=filename,
            status="completed",
            steps_completed=steps_completed,
            transcript=transcript_data,
            summary=summary_data,
            embedding=embedding_data,
            insights=insights_data
        )
        
    except Exception as e:
        logger.error(f"Pipeline step failed for meeting_id {meeting_id}: {str(e)}")
        return PipelineResponse(
            meeting_id=meeting_id,
            filename=filename,
            status="failed",
            steps_completed=steps_completed,
            error=str(e)
        )

def run_pipeline_steps(meeting_id: str):
    """Run pipeline steps in background"""
    try:
        # Step 1: Transcribe
        logger.info(f"Starting transcription for meeting_id: {meeting_id}")
        transcribe_audio_file(meeting_id)
        logger.info(f"Transcription completed for meeting_id: {meeting_id}")
        
        # Step 2: Generate summary
        logger.info(f"Starting summary generation for meeting_id: {meeting_id}")
        generate_summary(meeting_id)
        logger.info(f"Summary generation completed for meeting_id: {meeting_id}")
        
        # Step 3: Create embeddings
        logger.info(f"Starting embedding for meeting_id: {meeting_id}")
        embed_transcript(meeting_id)
        logger.info(f"Embedding completed for meeting_id: {meeting_id}")
        
        # Step 4: Generate insights
        logger.info(f"Starting insights generation for meeting_id: {meeting_id}")
        audio_file_path = Path(f"storage/audio/{meeting_id}_audio.mp3")
        if not audio_file_path.exists():
            audio_file_path = Path(f"storage/audio/{meeting_id}_audio.m4a")
        if audio_file_path.exists():
            generate_insights(meeting_id, str(audio_file_path))
        else:
            generate_insights(meeting_id)
        logger.info(f"Insights generation completed for meeting_id: {meeting_id}")
        
        logger.info(f"Pipeline completed successfully for meeting_id: {meeting_id}")
        
    except Exception as e:
        logger.error(f"Pipeline step failed for meeting_id {meeting_id}: {str(e)}")

@router.get("/pipeline/status/{meeting_id}", response_model=PipelineStatusResponse, summary="Get pipeline processing status", tags=["pipeline"])
async def get_pipeline_status(meeting_id: str):
    """
    Get the status of pipeline processing for a meeting
    
    - **meeting_id**: ID of the meeting to check
    - **returns**: Pipeline status with completed steps and progress
    """
    try:
        steps_completed = []
        progress = {}
        
        # Check if audio file exists
        audio_path = Path(f"storage/audio/{meeting_id}_audio.mp3")
        if audio_path.exists():
            steps_completed.append("upload")
            progress["upload"] = {"status": "completed"}
        
        # Check if transcript exists
        transcript_path = Path(f"storage/transcripts/{meeting_id}.json")
        if transcript_path.exists():
            steps_completed.append("transcribe")
            progress["transcribe"] = {"status": "completed"}
            try:
                import json
                with open(transcript_path, "r", encoding="utf-8") as f:
                    transcript_data = json.load(f)
                progress["transcribe"]["data"] = {
                    "created_at": transcript_data.get("created_at"),
                    "transcript_length": len(transcript_data.get("transcript", ""))
                }
            except Exception as e:
                logger.error(f"Error reading transcript data: {str(e)}")
        
        # Check if summary exists
        summary_path = Path(f"storage/outputs/{meeting_id}_summary.json")
        if summary_path.exists():
            steps_completed.append("summarize")
            progress["summarize"] = {"status": "completed"}
            try:
                import json
                with open(summary_path, "r", encoding="utf-8") as f:
                    summary_data = json.load(f)
                progress["summarize"]["data"] = {
                    "created_at": summary_data.get("created_at"),
                    "summary_length": len(summary_data.get("summary", ""))
                }
            except Exception as e:
                logger.error(f"Error reading summary data: {str(e)}")
        
        # Check if embeddings exist
        vector_index_path = Path(f"storage/vectors/{meeting_id}.index")
        meta_file_path = Path(f"storage/vectors/{meeting_id}_meta.json")
        if vector_index_path.exists() and meta_file_path.exists():
            steps_completed.append("embed")
            progress["embed"] = {"status": "completed"}
            try:
                import json
                with open(meta_file_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                progress["embed"]["data"] = {
                    "num_chunks": metadata.get("num_chunks", 0),
                    "embedding_model": metadata.get("embedding_model", "unknown")
                }
            except Exception as e:
                logger.error(f"Error reading embedding data: {str(e)}")
        
        # Determine overall status
        if len(steps_completed) == 4:
            status = "completed"
        elif len(steps_completed) > 0:
            status = "in_progress"
        else:
            status = "not_started"
        
        return PipelineStatusResponse(
            meeting_id=meeting_id,
            status=status,
            steps_completed=steps_completed,
            progress=progress
        )
        
    except Exception as e:
        logger.error(f"Error checking pipeline status for meeting_id {meeting_id}: {str(e)}")
        return PipelineStatusResponse(
            meeting_id=meeting_id,
            status="error",
            steps_completed=[],
            progress={},
            error=str(e)
        )

@router.post("/pipeline/process-sync", response_model=PipelineResponse, summary="Process audio file through entire pipeline synchronously", tags=["pipeline"])
async def process_audio_pipeline_sync(file: UploadFile = File(...)):
    """
    Process an audio file through the entire pipeline synchronously:
    1. Upload and store the file
    2. Transcribe the audio
    3. Generate summary
    4. Create embeddings
    
    This endpoint runs all steps synchronously and returns the complete results.
    
    - **file**: Audio file to process (mp3, wav, m4a, flac, ogg, aac)
    - **returns**: Complete pipeline response with all results
    """
    try:
        # Validate file type
        is_audio_content = file.content_type and file.content_type.startswith('audio/')
        is_audio_extension = file.filename and file.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.mp4', '.mpeg', '.mpga', '.oga', '.webm'))
        
        if not (is_audio_content or is_audio_extension):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Generate meeting ID
        meeting_id = str(uuid.uuid4())
        
        # Get file extension - preserve original extension if valid
        original_filename = file.filename or "audio"
        file_extension = Path(original_filename).suffix.lower()
        supported_extensions = ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac', '.mp4', '.mpeg', '.mpga', '.oga', '.webm']
        print(f"[DEBUG] Incoming filename: {original_filename}")
        print(f"[DEBUG] Detected extension: {file_extension}")
        # Only default to mp3 if extension is missing or unsupported
        if not file_extension or file_extension not in supported_extensions:
            print(f"[DEBUG] Extension not supported or missing, defaulting to .mp3")
            file_extension = '.mp3'  # Default to mp3 if no valid extension
        # Create filename with meeting ID prefix
        filename = f"{meeting_id}_audio{file_extension}"
        print(f"[DEBUG] Final saved filename: {filename}")
        
        # Create storage directory if it doesn't exist
        storage_dir = Path("storage/audio")
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = storage_dir / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Run pipeline synchronously
        return await run_pipeline_steps_sync(meeting_id, filename)
    
    except Exception as e:
        logger.error(f"Pipeline processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {str(e)}") 