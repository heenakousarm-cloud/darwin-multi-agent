"""
Darwin Multi-Agent System - Watcher Agent
==========================================
🕵️ The "Eyes" - Detects UX friction signals from PostHog analytics.
"""

from crewai import Agent, LLM

from src.tools import (
    PostHogQueryTool,
    PostHogRecordingsTool,
    MongoDBWriteTool,
    MongoDBReadTool,
)
from src.config.settings import get_settings


def get_gemini_llm() -> LLM:
    """Get configured Gemini LLM for CrewAI."""
    settings = get_settings()
    
    return LLM(
        model=f"gemini/{settings.GEMINI_MODEL}",
        api_key=settings.GEMINI_API_KEY,
    )


def create_watcher_agent(llm: LLM = None) -> Agent:
    """
    Create the Watcher Agent.
    
    Role: UX Friction Detector
    Goal: Monitor PostHog analytics and detect friction signals
    
    Tools:
    - PostHogQueryTool: Query for rage clicks, drop-offs, events
    - PostHogRecordingsTool: Fetch session recordings
    - MongoDBWriteTool: Save detected signals
    - MongoDBReadTool: Check existing signals
    """
    if llm is None:
        llm = get_gemini_llm()
    
    return Agent(
        role="UX Friction Detector",
        goal="""
        Monitor PostHog analytics to detect UX friction signals that indicate 
        users are struggling. Look for:
        - Rage clicks (users clicking repeatedly in frustration)
        - High drop-off rates on key pages
        - Error spikes
        - Slow page loads
        - Dead clicks on non-interactive elements
        
        When you find friction signals, save them to MongoDB with proper 
        classification (type, severity, affected users).
        """,
        backstory="""
        You are Darwin's eyes - a vigilant UX analyst who never sleeps.
        You've analyzed millions of user sessions and can spot patterns 
        that indicate frustration instantly.
        
        You understand that behind every rage click is a frustrated user 
        who might abandon the product. Your job is to catch these signals 
        early so they can be fixed before more users are affected.
        
        You work for a company that values user experience above all else.
        Every friction point you detect is an opportunity to improve.
        """,
        tools=[
            PostHogQueryTool(),
            PostHogRecordingsTool(),
            MongoDBWriteTool(),
            MongoDBReadTool(),
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=10,
    )


# Agent metadata for logging
WATCHER_METADATA = {
    "name": "Watcher",
    "emoji": "🕵️",
    "role": "UX Friction Detector",
    "description": "Monitors PostHog for rage clicks, drop-offs, and friction signals",
    "inputs": ["PostHog analytics data"],
    "outputs": ["Signals in MongoDB"],
}
