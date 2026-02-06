"""
UX Issues API Routes

Endpoints for managing UX issues (diagnosed friction points).
"""

from fastapi import APIRouter, Query, HTTPException, Body
from typing import Optional
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.db import find_many, find_by_id, update_by_id

router = APIRouter()


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable format."""
    if doc is None:
        return None
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    # Handle datetime fields
    for key, value in doc.items():
        if isinstance(value, datetime):
            doc[key] = value.isoformat()
    return doc


@router.get("/")
async def get_ux_issues(
    status: Optional[str] = Query(None, description="Filter by status (diagnosed, approved, rejected, pr_created)"),
    priority: Optional[str] = Query(None, description="Filter by priority (critical, high, medium, low)"),
    limit: int = Query(50, description="Maximum number of results", ge=1, le=100),
):
    """
    Get all UX issues.
    
    Optionally filter by status or priority.
    """
    query = {}
    
    if status:
        query["status"] = status
    if priority:
        query["priority"] = priority
    
    issues = find_many("ux_issues", query, limit=limit)
    serialized = [serialize_doc(i) for i in issues]
    
    return {
        "issues": serialized,
        "count": len(serialized),
        "filters": {
            "status": status,
            "priority": priority,
        }
    }


@router.get("/pending-review")
async def get_pending_review():
    """
    Get UX issues that are pending human review (status = 'diagnosed').
    """
    issues = find_many("ux_issues", {"status": "diagnosed"})
    serialized = [serialize_doc(i) for i in issues]
    
    return {
        "issues": serialized,
        "count": len(serialized),
    }


@router.get("/{issue_id}")
async def get_ux_issue(issue_id: str):
    """
    Get a specific UX issue by ID.
    """
    try:
        issue = find_by_id("ux_issues", issue_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid issue ID: {str(e)}")
    
    if not issue:
        raise HTTPException(status_code=404, detail="UX issue not found")
    
    return serialize_doc(issue)


@router.post("/{issue_id}/approve")
async def approve_issue(issue_id: str):
    """
    Approve a UX issue fix.
    
    This updates the issue status to 'approved', making it eligible
    for the Engineer agent to create a Pull Request.
    """
    try:
        issue = find_by_id("ux_issues", issue_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid issue ID: {str(e)}")
    
    if not issue:
        raise HTTPException(status_code=404, detail="UX issue not found")
    
    current_status = issue.get("status")
    if current_status not in ["diagnosed", "rejected"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot approve issue with status '{current_status}'. Only 'diagnosed' or 'rejected' issues can be approved."
        )
    
    update_by_id("ux_issues", issue_id, {
        "status": "approved",
        "approved_at": datetime.now().isoformat(),
    })
    
    return {
        "success": True,
        "message": f"Issue {issue_id} approved successfully",
        "previous_status": current_status,
        "new_status": "approved",
    }


@router.post("/{issue_id}/reject")
async def reject_issue(
    issue_id: str,
    reason: str = Body(default="", embed=True, description="Reason for rejection"),
):
    """
    Reject a UX issue fix.
    
    This updates the issue status to 'rejected' and stores the rejection reason.
    """
    try:
        issue = find_by_id("ux_issues", issue_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid issue ID: {str(e)}")
    
    if not issue:
        raise HTTPException(status_code=404, detail="UX issue not found")
    
    current_status = issue.get("status")
    
    update_by_id("ux_issues", issue_id, {
        "status": "rejected",
        "rejection_reason": reason,
        "rejected_at": datetime.now().isoformat(),
    })
    
    return {
        "success": True,
        "message": f"Issue {issue_id} rejected",
        "previous_status": current_status,
        "new_status": "rejected",
        "reason": reason,
    }


@router.get("/summary/by-status")
async def get_issues_by_status():
    """
    Get issue counts grouped by status.
    """
    issues = find_many("ux_issues", {})
    
    status_counts = {
        "diagnosed": 0,
        "approved": 0,
        "rejected": 0,
        "pr_created": 0,
    }
    
    for issue in issues:
        st = issue.get("status", "unknown")
        if st in status_counts:
            status_counts[st] += 1
        else:
            status_counts[st] = 1
    
    return {
        "by_status": status_counts,
        "total": sum(status_counts.values()),
    }
