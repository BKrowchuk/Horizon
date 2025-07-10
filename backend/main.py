from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from routers import upload, transcribe, summarize, insights, actions, flowchart, query, report, embedding

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

# Create global router with /api/v1 prefix
router = APIRouter(prefix="/api/v1")

# Include all routers under the global router
router.include_router(upload.router, tags=["upload"])
router.include_router(transcribe.router, tags=["transcribe"])
router.include_router(summarize.router, tags=["summarize"])
router.include_router(insights.router, tags=["insights"])
router.include_router(actions.router, tags=["actions"])
router.include_router(flowchart.router, tags=["flowchart"])
router.include_router(query.router, tags=["query"])
router.include_router(report.router, tags=["report"])
router.include_router(embedding.router, tags=["embedding"])

# Mount the global router on the app
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "StubbesScript API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)