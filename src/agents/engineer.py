"""
Darwin Multi-Agent System - Engineer Agent
==========================================
👩‍💻 The "Hands" - Generates code fixes and creates Pull Requests.
"""

from crewai import Agent, LLM

from src.tools import (
    GitHubReadTool,
    GitHubPRTool,
    GitHubListFilesTool,
    MongoDBReadTool,
    MongoDBWriteTool,
    MongoDBUpdateTool,
    GetPendingTasksTool,
)
from src.config.settings import get_settings


def get_gemini_llm() -> LLM:
    """Get configured Gemini LLM for CrewAI."""
    settings = get_settings()
    
    return LLM(
        model=f"gemini/{settings.GEMINI_MODEL}",
        api_key=settings.GEMINI_API_KEY,
    )


def create_engineer_agent(llm: LLM = None) -> Agent:
    """
    Create the Engineer Agent.
    
    Role: Autonomous Code Fixer
    Goal: Generate code fixes and create GitHub Pull Requests
    
    Tools:
    - GitHubReadTool: Read current file contents
    - GitHubPRTool: Create branches and PRs
    - GitHubListFilesTool: Explore codebase
    - MongoDBReadTool: Read tasks and issues
    - MongoDBWriteTool: Save PR records
    - MongoDBUpdateTool: Update task/issue status
    - GetPendingTasksTool: Get tasks to work on
    """
    if llm is None:
        llm = get_gemini_llm()
    
    return Agent(
        role="Autonomous Code Fixer",
        goal="""
        Implement code fixes and create GitHub Pull Requests. For each task:
        
        1. Read the pending task from MongoDB
        2. Read the current file content from GitHub
        3. Apply the recommended fix to the code
        4. Ensure the fix is syntactically correct
        5. Create a GitHub Pull Request with:
           - Clear title prefixed with "🧬 Darwin Fix:"
           - Detailed description explaining the issue and fix
           - Proper branch naming (darwin/fix-description-timestamp)
        6. Save the PR details to MongoDB
        7. Update the task and UX issue status to "pr_created"
        
        Your code changes must be precise and maintain the existing code style.
        Do not introduce any new issues or break existing functionality.
        """,
        backstory="""
        You are Darwin's hands - a senior React Native engineer who writes 
        clean, production-ready code. You've shipped code to millions of users.
        
        You follow these coding principles:
        - Match the existing code style exactly
        - Make minimal changes to fix the issue
        - Preserve all existing functionality
        - Add comments only when necessary
        - Follow React Native best practices
        
        When creating PRs, you write clear descriptions that help reviewers 
        understand what changed and why. You include:
        - Summary of the issue
        - Root cause explanation
        - Description of the fix
        - Impact on users
        
        You never guess - if you're unsure about something, you read the 
        code first. Your PRs are always ready for review.
        """,
        tools=[
            GitHubReadTool(),
            GitHubPRTool(),
            GitHubListFilesTool(),
            MongoDBReadTool(),
            MongoDBWriteTool(),
            MongoDBUpdateTool(),
            GetPendingTasksTool(),
        ],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=15,
    )


# Agent metadata for logging
ENGINEER_METADATA = {
    "name": "Engineer",
    "emoji": "👩‍💻",
    "role": "Autonomous Code Fixer",
    "description": "Generates code fixes and creates GitHub Pull Requests",
    "inputs": ["Tasks from MongoDB", "Source code from GitHub"],
    "outputs": ["GitHub Pull Requests"],
}
