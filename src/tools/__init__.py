"""
Darwin Multi-Agent System - Custom Tools
========================================
CrewAI tools for PostHog, GitHub, and MongoDB operations.
"""

from .posthog_tools import (
    PostHogQueryTool,
    PostHogRecordingsTool,
)

from .github_tools import (
    GitHubReadTool,
    GitHubPRTool,
    GitHubCheckBranchTool,
    GitHubListFilesTool,
)

from .mongodb_tools import (
    MongoDBReadTool,
    MongoDBWriteTool,
    MongoDBUpdateTool,
    MongoDBFindByIdTool,
    MongoDBCountTool,
    GetUnprocessedSignalsTool,
    GetPendingTasksTool,
)


__all__ = [
    # PostHog Tools
    "PostHogQueryTool",
    "PostHogRecordingsTool",
    # GitHub Tools
    "GitHubReadTool",
    "GitHubPRTool",
    "GitHubCheckBranchTool",
    "GitHubListFilesTool",
    # MongoDB Tools
    "MongoDBReadTool",
    "MongoDBWriteTool",
    "MongoDBUpdateTool",
    "MongoDBFindByIdTool",
    "MongoDBCountTool",
    "GetUnprocessedSignalsTool",
    "GetPendingTasksTool",
]


# Tool groups for agents
WATCHER_TOOLS = [
    PostHogQueryTool(),
    PostHogRecordingsTool(),
    MongoDBWriteTool(),
    MongoDBReadTool(),
]

ANALYST_TOOLS = [
    GitHubReadTool(),
    GitHubListFilesTool(),
    MongoDBReadTool(),
    MongoDBWriteTool(),
    MongoDBUpdateTool(),
    GetUnprocessedSignalsTool(),
]

ENGINEER_TOOLS = [
    GitHubReadTool(),
    GitHubPRTool(),
    GitHubListFilesTool(),
    MongoDBReadTool(),
    MongoDBWriteTool(),
    MongoDBUpdateTool(),
    GetPendingTasksTool(),
]
