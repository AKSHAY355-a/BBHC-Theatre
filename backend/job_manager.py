"""
Job Manager for async streaming requests
Handles job queue, state tracking, and job lifecycle
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional
from .models import JobStatus


class JobManager:
    """Manages streaming jobs with in-memory storage"""
    
    def __init__(self):
        self.jobs: Dict[str, dict] = {}
        self.lock = asyncio.Lock()
    
    def create_job(self, item_id: str, quality_index: int) -> str:
        """Create a new streaming job"""
        job_id = str(uuid.uuid4())
        now = datetime.now()
        
        self.jobs[job_id] = {
            "job_id": job_id,
            "item_id": item_id,
            "quality_index": quality_index,
            "status": "pending",
            "stream_url": None,
            "error": None,
            "created_at": now,
            "updated_at": now,
            "progress": "Job created"
        }
        
        return job_id
    
    async def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        stream_url: Optional[str] = None,
        error: Optional[str] = None,
        progress: Optional[str] = None
    ):
        """Update job status"""
        async with self.lock:
            if job_id not in self.jobs:
                raise ValueError(f"Job {job_id} not found")
            
            job = self.jobs[job_id]
            
            if status:
                job["status"] = status
            if stream_url:
                job["stream_url"] = stream_url
            if error:
                job["error"] = error
            if progress:
                job["progress"] = progress
            
            job["updated_at"] = datetime.now()
    
    def get_job(self, job_id: str) -> Optional[JobStatus]:
        """Get job status"""
        if job_id not in self.jobs:
            return None
        
        job_data = self.jobs[job_id]
        return JobStatus(**job_data)
    
    async def mark_processing(self, job_id: str, progress: str = "Processing request"):
        """Mark job as processing"""
        await self.update_job(job_id, status="processing", progress=progress)
    
    async def mark_done(self, job_id: str, stream_url: str):
        """Mark job as completed"""
        await self.update_job(
            job_id,
            status="done",
            stream_url=stream_url,
            progress="Stream ready"
        )
    
    async def mark_failed(self, job_id: str, error: str):
        """Mark job as failed"""
        await self.update_job(
            job_id,
            status="failed",
            error=error,
            progress="Failed"
        )
    
    def cleanup_old_jobs(self, max_age_seconds: int = 3600):
        """Remove jobs older than max_age_seconds"""
        now = datetime.now()
        to_remove = []
        
        for job_id, job in self.jobs.items():
            age = (now - job["created_at"]).total_seconds()
            if age > max_age_seconds:
                to_remove.append(job_id)
        
        for job_id in to_remove:
            del self.jobs[job_id]
        
        return len(to_remove)


# Global job manager instance
job_manager = JobManager()
