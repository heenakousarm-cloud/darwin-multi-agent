"""
Signals API Routes

Endpoints for managing UX friction signals.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from bson import ObjectId
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
    return doc


@router.get("/")
async def get_signals(
    severity: Optional[str] = Query(None, description="Filter by severity (critical, high, medium, low)"),
    processed: Optional[bool] = Query(None, description="Filter by processed status"),
    type: Optional[str] = Query(None, description="Filter by signal type (rage_click, drop_off, error_spike)"),
    limit: int = Query(50, description="Maximum number of results", ge=1, le=100),
):
    """
    Get all friction signals.
    
    Optionally filter by severity, processed status, or type.
    """
    query = {}
    
    if severity:
        query["severity"] = severity
    if processed is not None:
        query["processed"] = processed
    if type:
        query["type"] = type
    
    signals = find_many("signals", query, limit=limit)
    serialized = [serialize_doc(s) for s in signals]
    
    return {
        "signals": serialized,
        "count": len(serialized),
        "filters": {
            "severity": severity,
            "processed": processed,
            "type": type,
        }
    }


@router.get("/{signal_id}")
async def get_signal(signal_id: str):
    """
    Get a specific signal by ID.
    """
    try:
        signal = find_by_id("signals", signal_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid signal ID: {str(e)}")
    
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    return serialize_doc(signal)


@router.get("/summary/by-severity")
async def get_signals_by_severity():
    """
    Get signal counts grouped by severity.
    """
    signals = find_many("signals", {})
    
    severity_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }
    
    for signal in signals:
        sev = signal.get("severity", "unknown")
        if sev in severity_counts:
            severity_counts[sev] += 1
    
    return {
        "by_severity": severity_counts,
        "total": sum(severity_counts.values()),
    }


@router.get("/summary/by-type")
async def get_signals_by_type():
    """
    Get signal counts grouped by type.
    """
    signals = find_many("signals", {})
    
    type_counts = {}
    for signal in signals:
        signal_type = signal.get("type", "unknown")
        type_counts[signal_type] = type_counts.get(signal_type, 0) + 1
    
    return {
        "by_type": type_counts,
        "total": sum(type_counts.values()),
    }
