from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, transcribe, summarize, insights, actions, flowchart, query, report

app = FastAPI(
    title="StubbesScript API",
    description="API for audio processing, transcription, and analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(transcribe.router, prefix="/api/v1", tags=["transcribe"])
app.include_router(summarize.router, prefix="/api/v1", tags=["summarize"])
app.include_router(insights.router, prefix="/api/v1", tags=["insights"])
app.include_router(actions.router, prefix="/api/v1", tags=["actions"])
app.include_router(flowchart.router, prefix="/api/v1", tags=["flowchart"])
app.include_router(query.router, prefix="/api/v1", tags=["query"])
app.include_router(report.router, prefix="/api/v1", tags=["report"])

@app.get("/")
async def root():
    return {"message": "StubbesScript API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 