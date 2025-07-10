#!/usr/bin/env python3
"""
Test Pipeline Script for StubbesScript

This script tests the entire audio processing pipeline:
1. Upload audio file
2. Transcribe audio file
3. Vectorize transcript

Usage:
    python test_pipeline.py --audio_file path/to/audio.mp3
    python test_pipeline.py --audio_file path/to/audio.mp3 --base_url http://localhost:8000
"""

import requests
import json
import os
import time
import argparse
from pathlib import Path
from typing import Dict, Any, Optional


def print_step(step: str, description: str = ""):
    """Print a formatted step header"""
    print(f"\n{'='*60}")
    print(f"STEP: {step}")
    if description:
        print(f"Description: {description}")
    print(f"{'='*60}")


def print_success(message: str):
    """Print a success message"""
    print(f"✅ {message}")


def print_error(message: str):
    """Print an error message"""
    print(f"❌ {message}")


def print_info(message: str):
    """Print an info message"""
    print(f"ℹ️  {message}")


def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists and print status"""
    if os.path.exists(file_path):
        print_success(f"{description}: {file_path}")
        return True
    else:
        print_error(f"{description}: {file_path} (NOT FOUND)")
        return False


def print_file_content(file_path: str, max_lines: int = 10):
    """Print the content of a file (first few lines)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"\n📄 File content ({file_path}):")
            print("-" * 40)
            for i, line in enumerate(lines[:max_lines]):
                print(f"{i+1:2d}: {line.rstrip()}")
            if len(lines) > max_lines:
                print(f"... and {len(lines) - max_lines} more lines")
            print("-" * 40)
    except Exception as e:
        print_error(f"Could not read file {file_path}: {e}")


def upload_audio_file(base_url: str, audio_file_path: str) -> Optional[Dict[str, Any]]:
    """Upload audio file to the API"""
    print_step("1. UPLOAD AUDIO FILE", f"Uploading {audio_file_path}")
    
    if not os.path.exists(audio_file_path):
        print_error(f"Audio file not found: {audio_file_path}")
        return None
    
    try:
        # Prepare the file for upload
        with open(audio_file_path, 'rb') as f:
            files = {'file': (os.path.basename(audio_file_path), f, 'audio/mpeg')}
            
            print_info(f"Uploading to: {base_url}/api/v1/upload")
            response = requests.post(f"{base_url}/api/v1/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Upload successful!")
            print_info(f"Meeting ID: {result.get('meeting_id')}")
            print_info(f"Filename: {result.get('filename')}")
            return result
        else:
            print_error(f"Upload failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to {base_url}. Is the server running?")
        return None
    except Exception as e:
        print_error(f"Upload error: {e}")
        return None


