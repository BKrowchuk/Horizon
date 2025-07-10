# Summary Agent Guide

## Overview

The Summary Agent (`agents/summary_agent.py`) is responsible for generating comprehensive summaries of meeting transcripts using OpenAI's Chat Completion API.

## Features

- **AI-Powered Summarization**: Uses GPT-4 to generate professional meeting summaries
- **Comprehensive Coverage**: Focuses on key discussion points, decisions made, and narrative flow
- **Structured Output**: Saves summaries in a consistent JSON format
- **Error Handling**: Robust error handling with detailed logging

## API Endpoint

### POST `/api/v1/summarize`

Generates a summary for a meeting transcript.

**Request Body:**

```json
{
  "meeting_id": "string"
}
```

**Response:**

```json
{
  "meeting_id": "string",
  "project_id": "string",
  "created_at": "ISO timestamp",
  "summary": "Generated summary text"
}
```

## Usage

### Direct Function Call

```python
from agents.summary_agent import generate_summary

# Generate summary for a meeting
summary_data = generate_summary("meeting_id_123")
print(summary_data["summary"])
```

### API Call

```bash
curl -X POST "http://localhost:8000/api/v1/summarize" \
  -H "Content-Type: application/json" \
  -d '{"meeting_id": "meeting_id_123"}'
```

## File Structure

### Input

- **Location**: `storage/transcripts/{meeting_id}.json`
- **Format**: JSON with transcript text and metadata

### Output

- **Location**: `storage/outputs/{meeting_id}_summary.json`
- **Format**: JSON with summary data

## Configuration

### OpenAI Settings

- **Model**: `gpt-4` (configurable to `gpt-3.5-turbo`)
- **Temperature**: `0.3` (for consistent output)
- **Max Tokens**: `1000` (summary length limit)

### System Prompt

The agent uses a professional system prompt that instructs the AI to:

- Create concise but comprehensive summaries
- Focus on key discussion points
- Highlight decisions made
- Maintain narrative flow

## Error Handling

The agent handles various error scenarios:

- **FileNotFoundError**: When transcript file doesn't exist
- **ValueError**: When transcript text is empty
- **OpenAI API Errors**: Network issues, rate limits, etc.

## Testing

Run the test suite to verify functionality:

```bash
cd backend/tests
python test_summary_agent.py
```

## Dependencies

- `openai`: OpenAI API client
- `json`: JSON data handling
- `pathlib`: File path operations
- `datetime`: Timestamp generation
- `logging`: Error and info logging

## Environment Variables

Ensure the following environment variable is set:

- `OPENAI_API_KEY`: Your OpenAI API key
