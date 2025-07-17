# Horizon API - cURL Requests

This document contains all the cURL requests for the Horizon API endpoints. Make sure your FastAPI server is running on `localhost:8000` before executing these commands.

## Base URL

All endpoints are prefixed with: `http://localhost:8000/api/v1`

## 1. Upload Audio File

Upload an audio file to the system. This is the first step in the workflow.

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@RiverKiller.mp3"
```

**Response Example:**

```json
{
  "meeting_id": "abc123-def456-7890-ghij-klmnopqrstuv",
  "filename": "abc123-def456-7890-ghij-klmnopqrstuv_audio.mp3"
}
```

## 2. Check Upload Status

Check if a file has been uploaded successfully.

```bash
curl -X GET "http://localhost:8000/api/v1/upload/status/your-meeting-id-here"
```

## 3. Transcribe Audio File

Transcribe the uploaded audio file using OpenAI Whisper.

```bash
curl -X POST "http://localhost:8000/api/v1/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "your-meeting-id-here"
  }'
```

**Response Example:**

```json
{
  "meeting_id": "abc123-def456-7890-ghij-klmnopqrstuv",
  "project_id": "project_123",
  "created_at": "2024-01-01T12:00:00Z",
  "transcript": "This is the transcribed text from the audio file..."
}
```

## 4. Embed Transcript

Create vector embeddings from the transcribed text for semantic search.

```bash
curl -X POST "http://localhost:8000/api/v1/embedding/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "fb9ceb5a-be59-4196-b04e-f739989bedc2"
  }'
```

**Response Example:**

```json
{
  "meeting_id": "abc123-def456-7890-ghij-klmnopqrstuv",
  "num_chunks": 15,
  "vector_index_path": "storage/vectors/abc123-def456-7890-ghij-klmnopqrstuv.index",
  "meta_path": "storage/vectors/abc123-def456-7890-ghij-klmnopqrstuv_meta.json",
  "status": "completed"
}
```

## 5. Summarize Transcript

Generate a summary of the transcribed content.

```bash
curl -X POST "http://localhost:8000/api/v1/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "fb9ceb5a-be59-4196-b04e-f739989bedc2"
  }'
```

**Response Example:**

```json
{
  "meeting_id": "abc123-def456-7890-ghij-klmnopqrstuv",
  "project_id": "project_123",
  "created_at": "2024-01-01T12:00:00Z",
  "summary": "This meeting covered the following key points..."
}
```

## 6. Search Embeddings

Search for similar content in the embedded transcript.

```bash
curl -X POST "http://localhost:8000/api/v1/embedding/search" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "fb9ceb5a-be59-4196-b04e-f739989bedc2",
    "query_text": "your search query here",
    "top_k": 5
  }'
```

**Response Example:**

```json
{
  "meeting_id": "abc123-def456-7890-ghij-klmnopqrstuv",
  "query_text": "your search query here",
  "results": [
    {
      "rank": 1,
      "chunk_id": 5,
      "text": "Relevant text chunk...",
      "similarity_score": 0.95,
      "distance": 0.05
    }
  ],
  "total_results": 1
}
```

## 7. Check Embedding Status

Check if embeddings exist for a meeting.

```bash
curl -X GET "http://localhost:8000/api/v1/embedding/status/your-meeting-id-here"
```

**Response Example:**

```json
{
  "meeting_id": "abc123-def456-7890-ghij-klmnopqrstuv",
  "status": "embedded",
  "num_chunks": 15,
  "embedding_model": "text-embedding-ada-002",
  "created_at": "2024-01-01T12:00:00Z"
}
```

## Complete Workflow Example

Here's a typical workflow using the same `meeting_id` throughout:

1. **Upload** your audio file:

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@RiverKiller.mp3"
```

2. **Transcribe** the audio (using the `meeting_id` from step 1):

```bash
curl -X POST "http://localhost:8000/api/v1/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "abc123-def456-7890-ghij-klmnopqrstuv"
  }'
```

3. **Embed** the transcript:

```bash
curl -X POST "http://localhost:8000/api/v1/embedding/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "abc123-def456-7890-ghij-klmnopqrstuv"
  }'
```

4. **Summarize** the content:

```bash
curl -X POST "http://localhost:8000/api/v1/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "abc123-def456-7890-ghij-klmnopqrstuv"
  }'
```

5. **Search** the embeddings (optional):

```bash
curl -X POST "http://localhost:8000/api/v1/embedding/search" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "abc123-def456-7890-ghij-klmnopqrstuv",
    "query_text": "What was discussed about the budget?",
    "top_k": 3
  }'
```

## Notes

- Replace `your-meeting-id-here` with the actual `meeting_id` returned from the upload step
- The server must be running on `localhost:8000` (adjust URL if different)
- All audio files should be in supported formats: mp3, wav, m4a, flac, ogg, aac
- The `meeting_id` is a UUID that links all operations for the same audio file
- Each step depends on the previous step being completed successfully
