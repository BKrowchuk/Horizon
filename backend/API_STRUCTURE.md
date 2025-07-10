# StubbesScript API Structure

## Overview

All FastAPI endpoints are now properly organized under `/api/v1/*` with consistent routing and documentation.

## API Endpoints

### Upload Routes (`/api/v1/upload`)

- `POST /api/v1/upload` - Upload audio file
- `GET /api/v1/upload/status/{file_id}` - Get upload status

### Transcription Routes (`/api/v1/transcribe`)

- `POST /api/v1/transcribe` - Transcribe audio file
- `GET /api/v1/transcribe/status/{file_id}` - Get transcription status
- `POST /api/v1/transcribe/meeting` - Transcribe meeting using OpenAI Whisper

### Summarization Routes (`/api/v1/summarize`)

- `POST /api/v1/summarize` - Summarize transcribed text
- `GET /api/v1/summarize/{file_id}` - Get summary for file

### Query Routes (`/api/v1/query`)

- `POST /api/v1/query` - Query processed content
- `GET /api/v1/query/{file_id}/history` - Get query history
- `GET /api/v1/query/suggestions` - Get query suggestions

### Insights Routes (`/api/v1/insights`)

- `POST /api/v1/insights` - Generate insights from content
- `GET /api/v1/insights/{file_id}` - Get insights for file

### Actions Routes (`/api/v1/actions`)

- `POST /api/v1/actions` - Create new action
- `GET /api/v1/actions/{action_id}` - Get action details
- `PUT /api/v1/actions/{action_id}/status` - Update action status
- `GET /api/v1/actions` - List all actions

### Flowchart Routes (`/api/v1/flowchart`)

- `POST /api/v1/flowchart` - Generate flowchart from content
- `GET /api/v1/flowchart/{file_id}` - Get flowchart for file
- `GET /api/v1/flowchart/{file_id}/image` - Get flowchart as image

### Report Routes (`/api/v1/report`)

- `POST /api/v1/report` - Generate comprehensive report
- `GET /api/v1/report/{file_id}` - Get report for file
- `GET /api/v1/report/{file_id}/pdf` - Get report as PDF
- `GET /api/v1/report/{file_id}/html` - Get report as HTML

## File Structure

```
backend/
├── main.py                    # FastAPI app with global router
├── routers/                   # All route modules
│   ├── upload.py             # Upload endpoints
│   ├── transcribe.py         # Transcription endpoints
│   ├── summarize.py          # Summarization endpoints
│   ├── query.py              # Query endpoints
│   ├── insights.py           # Insights endpoints
│   ├── actions.py            # Actions endpoints
│   ├── flowchart.py          # Flowchart endpoints
│   └── report.py             # Report endpoints
├── models/                    # Pydantic models
├── agents/                    # Business logic agents
├── storage/                   # File storage
│   ├── audio/                # Uploaded audio files
│   ├── transcripts/          # Transcription results
│   ├── outputs/              # Generated outputs
│   └── vectors/              # Vector embeddings
└── API_STRUCTURE.md          # This documentation
```

## Key Improvements Made

1. **Consistent Prefixing**: All routes now use `/api/v1/*` prefix through a global router
2. **No Double Prefixing**: Removed duplicate `/api/` prefixes from individual route files
3. **Proper Documentation**: Added `tags` and `summary` parameters to all endpoints
4. **Clean Structure**: Each router file corresponds to a specific domain
5. **Automatic API Docs**: FastAPI will generate clean documentation with proper grouping

## Usage

- All endpoints are accessible under `/api/v1/*`
- API documentation available at `/docs` (Swagger UI)
- Alternative docs at `/redoc` (ReDoc)
- Health check at `/health`
- Root endpoint at `/`
