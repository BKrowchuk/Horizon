# StubbesScript Backend API

A FastAPI-based backend for audio processing, transcription, and analysis.

## Features

- **Upload**: Audio file upload and management
- **Transcribe**: Audio transcription with confidence scoring
- **Summarize**: Text summarization with key points extraction
- **Insights**: Sentiment analysis, topic detection, and entity recognition
- **Actions**: Task management and workflow automation
- **Flowchart**: Process visualization and diagram generation
- **Query**: Natural language querying of processed content
- **Report**: Comprehensive report generation in multiple formats

## Setup

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:

   ```bash
   python main.py
   ```

   Or using uvicorn directly:

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## Complete Workflow Example

Here's a complete example of uploading and transcribing an audio file using curl:

### 1. Upload Audio File

```bash
curl -X POST "http://localhost:8000/api/v1/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@C:\src\StubbesScript\RiverKiller.mp3"
```

**Response:**

```json
{
  "meeting_id": "uuid-string-here",
  "filename": "uuid-string-here_audio.mp3"
}
```

### 2. Transcribe the Uploaded Audio

After uploading, you can transcribe using either of these endpoints:

#### Option A: Using the /transcribe endpoint (requires file_id)

```bash
curl -X POST "http://localhost:8000/api/v1/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "your-meeting-id-here",
    "language": "en",
    "model": "default"
  }'
```

#### Option B: Using the /api/transcribe endpoint (requires meeting_id)

```bash
curl -X POST "http://localhost:8000/api/v1/api/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "your-meeting-id-here"
  }'
```

**Response:**

```json
{
  "success": true,
  "file_id": "your-meeting-id-here",
  "transcript": "This is the transcribed text...",
  "confidence": 0.95,
  "language": "en",
  "duration": 120.5
}
```

### Complete Example with RiverKiller.mp3

```bash
# 1. Upload the audio file
curl -X POST "http://localhost:8000/api/v1/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@RiverKiller.mp3"

# 2. Use the meeting_id from the response to transcribe
curl -X POST "http://localhost:8000/api/v1/api/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_id": "meeting-id-from-upload-response"
  }'
```

**Notes:**

- The server needs to be running on `localhost:8000` (default FastAPI port)
- Replace `your-meeting-id-here` with the actual `meeting_id` returned from the upload response
- The API supports various audio formats: `.mp3`, `.wav`, `.m4a`, `.flac`, `.ogg`, `.aac`

## API Endpoints

### Upload

- `POST /api/v1/api/upload` - Upload audio file
- `GET /api/v1/upload/status/{file_id}` - Get upload status

### Transcribe

- `POST /api/v1/transcribe` - Transcribe audio file
- `POST /api/v1/api/transcribe` - Transcribe meeting audio
- `GET /api/v1/transcribe/status/{file_id}` - Get transcription status

### Summarize

- `POST /api/v1/summarize` - Summarize transcribed text
- `GET /api/v1/summarize/{file_id}` - Get summary

### Insights

- `POST /api/v1/insights` - Generate insights
- `GET /api/v1/insights/{file_id}` - Get insights

### Actions

- `POST /api/v1/actions` - Create action
- `GET /api/v1/actions/{action_id}` - Get action details
- `PUT /api/v1/actions/{action_id}/status` - Update action status
- `GET /api/v1/actions` - List all actions

### Flowchart

- `POST /api/v1/flowchart` - Generate flowchart
- `GET /api/v1/flowchart/{file_id}` - Get flowchart
- `GET /api/v1/flowchart/{file_id}/image` - Get flowchart image

### Query

- `POST /api/v1/query` - Query content
- `GET /api/v1/query/{file_id}/history` - Get query history
- `GET /api/v1/query/suggestions` - Get query suggestions

### Report

- `POST /api/v1/report` - Generate report
- `GET /api/v1/report/{file_id}` - Get report
- `GET /api/v1/report/{file_id}/pdf` - Get report as PDF
- `GET /api/v1/report/{file_id}/html` - Get report as HTML

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── routers/               # API route handlers
│   ├── __init__.py
│   ├── upload.py
│   ├── transcribe.py
│   ├── summarize.py
│   ├── insights.py
│   ├── actions.py
│   ├── flowchart.py
│   ├── query.py
│   └── report.py
├── models/                # Pydantic models
│   ├── __init__.py
│   ├── upload.py
│   ├── transcribe.py
│   ├── summarize.py
│   ├── insights.py
│   ├── actions.py
│   ├── flowchart.py
│   ├── query.py
│   └── report.py
└── storage/               # File storage
    ├── audio/             # Uploaded audio files
    ├── transcripts/       # Transcription results
    ├── vectors/           # Vector embeddings
    └── outputs/           # Generated outputs
```

## Development

This is a monorepo structure. The backend is located in the `backend/` directory and can be developed independently or as part of the larger project.

## TODO

- Implement actual transcription service integration
- Add authentication and authorization
- Implement vector storage and similarity search
- Add real-time processing capabilities
- Implement PDF and HTML report generation
- Add comprehensive error handling and logging
- Add unit tests and integration tests
