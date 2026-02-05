"""
Darwin Multi-Agent System - UX Issue Model
==========================================
Represents diagnosed UX issues with root cause and recommended fixes.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from .enums import Severity, UXIssueStatus, TaskPriority


class RecommendedFix(BaseModel):
    """A recommended code fix for a UX issue."""
    
    title: str = Field(..., description="Short title for the fix")
    description: str = Field(..., description="Detailed description of what to change")
    file_path: str = Field(..., description="Path to file that needs modification")
    line_start: Optional[int] = Field(default=None, description="Starting line number")
    line_end: Optional[int] = Field(default=None, description="Ending line number")
    original_code: Optional[str] = Field(default=None, description="Current code snippet")
    suggested_code: Optional[str] = Field(default=None, description="Suggested replacement code")
    estimated_effort: str = Field(default="small", description="small, medium, large")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in this fix")


class UXIssue(BaseModel):
    """
    A diagnosed UX issue with root cause analysis and fix recommendations.
    
    Created by: Analyst Agent
    Consumed by: Engineer Agent (after human approval)
    """
    
    # Identity
    id: Optional[str] = Field(default=None, alias="_id", description="MongoDB ObjectId")
    signal_id: str = Field(..., description="ID of the source signal")
    
    # Status & Priority
    status: UXIssueStatus = Field(default=UXIssueStatus.DETECTED, description="Issue status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Priority level")
    severity: Severity = Field(default=Severity.MEDIUM, description="Severity level")
    
    # Issue Details
    title: str = Field(..., description="Human-readable issue title")
    description: str = Field(..., description="Detailed issue description")
    
    # Location
    page: str = Field(..., description="Page/screen affected")
    page_info: Optional[str] = Field(default=None, description="Additional page context")
    component: Optional[str] = Field(default=None, description="Specific component affected")
    
    # Impact Metrics
    affected_users: int = Field(default=0, ge=0, description="Number of users affected")
    replays_count: int = Field(default=0, ge=0, description="Number of session replays available")
    conversion_impact: Optional[float] = Field(default=None, description="Estimated conversion impact %")
    
    # Analysis
    root_cause: str = Field(..., description="Identified root cause")
    user_impact: str = Field(..., description="How this affects users")
    business_impact: str = Field(..., description="Business impact of this issue")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Analysis confidence 0-1")
    
    # Recommended Fix
    recommended_fix: Optional[RecommendedFix] = Field(default=None, description="Recommended code fix")
    
    # Code Location
    file_path: Optional[str] = Field(default=None, description="Primary file to modify")
    line_range: Optional[str] = Field(default=None, description="Line range (e.g., '345-360')")
    
    # Evidence
    recording_urls: List[str] = Field(default_factory=list, description="Session recording URLs")
    screenshots: List[str] = Field(default_factory=list, description="Screenshot URLs")
    
    # Tracking
    task_id: Optional[str] = Field(default=None, description="Linked task ID if approved")
    pr_url: Optional[str] = Field(default=None, description="GitHub PR URL if created")
    
    # Timestamps
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="When detected")
    analyzed_at: Optional[datetime] = Field(default=None, description="When analysis completed")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    
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
        # Handle nested model
        if "recommended_fix" in data and data["recommended_fix"]:
            data["recommended_fix"] = dict(data["recommended_fix"])
        return data
    
    @classmethod
    def from_mongo(cls, doc: dict) -> "UXIssue":
        """Create from MongoDB document."""
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return cls(**doc)
