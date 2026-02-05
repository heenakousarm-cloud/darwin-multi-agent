"""
Darwin Multi-Agent System - Signal Model
========================================
Represents friction signals detected by the Watcher Agent.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .enums import SignalType, Severity, SignalStatus


class Signal(BaseModel):
    """
    A UX friction signal detected from PostHog analytics.
    
    Created by: Watcher Agent
    Consumed by: Analyst Agent
    """
    
    # Identity
    id: Optional[str] = Field(default=None, alias="_id", description="MongoDB ObjectId")
    
    # Signal Classification
    type: SignalType = Field(..., description="Type of friction signal")
    severity: Severity = Field(..., description="Severity level")
    status: SignalStatus = Field(default=SignalStatus.NEW, description="Processing status")
    
    # Signal Details
    title: str = Field(..., description="Human-readable signal title")
    description: str = Field(..., description="Detailed description of the signal")
    
    # Metrics
    metric_name: str = Field(..., description="Name of the metric (e.g., 'rage_click_count')")
    metric_value: float = Field(..., description="Current value of the metric")
    threshold: Optional[float] = Field(default=None, description="Threshold that was exceeded")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence score 0-1")
    
    # Location
    page: str = Field(..., description="Page/screen where signal occurred")
    element: Optional[str] = Field(default=None, description="Specific element (button, form, etc.)")
    
    # Impact
    affected_users: int = Field(default=0, ge=0, description="Number of users affected")
    session_count: int = Field(default=0, ge=0, description="Number of sessions with this signal")
    
    # Evidence
    recording_ids: List[str] = Field(default_factory=list, description="PostHog recording IDs")
    sample_events: List[dict] = Field(default_factory=list, description="Sample event data")
    
    # Timestamps
    first_seen: datetime = Field(default_factory=datetime.utcnow, description="First occurrence")
    last_seen: datetime = Field(default_factory=datetime.utcnow, description="Most recent occurrence")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation time")
    
    # Processing
    processed: bool = Field(default=False, description="Has been processed by Analyst")
    ux_issue_id: Optional[str] = Field(default=None, description="Linked UX Issue ID if created")
    
    class Config:
        populate_by_name = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_mongo(self) -> dict:
        """Convert to MongoDB document format."""
        data = self.model_dump(by_alias=True, exclude_none=True)
        if "_id" in data and data["_id"] is None:
            del data["_id"]
        return data
    
    @classmethod
    def from_mongo(cls, doc: dict) -> "Signal":
        """Create from MongoDB document."""
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return cls(**doc)