def transcribe_audio(base_url: str, meeting_id: str) -> Optional[Dict[str, Any]]:
    """Transcribe the uploaded audio file"""
    print_step("2. TRANSCRIBE AUDIO", f"Transcribing meeting ID: {meeting_id}")
    
    try:
        payload = {"meeting_id": meeting_id}
        print_info(f"Transcribing via: {base_url}/api/v1/transcribe")
        
        response = requests.post(f"{base_url}/api/v1/transcribe", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print_success("Transcription successful!")
            print_info(f"Project ID: {result.get('project_id')}")
            print_info(f"Created at: {result.get('created_at')}")
            print_info(f"Transcript length: {len(result.get('transcript', ''))} characters")
            return result
        else:
            print_error(f"Transcription failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to {base_url}")
        return None
    except Exception as e:
        print_error(f"Transcription error: {e}")
        return None


def vectorize_transcript(base_url: str, meeting_id: str) -> Optional[Dict[str, Any]]:
    """Vectorize the transcribed text"""
    print_step("3. VECTORIZE TRANSCRIPT", f"Vectorizing meeting ID: {meeting_id}")
    
    try:
        payload = {"meeting_id": meeting_id}
        print_info(f"Vectorizing via: {base_url}/api/v1/vectorize")
        
        response = requests.post(f"{base_url}/api/v1/vectorize", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print_success("Vectorization successful!")
            print_info(f"Number of chunks: {result.get('num_chunks')}")
            print_info(f"Status: {result.get('status')}")
            return result
        else:
            print_error(f"Vectorization failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print_error(f"Could not connect to {base_url}")
        return None
    except Exception as e:
        print_error(f"Vectorization error: {e}")
        return None


def verify_storage_files(meeting_id: str):
    """Verify that expected files exist in storage directories"""
    print_step("4. VERIFY STORAGE FILES", f"Checking files for meeting ID: {meeting_id}")
    
    # Define expected file paths
    expected_files = [
        (f"backend/storage/audio/{meeting_id}_audio.mp3", "Audio file"),
        (f"backend/storage/transcripts/{meeting_id}.json", "Transcript file"),
        (f"backend/storage/vectors/{meeting_id}_meta.json", "Vector file"),
        (f"backend/storage/outputs/{meeting_id}.json", "Output file")
    ]
    
    all_files_exist = True
    for file_path, description in expected_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    if all_files_exist:
        print_success("All expected files found!")
    else:
        print_error("Some expected files are missing")
    
    return all_files_exist


def print_key_file_contents(meeting_id: str):
    """Print the content of key files"""
    print_step("5. FILE CONTENTS", f"Displaying key file contents for meeting ID: {meeting_id}")
    
    key_files = [
        (f"backend/storage/transcripts/{meeting_id}.json", "Transcript"),
        (f"backend/storage/vectors/{meeting_id}_meta.json", "Vectors"),
        (f"backend/storage/outputs/{meeting_id}.json", "Output")
    ]
    
    for file_path, description in key_files:
        if os.path.exists(file_path):
            print_file_content(file_path)
        else:
            print_error(f"{description} file not found: {file_path}")


def run_pipeline(audio_file_path: str, base_url: str = "http://localhost:8000"):
    """Run the complete audio processing pipeline"""
    print(f"\n🚀 Starting StubbesScript Pipeline Test")
    print(f"📁 Audio file: {audio_file_path}")
    print(f"🌐 Base URL: {base_url}")
    
    # Step 1: Upload
    upload_result = upload_audio_file(base_url, audio_file_path)
    if not upload_result:
        print_error("Pipeline failed at upload step")
        return False
    
    meeting_id = upload_result.get('meeting_id')
    if not meeting_id:
        print_error("No meeting ID received from upload")
        return False
    
    # Step 2: Transcribe
    transcribe_result = transcribe_audio(base_url, meeting_id)
    if not transcribe_result:
        print_error("Pipeline failed at transcription step")
        return False
    
    # Step 3: Vectorize
    vectorize_result = vectorize_transcript(base_url, meeting_id)
    if not vectorize_result:
        print_error("Pipeline failed at vectorization step")
        return False
    
    # Step 4: Verify files
    files_exist = verify_storage_files(meeting_id)
    
    # Step 5: Print file contents
    print_key_file_contents(meeting_id)
    
    # Final summary
    print_step("PIPELINE COMPLETE", "Summary")
    if files_exist:
        print_success("🎉 Pipeline completed successfully!")
        print_info(f"Meeting ID: {meeting_id}")
        print_info(f"All files generated and verified")
    else:
        print_error("⚠️  Pipeline completed but some files are missing")
    
    return True


def main():
    """Main function with command-line argument parsing"""
    parser = argparse.ArgumentParser(
        description="Test the StubbesScript audio processing pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_pipeline.py --audio_file RiverKiller.mp3
  python test_pipeline.py --audio_file RiverKiller.mp3 --base_url http://localhost:8000
        """
    )
    
    parser.add_argument(
        '--audio_file',
        required=True,
        help='Path to the audio file to process'
    )
    
    parser.add_argument(
        '--base_url',
        default='http://localhost:8000',
        help='Base URL of the API server (default: http://localhost:8000)'
    )
    
    args = parser.parse_args()
    
    # Validate audio file exists
    if not os.path.exists(args.audio_file):
        print_error(f"Audio file not found: {args.audio_file}")
        return 1
    
    # Run the pipeline
    success = run_pipeline(args.audio_file, args.base_url)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main()) 