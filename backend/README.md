# StubbesScript Backend

A FastAPI-based backend for audio processing, transcription, and analysis.

## Quick Start

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:

   ```bash
   python main.py
   ```

3. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## Documentation

📚 **Complete documentation is available in the `docs/` folder:**

- **[README.md](docs/README.md)** - Detailed setup and usage guide
- **[API_STRUCTURE.md](docs/API_STRUCTURE.md)** - API endpoint documentation
- **[EMBEDDING_GUIDE.md](docs/EMBEDDING_GUIDE.md)** - Embedding agent implementation guide
- **[TRANSCRIPTION_GUIDE.md](docs/TRANSCRIPTION_GUIDE.md)** - Transcription pipeline guide

## Testing

Run all tests:

```bash
python tests/run_tests.py
```

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── docs/                  # Documentation
│   ├── README.md
│   ├── API_STRUCTURE.md
│   ├── EMBEDDING_GUIDE.md
│   └── TRANSCRIPTION_GUIDE.md
├── tests/                 # Test files
├── routers/               # API route handlers
├── models/                # Pydantic models
├── agents/                # Business logic agents
└── storage/               # File storage
```

## Features

- **Upload**: Audio file upload and management
- **Transcribe**: Audio transcription with confidence scoring
- **Summarize**: Text summarization with key points extraction
- **Insights**: Sentiment analysis, topic detection, and entity recognition
- **Actions**: Task management and workflow automation
- **Flowchart**: Process visualization and diagram generation
- **Query**: Natural language querying of processed content
- **Report**: Comprehensive report generation in multiple formats

For detailed information, see the [complete documentation](docs/README.md).
