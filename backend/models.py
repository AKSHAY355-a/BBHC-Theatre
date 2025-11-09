"""
Data models for BBHC Theatre Backend API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class QualityOption(BaseModel):
    """Represents a quality/format option for streaming"""
    label: str = Field(..., description="Display label (e.g., '720p', '1080p')")
    type: Literal["url", "callback", "forward"] = Field(..., description="Button type")
    value: str | int = Field(..., description="URL, callback data, or button index")


class SearchResultItem(BaseModel):
    """Single search result item"""
    id: str = Field(..., description="Unique identifier for this result")
    title: str = Field(..., description="Movie/series title")
    snippet: Optional[str] = Field(None, description="Description or snippet")
    poster_url: Optional[str] = Field(None, description="Poster image URL")
    year: Optional[int] = Field(None, description="Release year")
    imdb_rating: Optional[float] = Field(None, description="IMDB rating")
    genre: Optional[List[str]] = Field(None, description="List of genres")
    qualities: List[QualityOption] = Field(default_factory=list, description="Available quality options")
    message_chat_id: Optional[int] = Field(None, description="Telegram chat ID")
    message_id: Optional[int] = Field(None, description="Telegram message ID")


class SearchResponse(BaseModel):
    """Response for search endpoint"""
    query: str
    results: List[SearchResultItem]
    total: int
    success: bool = True


class StreamRequest(BaseModel):
    """Request to start streaming"""
    item_id: str = Field(..., description="Result item ID from search")
    quality_index: int = Field(0, description="Index of quality option to use")


class JobStatus(BaseModel):
    """Status of a streaming job"""
    job_id: str
    status: Literal["pending", "processing", "done", "failed"]
    stream_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    progress: Optional[str] = None


class StreamResponse(BaseModel):
    """Response for stream request"""
    job_id: str
    status: str
    message: str = "Stream request received"


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    error_code: str
    details: Optional[str] = None
