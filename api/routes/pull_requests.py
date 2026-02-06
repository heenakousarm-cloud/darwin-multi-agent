"""
Pull Requests API Routes

Endpoints for managing GitHub Pull Requests created by Darwin.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.db import find_many, find_by_id

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
async def get_pull_requests(
    status: Optional[str] = Query(None, description="Filter by status (open, merged, closed)"),
    limit: int = Query(50, description="Maximum number of results", ge=1, le=100),
):
    """
    Get all Pull Requests created by Darwin.
    
    Optionally filter by status.
    """
    query = {}
    
    if status:
        query["status"] = status
    
    prs = find_many("pull_requests", query, limit=limit)
    serialized = [serialize_doc(pr) for pr in prs]
    
    return {
        "pull_requests": serialized,
        "count": len(serialized),
        "filters": {
            "status": status,
        }
    }


@router.get("/{pr_id}")
async def get_pull_request(pr_id: str):
    """
    Get a specific Pull Request by ID.
    """
    try:
        pr = find_by_id("pull_requests", pr_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid PR ID: {str(e)}")
    
    if not pr:
        raise HTTPException(status_code=404, detail="Pull Request not found")
    
    return serialize_doc(pr)


@router.get("/summary/stats")
async def get_pr_stats():
    """
    Get Pull Request statistics.
    """
    prs = find_many("pull_requests", {})
    
    status_counts = {
        "open": 0,
        "merged": 0,
        "closed": 0,
    }
    
    for pr in prs:
        st = pr.get("status", "unknown")
        if st in status_counts:
            status_counts[st] += 1
        else:
            status_counts[st] = 1
    
    return {
        "by_status": status_counts,
        "total": sum(status_counts.values()),
    }
