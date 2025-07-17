# Query Agent Guide

## Overview

The Query Agent provides semantic search capabilities for meeting content using OpenAI embeddings and FAISS vector search. It enables users to ask natural language questions about meeting transcripts and receive relevant answers with source citations.

## Features

- **Semantic Search**: Uses OpenAI's text-embedding-ada-002 model to convert queries into embeddings
- **Vector Search**: Leverages FAISS for fast similarity search across meeting chunks
- **AI-Powered Answers**: Uses GPT-3.5-turbo to generate contextual answers based on relevant transcript chunks
- **Source Citations**: Provides similarity scores and text previews for source chunks
- **Query History**: Automatically saves all queries and responses for future reference
- **Error Handling**: Comprehensive error handling for missing files, API failures, and invalid inputs

## Architecture

### Components

1. **Query Agent** (`agents/query_agent.py`)

   - Core semantic search functionality
   - OpenAI API integration
   - FAISS vector search
   - Query history management

2. **Query Router** (`routers/query.py`)

   - REST API endpoints
   - Request/response validation
   - Error handling

3. **Storage Structure**
   - Vector indices: `storage/vectors/{meeting_id}.index`
   - Metadata: `storage/vectors/{meeting_id}_meta.json`
   - Query history: `storage/outputs/{meeting_id}_queries.json`

## API Endpoints

### POST `/api/v1/query/query`

Query meeting content using semantic search.

**Request Body:**

```json
{
  "meeting_id": "string",
  "query": "string"
}
```

**Response:**

```json
{
  "meeting_id": "string",
  "query": "string",
  "answer": "string",
  "sources": [
    {
      "chunk_id": 0,
      "similarity_score": 0.85,
      "text_preview": "first 100 chars of chunk..."
    }
  ],
  "timestamp": "2024-01-01T12:00:00"
}
```

### GET `/api/v1/query/query/{meeting_id}/history`

Get query history for a meeting.

**Response:**

```json
{
  "meeting_id": "string",
  "queries": [
    {
      "meeting_id": "string",
      "query": "string",
      "answer": "string",
      "sources": [...],
      "timestamp": "string"
    }
  ]
}
```

### GET `/api/v1/query/suggestions`

Get suggested queries.

**Response:**

```json
{
  "suggestions": [
    "What are the main topics discussed?",
    "What action items were mentioned?",
    "What decisions were made?",
    "Who were the key participants?",
    "What was the overall sentiment?",
    "What challenges were identified?",
    "What solutions were proposed?",
    "What is the next meeting about?",
    "What deadlines were mentioned?",
    "What resources were discussed?"
  ]
}
```

## Usage Examples

### Basic Query

```python
from agents.query_agent import query_meeting

# Query a meeting
result = query_meeting("meeting_123", "What were the main topics discussed?")

print(f"Answer: {result['answer']}")
print(f"Sources: {len(result['sources'])} found")
```

### API Usage

```python
import requests

# Query via API
response = requests.post("http://localhost:8000/api/v1/query/query", json={
    "meeting_id": "meeting_123",
    "query": "What action items were mentioned?"
})

data = response.json()
print(f"Answer: {data['answer']}")
```

## Error Handling

### Common Error Scenarios

1. **Missing Vector Index**

   ```
   Error: Vector index not found for meeting_id: {meeting_id}
   Solution: Ensure the meeting has been processed through the embedding pipeline
   ```

2. **Empty Query**

   ```
   Error: Query cannot be empty
   Solution: Provide a non-empty query string
   ```

3. **OpenAI API Failure**

   ```
   Error: Query failed: OpenAI API error
   Solution: Check API key and network connectivity
   ```

4. **No Relevant Chunks**
   ```
   Answer: "I don't have enough information to answer this question based on the meeting content."
   Sources: []
   ```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for OpenAI API access

### Dependencies

- `openai==1.3.0`: OpenAI API client
- `faiss-cpu>=1.7.4`: Vector similarity search
- `numpy>=1.26.0`: Numerical operations
- `python-dotenv==1.0.0`: Environment variable management

## Performance Considerations

### Search Parameters

- **Top-k Results**: Default 5 most similar chunks
- **Similarity Threshold**: Automatic filtering based on distance
- **Context Window**: Top 3 chunks used for answer generation

### Optimization Tips

1. **Chunk Size**: Optimal chunk size is 500 words with 50-word overlap
2. **Vector Dimension**: 1536 dimensions for text-embedding-ada-002
3. **Index Type**: FAISS IndexFlatL2 for L2 distance search

## Testing

### Structure Tests

```bash
python test_query_structure.py
```

### API Tests

```bash
# Start the server
python main.py

# In another terminal
python test_query_api.py
```

### Integration Tests

```bash
python tests/test_pipeline.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**

   - Ensure all dependencies are installed: `pip install -r requirements.txt`

2. **API Key Issues**

   - Verify `OPENAI_API_KEY` is set in environment or `.env` file

3. **File Not Found Errors**

   - Check that meeting has been processed through the full pipeline
   - Verify file paths are correct for your system

4. **Memory Issues**
   - Large meetings may require more memory for vector operations
   - Consider processing meetings in smaller chunks

## Future Enhancements

### Planned Features

1. **Multi-meeting Search**: Search across multiple meetings
2. **Advanced Filtering**: Filter by date, participants, or topics
3. **Query Templates**: Pre-defined query templates for common questions
4. **Confidence Scoring**: Enhanced confidence metrics for answers
5. **Export Functionality**: Export query results to various formats

### Performance Improvements

1. **Caching**: Cache frequently accessed embeddings
2. **Batch Processing**: Process multiple queries in batch
3. **Async Operations**: Non-blocking query processing
4. **Compression**: Compress vector indices for storage efficiency

## Contributing

When contributing to the query agent:

1. Follow the existing code structure and patterns
2. Add comprehensive error handling
3. Include tests for new functionality
4. Update documentation for any API changes
5. Ensure backward compatibility

## License

This query agent is part of the Horizon project and follows the same licensing terms.
