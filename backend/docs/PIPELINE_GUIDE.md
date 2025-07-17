# Pipeline API Guide

The Pipeline API provides a comprehensive endpoint that processes audio files through the entire workflow from upload to summarization and embedding.

## Endpoints

### 1. Process Audio Pipeline (Synchronous)

**Endpoint:** `POST /api/v1/pipeline/process-sync`

Process an audio file through the entire pipeline synchronously and return complete results.

**Request:**

- Content-Type: `multipart/form-data`
- Body: Audio file (mp3, wav, m4a, flac, ogg, aac)

**Response:**

```json
{
  "meeting_id": "uuid-string",
  "filename": "uuid-string_audio.mp3",
  "status": "completed",
  "steps_completed": ["upload", "transcribe", "summarize", "embed"],
  "transcript": {
    "meeting_id": "uuid-string",
    "project_id": "demo_project",
    "created_at": "2024-01-01T12:00:00Z",
    "transcript": "Transcribed text content...",
    "original_length": 1000,
    "cleaned_length": 950,
    "whisper_params": {
      "language": "en",
      "temperature": 0.0,
      "prompt": "This is a song or music recording. Transcribe the lyrics accurately."
    }
  },
  "summary": {
    "meeting_id": "uuid-string",
    "project_id": "demo_project",
    "created_at": "2024-01-01T12:05:00Z",
    "summary": "Generated summary content..."
  },
  "embedding": {
    "meeting_id": "uuid-string",
    "num_chunks": 5,
    "vector_index_path": "storage/vectors/uuid-string.index",
    "meta_path": "storage/vectors/uuid-string_meta.json"
  }
}
```

### 2. Process Audio Pipeline (Asynchronous)

**Endpoint:** `POST /api/v1/pipeline/process`

Process an audio file through the entire pipeline asynchronously.

**Request:**

- Content-Type: `multipart/form-data`
- Body: Audio file (mp3, wav, m4a, flac, ogg, aac)

**Response:**

```json
{
  "meeting_id": "uuid-string",
  "filename": "uuid-string_audio.mp3",
  "status": "processing",
  "steps_completed": ["upload"]
}
```

### 3. Get Pipeline Status

**Endpoint:** `GET /api/v1/pipeline/status/{meeting_id}`

Check the status of pipeline processing for a meeting.

**Response:**

```json
{
  "meeting_id": "uuid-string",
  "status": "completed",
  "steps_completed": ["upload", "transcribe", "summarize", "embed"],
  "progress": {
    "upload": {
      "status": "completed"
    },
    "transcribe": {
      "status": "completed",
      "data": {
        "created_at": "2024-01-01T12:00:00Z",
        "transcript_length": 1000
      }
    },
    "summarize": {
      "status": "completed",
      "data": {
        "created_at": "2024-01-01T12:05:00Z",
        "summary_length": 200
      }
    },
    "embed": {
      "status": "completed",
      "data": {
        "num_chunks": 5,
        "embedding_model": "text-embedding-ada-002"
      }
    }
  }
}
```

## Pipeline Steps

The pipeline processes audio files through the following steps:

1. **Upload**: Store the audio file with a unique meeting ID
2. **Transcribe**: Convert audio to text using OpenAI Whisper
3. **Summarize**: Generate a summary using OpenAI GPT-4
4. **Embed**: Create vector embeddings for semantic search

## Usage Examples

### cURL Example (Synchronous)

```bash
curl -X POST "http://localhost:8000/api/v1/pipeline/process-sync" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/audio.mp3"
```

### cURL Example (Asynchronous)

```bash
# Start processing
curl -X POST "http://localhost:8000/api/v1/pipeline/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/audio.mp3"

# Check status
curl -X GET "http://localhost:8000/api/v1/pipeline/status/{meeting_id}"
```

### Python Example

```python
import requests

# Process file synchronously
with open("audio.mp3", "rb") as f:
    files = {"file": ("audio.mp3", f, "audio/mpeg")}
    response = requests.post(
        "http://localhost:8000/api/v1/pipeline/process-sync",
        files=files
    )

if response.status_code == 200:
    result = response.json()
    print(f"Meeting ID: {result['meeting_id']}")
    print(f"Status: {result['status']}")
    print(f"Transcript: {result['transcript']['transcript']}")
    print(f"Summary: {result['summary']['summary']}")
```

## Error Handling

The pipeline handles various error scenarios:

- **Invalid file type**: Returns 400 error for non-audio files
- **Processing errors**: Returns 500 error with details
- **File not found**: Returns 404 error for missing files

## File Storage

Processed files are stored in the following structure:

```
storage/
├── audio/
│   └── {meeting_id}_audio.mp3
├── transcripts/
│   └── {meeting_id}.json
├── outputs/
│   └── {meeting_id}_summary.json
└── vectors/
    ├── {meeting_id}.index
    └── {meeting_id}_meta.json
```

## Performance Considerations

- **Synchronous processing**: Best for small files and immediate results
- **Asynchronous processing**: Better for large files and background processing
- **File size limits**: Consider your server's memory and processing capabilities
- **API rate limits**: Be aware of OpenAI API rate limits for large-scale processing
