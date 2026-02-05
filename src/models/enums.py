"""
Darwin Multi-Agent System - Enums & Constants
==============================================
Centralized enum definitions for type safety across the system.
"""

from enum import Enum


class SignalType(str, Enum):
    """Types of UX friction signals detected by Watcher."""
    
    RAGE_CLICK = "rage_click"
    DROP_OFF = "drop_off"
    ERROR_SPIKE = "error_spike"
    SLOW_LOAD = "slow_load"
    DEAD_CLICK = "dead_click"
    FORM_ABANDONMENT = "form_abandonment"
    SCROLL_BOUNCE = "scroll_bounce"
    
    def __str__(self) -> str:
        return self.value


class Severity(str, Enum):
    """Severity levels for signals and issues."""
    
    CRITICAL = "critical"    # Immediate attention required
    HIGH = "high"            # Should fix soon
    MEDIUM = "medium"        # Plan to fix
    LOW = "low"              # Nice to have
    
    def __str__(self) -> str:
        return self.value


class SignalStatus(str, Enum):
    """Processing status of a signal."""
    
    NEW = "new"                      # Just detected
    PROCESSING = "processing"        # Being analyzed
    ANALYZED = "analyzed"            # Analysis complete
    ISSUE_CREATED = "issue_created"  # UX Issue created
    DISMISSED = "dismissed"          # Marked as not actionable
    
    def __str__(self) -> str:
        return self.value


class UXIssueStatus(str, Enum):
    """Status of a UX Issue through the pipeline."""
    
    DETECTED = "detected"            # Initial detection
    ANALYZING = "analyzing"          # Root cause analysis in progress
    DIAGNOSED = "diagnosed"          # Root cause identified
    FIX_PROPOSED = "fix_proposed"    # Code fix recommended
    TASK_CREATED = "task_created"    # Human approved, task created
    IN_PROGRESS = "in_progress"      # Engineer agent working
    PR_CREATED = "pr_created"        # Pull request opened
    PR_MERGED = "pr_merged"          # Fix deployed
    RESOLVED = "resolved"            # Verified fixed
    WONT_FIX = "wont_fix"            # Marked as won't fix
    
    def __str__(self) -> str:
        return self.value


class TaskPriority(str, Enum):
    """Priority levels for tasks."""
    
    URGENT = "urgent"        # P0 - Do immediately
    HIGH = "high"            # P1 - This sprint
    MEDIUM = "medium"        # P2 - Next sprint
    LOW = "low"              # P3 - Backlog
    
    def __str__(self) -> str:
        return self.value


class TaskStatus(str, Enum):
    """Status of a task."""
    
    PENDING = "pending"              # Waiting to start
    IN_PROGRESS = "in_progress"      # Being worked on
    COMPLETED = "completed"          # Done
    CANCELLED = "cancelled"          # Cancelled
    
    def __str__(self) -> str:
        return self.value


class PRStatus(str, Enum):
    """Status of a Pull Request."""
    
    DRAFT = "draft"                  # Draft PR
    OPEN = "open"                    # Open for review
    REVIEW_REQUESTED = "review_requested"
    CHANGES_REQUESTED = "changes_requested"
    APPROVED = "approved"            # Approved
    MERGED = "merged"                # Merged
    CLOSED = "closed"                # Closed without merge
    
    def __str__(self) -> str:
        return self.value


class AgentType(str, Enum):
    """Types of Darwin agents."""
    
    WATCHER = "watcher"      # 🕵️ Eyes - Detects signals
    ANALYST = "analyst"      # 🧠 Brain - Diagnoses issues
    ENGINEER = "engineer"    # 👩‍💻 Hands - Creates fixes
    
    def __str__(self) -> str:
        return self.value


class LogLevel(str, Enum):
    """Log levels for agent activity."""
    
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
    def __str__(self) -> str:
        return self.value


# ===================
# Constants
# ===================

# Severity thresholds
SEVERITY_THRESHOLDS = {
    "rage_click_count": {
        Severity.CRITICAL: 50,
        Severity.HIGH: 20,
        Severity.MEDIUM: 10,
        Severity.LOW: 5,
    },
    "drop_off_rate": {
        Severity.CRITICAL: 0.5,   # 50%+
        Severity.HIGH: 0.3,       # 30%+
        Severity.MEDIUM: 0.2,     # 20%+
        Severity.LOW: 0.1,        # 10%+
    }
}

# Confidence thresholds
CONFIDENCE_THRESHOLDS = {
    "high": 0.8,
    "medium": 0.6,
    "low": 0.4,
}
