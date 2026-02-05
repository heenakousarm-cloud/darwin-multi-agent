"""
Darwin Multi-Agent System - Tasks
=================================
CrewAI task definitions for the Darwin pipeline.
"""

from .all_tasks import (
    create_detect_signals_task,
    create_analyze_issues_task,
    create_fix_and_pr_task,
    TASK_METADATA,
)


__all__ = [
    "create_detect_signals_task",
    "create_analyze_issues_task",
    "create_fix_and_pr_task",
    "TASK_METADATA",
]
