# Transcription System Guide

## Overview

The transcription system uses OpenAI's Whisper API to transcribe audio files. It expects audio files to be stored in `storage/audio/{meeting_id}_audio.mp3` format and saves transcripts to `storage/transcripts/{meeting_id}.json`.

## API Endpoint

### POST `/api/v1/transcribe`

Transcribes an audio file using OpenAI Whisper.

**Request Body:**

```json
{
  "meeting_id": "your-meeting-id"
}
```

**Response:**

```json
{
  "meeting_id": "your-meeting-id",
  "project_id": "demo_project",
  "created_at": "2024-06-02T15:00:00Z",
  "transcript": "All the words spoken at the meeting..."
}
```

## File Structure

- **Audio files**: `storage/audio/{meeting_id}_audio.mp3`
- **Transcript files**: `storage/transcripts/{meeting_id}.json`

## Example Usage

1. **Place your audio file** in `storage/audio/` with the naming convention `{meeting_id}_audio.mp3`

2. **Make a POST request** to transcribe:

   ```bash
   curl -X POST "http://localhost:8000/api/v1/transcribe" \
        -H "Content-Type: application/json" \
        -d '{"meeting_id": "your-meeting-id"}'
   ```

3. **Check the transcript file** at `storage/transcripts/{meeting_id}.json`

## Error Handling

- **404**: Audio file not found
- **500**: OpenAI API error or other transcription failure

## Testing

Run the test script to verify the system works:

```bash
cd backend
python test_transcription.py
```

Make sure the server is running on `localhost:8000` before running the test.
