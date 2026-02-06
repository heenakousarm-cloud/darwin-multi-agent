"""
Darwin Multi-Agent System - MongoDB Client
==========================================
Centralized MongoDB connection and collection access.
"""

from typing import Optional, List, Dict, Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from bson import ObjectId

from src.config.settings import get_settings


# Global client instance
_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_client() -> MongoClient:
    """Get or create MongoDB client."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = MongoClient(settings.MONGODB_URI)
    return _client


def get_database() -> Database:
    """Get the Darwin database."""
    global _db
    if _db is None:
        settings = get_settings()
        _db = get_client()[settings.MONGODB_DATABASE]
    return _db


def get_collection(name: str) -> Collection:
    """Get a collection by name."""
    return get_database()[name]


# ===================
# Collection Shortcuts
# ===================

def signals_collection() -> Collection:
    """Get the signals collection."""
    return get_collection("signals")


def ux_issues_collection() -> Collection:
    """Get the ux_issues collection."""
    return get_collection("ux_issues")


def tasks_collection() -> Collection:
    """Get the tasks collection."""
    return get_collection("tasks")


def pull_requests_collection() -> Collection:
    """Get the pull_requests collection."""
    return get_collection("pull_requests")


def agent_logs_collection() -> Collection:
    """Get the agent_logs collection."""
    return get_collection("agent_logs")


def code_fixes_collection() -> Collection:
    """Get the code_fixes collection."""
    return get_collection("code_fixes")


def insights_collection() -> Collection:
    """Get the insights collection."""
    return get_collection("insights")


def product_metrics_collection() -> Collection:
    """Get the product_metrics collection."""
    return get_collection("product_metrics")


# ===================
# Helper Functions
# ===================

def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB document for JSON serialization."""
    if doc is None:
        return None
    
    result = dict(doc)
    if "_id" in result:
        result["_id"] = str(result["_id"])
    return result


def serialize_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert multiple MongoDB documents for JSON serialization."""
    return [serialize_doc(doc) for doc in docs]


def to_object_id(id_str: str) -> ObjectId:
    """Convert string to ObjectId."""
    return ObjectId(id_str)


# ===================
# CRUD Operations
# ===================

def insert_one(collection_name: str, document: Dict[str, Any]) -> str:
    """Insert a document and return its ID."""
    collection = get_collection(collection_name)
    result = collection.insert_one(document)
    return str(result.inserted_id)


def find_one(collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Find a single document."""
    collection = get_collection(collection_name)
    doc = collection.find_one(query)
    return serialize_doc(doc) if doc else None


