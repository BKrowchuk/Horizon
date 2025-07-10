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

## API Endpoints

### Upload

- `POST /api/v1/upload` - Upload audio file
- `GET /api/v1/upload/status/{file_id}` - Get upload status

### Transcribe

- `POST /api/v1/transcribe` - Transcribe audio file
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
