"""
Darwin Multi-Agent System - MongoDB Tools
=========================================
Custom CrewAI tools for MongoDB operations.
"""

from typing import Type, Optional, List, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import json
from bson import ObjectId
from datetime import datetime

from src.db import (
    get_collection,
    insert_one,
    find_one,
    find_by_id,
    find_many,
    update_one,
    update_by_id,
    serialize_doc,
    serialize_docs,
)


class MongoDBReadInput(BaseModel):
    """Input schema for MongoDB read tool."""
    collection: str = Field(
        description="Collection name: 'signals', 'ux_issues', 'tasks', 'pull_requests', 'agent_logs'"
    )
    query: str = Field(
        default="{}",
        description="MongoDB query as JSON string (e.g., '{\"status\": \"new\"}')"
    )
    limit: int = Field(
        default=10,
        description="Maximum number of documents to return"
    )


class MongoDBReadTool(BaseTool):
    """
    Read documents from MongoDB collections.
    
    Used by: All Agents
    """
    
    name: str = "mongodb_read"
    description: str = """
    Read documents from MongoDB collections.
    Available collections:
    - signals: UX friction signals from PostHog
    - ux_issues: Diagnosed UX issues with fixes
    - tasks: Human-approved tasks
    - pull_requests: GitHub PRs created
    - agent_logs: Agent activity logs
    
    Provide a query as a JSON string to filter results.
    Example queries:
    - '{"status": "new"}' - Find new signals
    - '{"processed": false}' - Find unprocessed items
    - '{}' - Get all documents
    """
    args_schema: Type[BaseModel] = MongoDBReadInput
    
    def _run(
        self,
        collection: str,
        query: str = "{}",
        limit: int = 10
    ) -> str:
        """Read documents from MongoDB."""
        try:
            # Parse query
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                return f"Invalid JSON query: {query}"
            
            # Validate collection
            valid_collections = [
                'signals', 'ux_issues', 'tasks', 
                'pull_requests', 'agent_logs',
                'code_fixes', 'product_metrics', 'insights'
            ]
            if collection not in valid_collections:
                return f"Invalid collection: {collection}. Use one of: {valid_collections}"
            
            # Execute query
            docs = find_many(collection, query_dict, limit=limit)
            
            if not docs:
                return f"No documents found in '{collection}' matching query: {query}"
            
            # Format output
            output = f"## Found {len(docs)} document(s) in `{collection}`\n\n"
            
            for i, doc in enumerate(docs, 1):
                output += f"### Document {i}\n"
                output += f"```json\n{json.dumps(doc, indent=2, default=str)}\n```\n\n"
            
            return output
            
        except Exception as e:
            return f"Error reading from MongoDB: {str(e)}"


class MongoDBWriteInput(BaseModel):
    """Input schema for MongoDB write tool."""
    collection: str = Field(
        description="Collection name to write to"
    )
    document: str = Field(
        description="Document to insert as JSON string"
    )


class MongoDBWriteTool(BaseTool):
    """
    Write documents to MongoDB collections.
    
    Used by: All Agents
    """
    
    name: str = "mongodb_write"
    description: str = """
    Insert a new document into a MongoDB collection.
    Provide the collection name and document as a JSON string.
    Returns the inserted document ID on success.
    
    Example document for signals:
    '{
        "type": "rage_click",
        "severity": "high",
        "title": "Rage clicks on Add to Cart",
        "page": "/product/123",
        "affected_users": 50
    }'
    """
    args_schema: Type[BaseModel] = MongoDBWriteInput
    
    def _run(self, collection: str, document: str) -> str:
        """Write document to MongoDB."""
        try:
            # Parse document
            try:
                doc_dict = json.loads(document)
            except json.JSONDecodeError:
                return f"Invalid JSON document: {document[:100]}..."
            
            # Add timestamps
            now = datetime.utcnow()
            doc_dict['created_at'] = now.isoformat()
            doc_dict['updated_at'] = now.isoformat()
            
            # Insert
            doc_id = insert_one(collection, doc_dict)
            
            return f"✅ Document inserted successfully!\n\n**Collection:** {collection}\n**Document ID:** {doc_id}"
            
        except Exception as e:
            return f"Error writing to MongoDB: {str(e)}"


class MongoDBUpdateInput(BaseModel):
    """Input schema for MongoDB update tool."""
    collection: str = Field(
        description="Collection name"
    )
    doc_id: str = Field(
        description="Document ID to update"
    )
    updates: str = Field(
        description="Fields to update as JSON string (e.g., '{\"status\": \"processed\"}')"
    )


class MongoDBUpdateTool(BaseTool):
    """
    Update a document in MongoDB.
    
    Used by: All Agents
    """
    
    name: str = "mongodb_update"
    description: str = """
    Update an existing document in MongoDB by its ID.
    Provide the collection name, document ID, and fields to update as JSON.
    
    Example:
    - collection: 'signals'
    - doc_id: '507f1f77bcf86cd799439011'
    - updates: '{"status": "processed", "processed": true}'
    """
    args_schema: Type[BaseModel] = MongoDBUpdateInput
    
    def _run(self, collection: str, doc_id: str, updates: str) -> str:
        """Update document in MongoDB."""
        try:
            # Parse updates
            try:
                updates_dict = json.loads(updates)
            except json.JSONDecodeError:
                return f"Invalid JSON updates: {updates}"
            
            # Add updated timestamp
            updates_dict['updated_at'] = datetime.utcnow().isoformat()
            
            # Update
            success = update_by_id(collection, doc_id, updates_dict)
            
            if success:
                return f"✅ Document updated successfully!\n\n**Collection:** {collection}\n**Document ID:** {doc_id}\n**Updated fields:** {list(updates_dict.keys())}"
            else:
                return f"⚠️ Document not found or no changes made.\n\n**Collection:** {collection}\n**Document ID:** {doc_id}"
            
        except Exception as e:
            return f"Error updating MongoDB: {str(e)}"


