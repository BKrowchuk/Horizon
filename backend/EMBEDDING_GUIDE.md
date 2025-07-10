# Embedding Agent Guide

## Overview

The embedding agent (`agents/embedding_agent.py`) provides functionality to convert meeting transcripts into vector embeddings using OpenAI's embedding API and store them in FAISS indices for efficient similarity search.

## Features

- **Transcript Chunking**: Splits long transcripts into manageable chunks (~500 words with 50-word overlap)
- **OpenAI Embeddings**: Uses `text-embedding-ada-002` model for high-quality embeddings
- **FAISS Indexing**: Stores vectors in FAISS `IndexFlatL2` for fast similarity search
- **Search Functionality**: Find similar text chunks based on semantic similarity
- **REST API**: Full FastAPI integration with endpoints for embedding and search

## Dependencies

```bash
pip install openai faiss-cpu numpy tiktoken
```

## Core Functions

### `embed_transcript(meeting_id: str) -> dict`

Converts a transcript into vector embeddings and stores them in FAISS index.

**Process:**

1. Loads transcript from `storage/transcripts/{meeting_id}.json`
2. Splits transcript into chunks of ~500 words with 50-word overlap
3. Generates embeddings for each chunk using OpenAI API
4. Creates FAISS index and saves to `storage/vectors/{meeting_id}.index`
5. Saves metadata to `storage/vectors/{meeting_id}_meta.json`

**Returns:**

```json
{
  "meeting_id": "meeting_123",
  "num_chunks": 5,
  "vector_index_path": "storage/vectors/meeting_123.index",
  "meta_path": "storage/vectors/meeting_123_meta.json"
}
```

### `search_similar_chunks(meeting_id: str, query_text: str, top_k: int = 5) -> List[Dict]`

Searches for semantically similar chunks in the embedding index.

**Returns:**

```json
[
  {
    "rank": 1,
    "chunk_id": 2,
    "text": "chunk text...",
    "similarity_score": 0.85,
    "distance": 0.15
  }
]
```

## API Endpoints

### POST `/api/v1/embedding/embed`

Embed a meeting transcript.

**Request:**

```json
{
  "meeting_id": "meeting_123"
}
```

**Response:**

```json
{
  "meeting_id": "meeting_123",
  "num_chunks": 5,
  "vector_index_path": "storage/vectors/meeting_123.index",
  "meta_path": "storage/vectors/meeting_123_meta.json",
  "status": "completed"
}
```

### POST `/api/v1/embedding/search`

Search for similar chunks.

**Request:**

```json
{
  "meeting_id": "meeting_123",
  "query_text": "neural networks and deep learning",
  "top_k": 5
}
```

**Response:**

```json
{
  "meeting_id": "meeting_123",
  "query_text": "neural networks and deep learning",
  "results": [
    {
      "rank": 1,
      "chunk_id": 2,
      "text": "We discussed neural networks...",
      "similarity_score": 0.85,
      "distance": 0.15
    }
  ],
  "total_results": 1
}
```

### GET `/api/v1/embedding/status/{meeting_id}`

Check embedding status for a meeting.

**Response:**

```json
{
  "meeting_id": "meeting_123",
  "status": "embedded",
  "num_chunks": 5,
  "embedding_model": "text-embedding-ada-002",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## Usage Examples

### Python Usage

```python
from agents.embedding_agent import embed_transcript, search_similar_chunks

# Embed a transcript
result = embed_transcript("meeting_123")
print(f"Embedded {result['num_chunks']} chunks")

# Search for similar content
results = search_similar_chunks(
    meeting_id="meeting_123",
    query_text="machine learning algorithms",
    top_k=3
)

for result in results:
    print(f"Rank {result['rank']}: {result['text'][:100]}...")
```

### Command Line Testing

```bash
# Run the test script
cd backend
python test_embedding_agent.py
```

## File Structure

```
backend/
├── agents/
│   └── embedding_agent.py          # Main embedding functionality
├── routers/
│   └── embedding.py                # FastAPI router
├── storage/
│   ├── transcripts/
│   │   └── {meeting_id}.json      # Transcript files
│   └── vectors/
│       ├── {meeting_id}.index     # FAISS index files
│       └── {meeting_id}_meta.json # Metadata files
└── test_embedding_agent.py        # Test script
```

## Configuration

### Environment Variables

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Chunking Parameters

Default chunking parameters can be modified in `split_transcript_into_chunks()`:

- `chunk_size_words`: 500 (target words per chunk)
- `overlap_words`: 50 (overlap between chunks)

### Embedding Model

Currently uses `text-embedding-ada-002`. To change:

```python
embedding_response = openai.embeddings.create(
    model="text-embedding-3-small",  # Alternative model
    input=chunk_text
)
```

## Error Handling

The agent handles common errors:

- **FileNotFoundError**: Transcript file doesn't exist
- **ValueError**: No transcript text found
- **OpenAI API Errors**: Network issues, rate limits, etc.
- **FAISS Errors**: Index creation/saving issues

## Performance Considerations

- **Chunk Size**: Larger chunks (500+ words) provide better context but slower processing
- **Overlap**: 50-word overlap helps maintain context across chunk boundaries
- **FAISS Index**: `IndexFlatL2` provides exact search but may be slow for large datasets
- **API Rate Limits**: Consider batching for large transcripts

## Future Enhancements

- **Advanced Chunking**: Sentence-aware splitting with LangChain
- **Multiple Models**: Support for different embedding models
- **Index Optimization**: Use FAISS IVF or HNSW for better performance
- **Batch Processing**: Process multiple meetings simultaneously
- **Caching**: Cache embeddings to avoid re-computation
