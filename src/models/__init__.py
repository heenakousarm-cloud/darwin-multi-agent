"""
Darwin Multi-Agent System - Data Models
=======================================
Pydantic models for type-safe data handling.
"""

from .enums import (
    SignalType,
    Severity,
    SignalStatus,
    UXIssueStatus,
    TaskPriority,
    TaskStatus,
    PRStatus,
    AgentType,
    LogLevel,
    SEVERITY_THRESHOLDS,
    CONFIDENCE_THRESHOLDS,
)

from .signal import Signal
from .ux_issue import UXIssue, RecommendedFix
from .task import Task
from .pull_request import PullRequest, FileChange


__all__ = [
    # Enums
    "SignalType",
    "Severity",
    "SignalStatus",
    "UXIssueStatus",
    "TaskPriority",
    "TaskStatus",
    "PRStatus",
    "AgentType",
    "LogLevel",
    # Constants
    "SEVERITY_THRESHOLDS",
    "CONFIDENCE_THRESHOLDS",
    # Models
    "Signal",
    "UXIssue",
    "RecommendedFix",
    "Task",
    "PullRequest",
    "FileChange",
]
