"""
Darwin Multi-Agent System - Task Model
======================================
Represents human-approved tasks for the Engineer Agent.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .enums import TaskPriority, TaskStatus


class Task(BaseModel):
    """
    A human-approved task for fixing a UX issue.
    
    Created by: NitroStack UI (human approval)
    Consumed by: Engineer Agent
    """
    
    # Identity
    id: Optional[str] = Field(default=None, alias="_id", description="MongoDB ObjectId")
    ux_issue_id: str = Field(..., description="ID of the source UX issue")
    signal_id: Optional[str] = Field(default=None, description="ID of the original signal")
    
    # Task Details
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description with fix details")
    
    # Priority & Status
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Task status")
    
    # Assignment
    assigned_to: str = Field(default="engineer_agent", description="Assigned to (agent or human)")
    
    # Fix Details
    file_path: str = Field(..., description="File to modify")
    line_range: Optional[str] = Field(default=None, description="Line range to modify")
    original_code: Optional[str] = Field(default=None, description="Current code")
    recommended_fix: str = Field(..., description="Recommended code change")
    
    # Output
    pr_url: Optional[str] = Field(default=None, description="Created PR URL")
    pr_number: Optional[int] = Field(default=None, description="PR number")
    branch_name: Optional[str] = Field(default=None, description="Branch name for fix")
    
    # Metadata
    approved_by: Optional[str] = Field(default=None, description="Who approved this task")
    approved_at: Optional[datetime] = Field(default=None, description="When approved")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update")
    completed_at: Optional[datetime] = Field(default=None, description="Completion time")
    
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
    def from_mongo(cls, doc: dict) -> "Task":
        """Create from MongoDB document."""
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return cls(**doc)
