"""BBHC Theatre - FastAPI Backend
Main application with search and streaming endpoints
"""
import asyncio
import sys
import os

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import codecs
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add parent directory to path for imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Change working directory to project root (where session files are)
os.chdir(parent_dir)

# Try relative imports first, fall back to absolute
try:
    from models import (
        SearchResponse,
        StreamRequest,
        StreamResponse,
        JobStatus,
        ErrorResponse
    )
    from telegram_service import TelegramService
    from job_manager import job_manager
except ImportError:
    from backend.models import (
        SearchResponse,
        StreamRequest,
        StreamResponse,
        JobStatus,
        ErrorResponse
    )
    from backend.telegram_service import TelegramService
    from backend.job_manager import job_manager

from config import API_ID, API_HASH, SEARCH_BOT_USERNAME, STREAMING_BOT_USERNAME


# Global telegram service
telegram_service: TelegramService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown"""
    global telegram_service
    
    # Startup
    print("=" * 60)
    print("🎬 BBHC Theatre Backend Starting...")
    print("=" * 60)
    
    # Initialize Telegram service
    telegram_service = TelegramService(
        api_id=int(API_ID),
        api_hash=API_HASH,
        search_bot=SEARCH_BOT_USERNAME,
        streaming_bot=STREAMING_BOT_USERNAME
    )
    
    await telegram_service.start()
    print(f"✅ Connected to search bot: {SEARCH_BOT_USERNAME}")
    print(f"✅ Streaming bot: {STREAMING_BOT_USERNAME}")
    print("🚀 Backend ready on http://localhost:5000")
    print("=" * 60)
    
    yield
    
    # Shutdown
    print("\n🛑 Shutting down backend...")
    await telegram_service.stop()
    print("✅ Backend stopped")


# Create FastAPI app
app = FastAPI(
    title="BBHC Theatre API",
    description="Backend API for movie search and streaming",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "BBHC Theatre API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "search": "/api/search?q=movie_name",
            "stream": "/api/stream (POST)",
            "job_status": "/api/job/{job_id}"
        }
    }


@app.get("/api/search", response_model=SearchResponse)
async def search_movies(
    q: str = Query(..., description="Search query", min_length=1)
):
    """
    Search for movies/series via Telegram search bot
    
    Returns list of results with available quality options
    """
    try:
        print(f"\n🔍 Search request: {q}")
        
        # Search via Telegram
        results = await telegram_service.search_movie(q)
        
        return SearchResponse(
            query=q,
            results=results,
            total=len(results),
            success=True
        )
    
    except Exception as e:
        print(f"❌ Search error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@app.post("/api/stream", response_model=StreamResponse)
async def request_stream(request: StreamRequest):
    """
    Request streaming URL for a specific quality
    
    Creates a job and processes it asynchronously
    Returns job_id for status tracking
    """
    try:
        print(f"\n📺 Stream request: {request.item_id}, quality index: {request.quality_index}")
        
        # Create job
        job_id = job_manager.create_job(request.item_id, request.quality_index)
        
        # Process job asynchronously
        asyncio.create_task(process_stream_job(job_id, request.item_id, request.quality_index))
        
        return StreamResponse(
            job_id=job_id,
            status="pending",
            message="Stream request received, processing..."
        )
    
    except Exception as e:
        print(f"❌ Stream request error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create stream request: {str(e)}"
        )


@app.get("/api/job/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get status of a streaming job
    
    Poll this endpoint to check if stream URL is ready
    """
    job = job_manager.get_job(job_id)
    
    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found"
        )
    
    return job


@app.delete("/api/cache")
async def clear_cache():
    """Clear message cache and old jobs"""
    telegram_service.clear_cache()
    removed = job_manager.cleanup_old_jobs(max_age_seconds=3600)
    
    return {
        "success": True,
        "message": f"Cache cleared, removed {removed} old jobs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "telegram_connected": telegram_service.client is not None and telegram_service.client.is_connected()
    }


async def process_stream_job(job_id: str, item_id: str, quality_index: int):
    """
    Background task to process streaming request
    
    1. Mark job as processing
    2. Click button / handle callback
    3. Forward to streaming bot
    4. Extract stream URL
    5. Update job with URL or error
    """
    try:
        # Mark as processing
        await job_manager.mark_processing(job_id, "Requesting stream from Telegram...")
        
        # Get stream URL via Telegram
        stream_url = await telegram_service.get_stream_url(item_id, quality_index)
        
        # Mark as done
        await job_manager.mark_done(job_id, stream_url)
        print(f"✅ Job {job_id} completed: {stream_url}")
    
    except Exception as e:
        # Mark as failed
        error_msg = str(e)
        await job_manager.mark_failed(job_id, error_msg)
        print(f"❌ Job {job_id} failed: {error_msg}")


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_code=f"HTTP_{exc.status_code}"
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_code="INTERNAL_ERROR",
            details=str(exc)
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("🎬 Starting BBHC Theatre Backend Server")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
