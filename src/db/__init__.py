"""
Darwin Multi-Agent System - Database Layer
==========================================
MongoDB client and helpers.
"""

from .mongodb import (
    # Connection
    get_client,
    get_database,
    get_collection,
    test_connection,
    get_stats,
    # Collection shortcuts
    signals_collection,
    ux_issues_collection,
    tasks_collection,
    pull_requests_collection,
    agent_logs_collection,
    code_fixes_collection,
    insights_collection,
    product_metrics_collection,
    # Serialization
    serialize_doc,
    serialize_docs,
    to_object_id,
    # CRUD
    insert_one,
    find_one,
    find_by_id,
    find_many,
    update_one,
    update_by_id,
    delete_one,
    delete_by_id,
    count,
    # Specialized queries
    get_unprocessed_signals,
    get_pending_tasks,
    get_issues_for_review,
    # Logging functions
    log_agent_action,
    save_code_fix,
    save_insight,
    save_product_metric,
    create_task,
)

__all__ = [
    "get_client",
    "get_database",
    "get_collection",
    "test_connection",
    "get_stats",
    "signals_collection",
    "ux_issues_collection",
    "tasks_collection",
    "pull_requests_collection",
    "agent_logs_collection",
    "code_fixes_collection",
    "insights_collection",
    "product_metrics_collection",
    "serialize_doc",
    "serialize_docs",
    "to_object_id",
    "insert_one",
    "find_one",
    "find_by_id",
    "find_many",
    "update_one",
    "update_by_id",
    "delete_one",
    "delete_by_id",
    "count",
    "get_unprocessed_signals",
    "get_pending_tasks",
    "get_issues_for_review",
    "log_agent_action",
    "save_code_fix",
    "save_insight",
    "save_product_metric",
    "create_task",
]
