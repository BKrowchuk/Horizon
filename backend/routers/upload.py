from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from models.upload import UploadResponse, UploadRequest
import os
import shutil
import uuid
from pathlib import Path

router = APIRouter()

@router.post("/upload", response_model=UploadResponse, summary="Upload audio file", tags=["upload"])
async def upload_file(file: UploadFile = File(...)):
    """
    Upload an audio file for processing
    
    - **file**: Audio file to upload (mp3, wav, m4a, flac, ogg, aac)
    - **returns**: Upload response with meeting ID and filename
    """
    try:
        # Debug logging
        print(f"Debug - Content type: {file.content_type}")
        print(f"Debug - Filename: {file.filename}")
        
        # Validate file type - check both content_type and file extension
        is_audio_content = file.content_type and file.content_type.startswith('audio/')
        is_audio_extension = file.filename and file.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac'))
        
        print(f"Debug - Is audio content: {is_audio_content}")
        print(f"Debug - Is audio extension: {is_audio_extension}")
        
        if not (is_audio_content or is_audio_extension):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Generate meeting ID
        meeting_id = str(uuid.uuid4())
        
        # Get file extension
        original_filename = file.filename or "audio"
        file_extension = Path(original_filename).suffix.lower()
        if not file_extension or file_extension not in ['.mp3', '.wav']:
            file_extension = '.mp3'  # Default to mp3 if no valid extension
        
        # Create filename with meeting ID prefix and _audio suffix to match transcription agent
        filename = f"{meeting_id}_audio{file_extension}"
        
        # Create storage directory if it doesn't exist
        storage_dir = Path("storage/audio")
        storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = storage_dir / filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return UploadResponse(
            meeting_id=meeting_id,
            filename=filename
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/upload/status/{file_id}", summary="Get upload status", tags=["upload"])
async def get_upload_status(file_id: str):
    """
    Get the status of an uploaded file
    
    - **file_id**: ID of the uploaded file
    - **returns**: Upload status information
    """
    file_path = Path(f"storage/audio/{file_id}")
    if file_path.exists():
        return {"status": "uploaded", "file_id": file_id}
    else:
        raise HTTPException(status_code=404, detail="File not found")