def find_by_id(collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
    """Find a document by its ID."""
    return find_one(collection_name, {"_id": ObjectId(doc_id)})


def find_many(
    collection_name: str,
    query: Dict[str, Any],
    limit: int = 100,
    sort: Optional[List[tuple]] = None
) -> List[Dict[str, Any]]:
    """Find multiple documents."""
    collection = get_collection(collection_name)
    cursor = collection.find(query)
    
    if sort:
        cursor = cursor.sort(sort)
    
    cursor = cursor.limit(limit)
    return serialize_docs(list(cursor))


def update_one(
    collection_name: str,
    query: Dict[str, Any],
    update: Dict[str, Any],
    upsert: bool = False
) -> bool:
    """Update a single document."""
    collection = get_collection(collection_name)
    result = collection.update_one(query, {"$set": update}, upsert=upsert)
    return result.modified_count > 0 or result.upserted_id is not None


def update_by_id(collection_name: str, doc_id: str, update: Dict[str, Any]) -> bool:
    """Update a document by its ID."""
    return update_one(collection_name, {"_id": ObjectId(doc_id)}, update)


def delete_one(collection_name: str, query: Dict[str, Any]) -> bool:
    """Delete a single document."""
    collection = get_collection(collection_name)
    result = collection.delete_one(query)
    return result.deleted_count > 0


def delete_by_id(collection_name: str, doc_id: str) -> bool:
    """Delete a document by its ID."""
    return delete_one(collection_name, {"_id": ObjectId(doc_id)})


def count(collection_name: str, query: Dict[str, Any] = None) -> int:
    """Count documents matching a query."""
    collection = get_collection(collection_name)
    return collection.count_documents(query or {})


# ===================
# Specialized Queries
# ===================

def get_unprocessed_signals(limit: int = 10) -> List[Dict[str, Any]]:
    """Get signals that haven't been processed yet."""
    return find_many(
        "signals",
        {"processed": False, "status": "new"},
        limit=limit,
        sort=[("severity", -1), ("created_at", 1)]
    )


def get_pending_tasks(limit: int = 10) -> List[Dict[str, Any]]:
    """Get tasks that are pending execution."""
    return find_many(
        "tasks",
        {"status": "pending"},
        limit=limit,
        sort=[("priority", -1), ("created_at", 1)]
    )


def get_issues_for_review(limit: int = 10) -> List[Dict[str, Any]]:
    """Get UX issues that need human review."""
    return find_many(
        "ux_issues",
        {"status": {"$in": ["diagnosed", "fix_proposed"]}},
        limit=limit,
        sort=[("priority", -1), ("created_at", 1)]
    )


# ===================
# Connection Test
# ===================

def test_connection() -> bool:
    """Test the MongoDB connection."""
    try:
        client = get_client()
        client.admin.command('ping')
        return True
    except Exception:
        return False


def get_stats() -> Dict[str, Any]:
    """Get database statistics."""
    db = get_database()
    collections = db.list_collection_names()
    
    stats = {
        "database": db.name,
        "collections": {},
        "total_documents": 0
    }
    
    for col_name in collections:
        col_count = db[col_name].count_documents({})
        stats["collections"][col_name] = col_count
        stats["total_documents"] += col_count
    
    return stats


# ===================
# Logging Functions
# ===================

def log_agent_action(
    agent_name: str,
    action: str,
    details: Dict[str, Any],
    status: str = "success"
) -> str:
    """Log an agent action to agent_logs collection."""
    from datetime import datetime
    
    log_entry = {
        "agent": agent_name,
        "action": action,
        "details": details,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
    }
    return insert_one("agent_logs", log_entry)


def save_code_fix(
    issue_id: str,
    file_path: str,
    original_code: str,
    fixed_code: str,
    fix_type: str,
    pr_number: Optional[int] = None
) -> str:
    """Save a code fix to code_fixes collection."""
    from datetime import datetime
    
    fix_entry = {
        "issue_id": issue_id,
        "file_path": file_path,
        "original_code": original_code,
        "fixed_code": fixed_code,
        "fix_type": fix_type,
        "pr_number": pr_number,
        "applied_at": datetime.utcnow().isoformat(),
        "status": "applied" if pr_number else "pending"
    }
    return insert_one("code_fixes", fix_entry)


def save_insight(
    insight_type: str,
    title: str,
    description: str,
    data: Dict[str, Any],
    severity: str = "info"
) -> str:
    """Save an insight to insights collection."""
    from datetime import datetime
    
    insight_entry = {
        "type": insight_type,
        "title": title,
        "description": description,
        "data": data,
        "severity": severity,
        "created_at": datetime.utcnow().isoformat(),
    }
    return insert_one("insights", insight_entry)


def save_product_metric(
    metric_name: str,
    value: float,
    unit: str,
    dimensions: Dict[str, Any] = None
) -> str:
    """Save a product metric to product_metrics collection."""
    from datetime import datetime
    
    metric_entry = {
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        "dimensions": dimensions or {},
        "recorded_at": datetime.utcnow().isoformat(),
    }
    return insert_one("product_metrics", metric_entry)


def create_task(
    task_type: str,
    title: str,
    description: str,
    priority: str = "medium",
    assigned_agent: str = None,
    related_issue_id: str = None
) -> str:
    """Create a task in tasks collection."""
    from datetime import datetime
    
    task_entry = {
        "type": task_type,
        "title": title,
        "description": description,
        "priority": priority,
        "assigned_agent": assigned_agent,
        "related_issue_id": related_issue_id,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    return insert_one("tasks", task_entry)
