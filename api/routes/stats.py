"""
Statistics API Routes

Endpoints for getting dashboard statistics and insights.
"""

from fastapi import APIRouter
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.db import find_many, get_stats as db_get_stats

router = APIRouter()


def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable format."""
    if doc is None:
        return None
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    for key, value in doc.items():
        if isinstance(value, datetime):
            doc[key] = value.isoformat()
    return doc


@router.get("/")
async def get_stats():
    """
    Get overall statistics for the Darwin dashboard.
    
    Returns counts for all collections and key metrics.
    """
    stats = db_get_stats()
    
    # Get additional breakdowns
    signals = find_many("signals", {})
    ux_issues = find_many("ux_issues", {})
    prs = find_many("pull_requests", {})
    
    # Signal severity breakdown
    signal_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for s in signals:
        sev = s.get("severity", "unknown")
        if sev in signal_severity:
            signal_severity[sev] += 1
    
    # Issue status breakdown
    issue_status = {"diagnosed": 0, "approved": 0, "rejected": 0, "pr_created": 0}
    for i in ux_issues:
        st = i.get("status", "unknown")
        if st in issue_status:
            issue_status[st] += 1
    
    # PR status breakdown
    pr_status = {"open": 0, "merged": 0, "closed": 0}
    for p in prs:
        st = p.get("status", "unknown")
        if st in pr_status:
            pr_status[st] += 1
    
    return {
        "database": stats.get("database"),
        "totals": {
            "signals": stats.get("collections", {}).get("signals", 0),
            "ux_issues": stats.get("collections", {}).get("ux_issues", 0),
            "pull_requests": stats.get("collections", {}).get("pull_requests", 0),
            "agent_logs": stats.get("collections", {}).get("agent_logs", 0),
            "insights": stats.get("collections", {}).get("insights", 0),
            "product_metrics": stats.get("collections", {}).get("product_metrics", 0),
            "tasks": stats.get("collections", {}).get("tasks", 0),
            "code_fixes": stats.get("collections", {}).get("code_fixes", 0),
        },
        "breakdowns": {
            "signals_by_severity": signal_severity,
            "issues_by_status": issue_status,
            "prs_by_status": pr_status,
        },
        "pending_actions": {
            "signals_unprocessed": len([s for s in signals if not s.get("processed", False)]),
            "issues_pending_review": issue_status.get("diagnosed", 0),
            "issues_approved_pending_pr": issue_status.get("approved", 0),
        },
    }


@router.get("/insights")
async def get_insights():
    """
    Get AI-generated insights from Darwin.
    """
    insights = find_many("insights", {}, limit=20)
    serialized = [serialize_doc(i) for i in insights]
    
    return {
        "insights": serialized,
        "count": len(serialized),
    }


@router.get("/agent-logs")
async def get_agent_logs(limit: int = 50):
    """
    Get recent agent activity logs.
    """
    logs = find_many("agent_logs", {}, limit=limit)
    serialized = [serialize_doc(log) for log in logs]
    
    return {
        "logs": serialized,
        "count": len(serialized),
    }


@router.get("/product-metrics")
async def get_product_metrics():
    """
    Get product metrics tracked by Darwin.
    """
    metrics = find_many("product_metrics", {}, limit=50)
    serialized = [serialize_doc(m) for m in metrics]
    
    return {
        "metrics": serialized,
        "count": len(serialized),
    }