class MongoDBFindByIdInput(BaseModel):
    """Input schema for MongoDB find by ID tool."""
    collection: str = Field(
        description="Collection name"
    )
    doc_id: str = Field(
        description="Document ID to find"
    )


class MongoDBFindByIdTool(BaseTool):
    """
    Find a single document by its ID.
    
    Used by: All Agents
    """
    
    name: str = "mongodb_find_by_id"
    description: str = """
    Find a single document in MongoDB by its ID.
    Returns the full document if found.
    """
    args_schema: Type[BaseModel] = MongoDBFindByIdInput
    
    def _run(self, collection: str, doc_id: str) -> str:
        """Find document by ID."""
        try:
            doc = find_by_id(collection, doc_id)
            
            if doc:
                return f"## Document Found\n\n**Collection:** {collection}\n\n```json\n{json.dumps(doc, indent=2, default=str)}\n```"
            else:
                return f"Document not found in '{collection}' with ID: {doc_id}"
            
        except Exception as e:
            return f"Error finding document: {str(e)}"


class MongoDBCountInput(BaseModel):
    """Input schema for MongoDB count tool."""
    collection: str = Field(
        description="Collection name"
    )
    query: str = Field(
        default="{}",
        description="Query to filter documents"
    )


class MongoDBCountTool(BaseTool):
    """
    Count documents in a collection.
    
    Used by: All Agents
    """
    
    name: str = "mongodb_count"
    description: str = """
    Count documents in a MongoDB collection.
    Optionally provide a query to count matching documents.
    """
    args_schema: Type[BaseModel] = MongoDBCountInput
    
    def _run(self, collection: str, query: str = "{}") -> str:
        """Count documents."""
        try:
            try:
                query_dict = json.loads(query)
            except json.JSONDecodeError:
                return f"Invalid JSON query: {query}"
            
            col = get_collection(collection)
            count = col.count_documents(query_dict)
            
            return f"**{collection}**: {count} document(s) matching query"
            
        except Exception as e:
            return f"Error counting documents: {str(e)}"


# Convenience tool for getting unprocessed signals
class GetUnprocessedSignalsInput(BaseModel):
    """Input schema for getting unprocessed signals."""
    limit: int = Field(
        default=10,
        description="Maximum number of signals to return"
    )


class GetUnprocessedSignalsTool(BaseTool):
    """
    Get unprocessed signals for analysis.
    
    Used by: Watcher Agent → Analyst Agent handoff
    """
    
    name: str = "get_unprocessed_signals"
    description: str = """
    Get signals that haven't been processed yet.
    These are new friction signals detected by the Watcher that need analysis.
    Returns signals sorted by severity (critical first).
    """
    args_schema: Type[BaseModel] = GetUnprocessedSignalsInput
    
    def _run(self, limit: int = 10) -> str:
        """Get unprocessed signals."""
        try:
            docs = find_many(
                "signals",
                {"processed": False},
                limit=limit,
                sort=[("severity", -1), ("created_at", 1)]
            )
            
            if not docs:
                return "No unprocessed signals found. The Watcher needs to detect new signals first."
            
            output = f"## {len(docs)} Unprocessed Signal(s)\n\n"
            
            for doc in docs:
                output += f"### {doc.get('title', 'Untitled')}\n"
                output += f"- **ID:** {doc.get('_id')}\n"
                output += f"- **Type:** {doc.get('type')}\n"
                output += f"- **Severity:** {doc.get('severity')}\n"
                output += f"- **Page:** {doc.get('page')}\n"
                output += f"- **Affected Users:** {doc.get('affected_users', 0)}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error getting signals: {str(e)}"


# Convenience tool for getting pending tasks
class GetPendingTasksInput(BaseModel):
    """Input schema for getting pending tasks."""
    limit: int = Field(
        default=10,
        description="Maximum number of tasks to return"
    )


class GetPendingTasksTool(BaseTool):
    """
    Get pending tasks for the Engineer to work on.
    
    Used by: Engineer Agent
    """
    
    name: str = "get_pending_tasks"
    description: str = """
    Get tasks that are pending execution.
    These are human-approved tasks ready for the Engineer to implement.
    Returns tasks sorted by priority (urgent first).
    """
    args_schema: Type[BaseModel] = GetPendingTasksInput
    
    def _run(self, limit: int = 10) -> str:
        """Get pending tasks."""
        try:
            docs = find_many(
                "tasks",
                {"status": "pending"},
                limit=limit,
                sort=[("priority", -1), ("created_at", 1)]
            )
            
            if not docs:
                return "No pending tasks found. Tasks need to be approved via NitroStack first."
            
            output = f"## {len(docs)} Pending Task(s)\n\n"
            
            for doc in docs:
                output += f"### {doc.get('title', 'Untitled')}\n"
                output += f"- **ID:** {doc.get('_id')}\n"
                output += f"- **Priority:** {doc.get('priority')}\n"
                output += f"- **File:** {doc.get('file_path')}\n"
                output += f"- **UX Issue ID:** {doc.get('ux_issue_id')}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error getting tasks: {str(e)}"
