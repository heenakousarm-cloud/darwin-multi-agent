"""
Darwin Multi-Agent System - Analyst Agent
==========================================
🧠 The "Brain" - Diagnoses root causes and recommends fixes.
"""

from crewai import Agent, LLM

from src.tools import (
    GitHubReadTool,
    GitHubListFilesTool,
    MongoDBReadTool,
    MongoDBWriteTool,
    MongoDBUpdateTool,
    GetUnprocessedSignalsTool,
)
from src.config.settings import get_settings


def get_gemini_llm() -> LLM:
    """Get configured Gemini LLM for CrewAI."""
    settings = get_settings()
    
    return LLM(
        model=f"gemini/{settings.GEMINI_MODEL}",
        api_key=settings.GEMINI_API_KEY,
    )


def create_analyst_agent(llm: LLM = None) -> Agent:
    """
    Create the Analyst Agent.
    
    Role: UX Root Cause Analyst
    Goal: Diagnose root causes and recommend specific code fixes
    
    Tools:
    - GitHubReadTool: Read source code files
    - GitHubListFilesTool: Explore codebase structure
    - MongoDBReadTool: Read signals and issues
    - MongoDBWriteTool: Create UX issues
    - MongoDBUpdateTool: Update signal status
    - GetUnprocessedSignalsTool: Get signals needing analysis
    """
    if llm is None:
        llm = get_gemini_llm()
    
    return Agent(
        role="UX Root Cause Analyst",
        goal="""
        Analyze UX friction signals to identify root causes and recommend 
        specific code fixes. For each signal:
        
        1. Read the signal details from MongoDB
        2. Identify which file/component is likely causing the issue
        3. Read the relevant source code from GitHub
        4. Diagnose the root cause (e.g., small touch target, missing feedback)
        5. Recommend a specific code fix with exact changes needed
        6. Create a UX Issue in MongoDB with full analysis
        7. Mark the original signal as processed
        
        Your recommendations must be specific enough for an engineer to 
        implement without guessing - include file paths, line numbers, 
        and exact code changes.
        """,
        backstory="""
        You are Darwin's brain - a senior UX engineer with deep expertise 
        in React Native, mobile UX patterns, and accessibility guidelines.
        
        You've debugged thousands of UX issues and can quickly trace a 
        symptom (like rage clicks) back to its root cause in the code.
        
        You follow these principles:
        - Touch targets should be at least 44x44 points (iOS) / 48x48 dp (Android)
        - Buttons need visual feedback on press
        - Loading states should be communicated clearly
        - Error messages should be helpful and actionable
        
        When you recommend a fix, you provide the exact code changes needed,
        not vague suggestions. You think like both a UX designer and a 
        frontend engineer.
        """,
        tools=[
            GitHubReadTool(),
            GitHubListFilesTool(),
            MongoDBReadTool(),
            MongoDBWriteTool(),
            MongoDBUpdateTool(),
            GetUnprocessedSignalsTool(),
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=15,
    )


# Agent metadata for logging
ANALYST_METADATA = {
    "name": "Analyst",
    "emoji": "🧠",
    "role": "UX Root Cause Analyst",
    "description": "Diagnoses root causes and recommends specific code fixes",
    "inputs": ["Signals from MongoDB", "Source code from GitHub"],
    "outputs": ["UX Issues with fix recommendations"],
}
