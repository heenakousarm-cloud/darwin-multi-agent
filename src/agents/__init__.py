"""
Darwin Multi-Agent System - Agents
==================================
CrewAI agents for the Darwin pipeline.
"""

from .watcher import (
    create_watcher_agent,
    get_gemini_llm,
    WATCHER_METADATA,
)

from .analyst import (
    create_analyst_agent,
    ANALYST_METADATA,
)

from .engineer import (
    create_engineer_agent,
    ENGINEER_METADATA,
)


__all__ = [
    # Agent creators
    "create_watcher_agent",
    "create_analyst_agent",
    "create_engineer_agent",
    # LLM
    "get_gemini_llm",
    # Metadata
    "WATCHER_METADATA",
    "ANALYST_METADATA",
    "ENGINEER_METADATA",
]


# All agent metadata for easy access
ALL_AGENTS_METADATA = {
    "watcher": WATCHER_METADATA,
    "analyst": ANALYST_METADATA,
    "engineer": ENGINEER_METADATA,
}
