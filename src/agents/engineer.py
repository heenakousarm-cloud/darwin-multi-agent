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
        Implement code fixes and create GitHub Pull Requests using PATCH approach.
        
        IMPORTANT: Use the PATCH-BASED PR tool - you do NOT need to output full files!
        
        For each task:
        1. Read ONE issue from MongoDB (approved or diagnosed status)
        2. Extract original_code and suggested_code from the issue's recommended_fix
        3. Create a GitHub Pull Request using github_create_pr with:
           - title: "🧬 Darwin Fix: [Issue Title]"
           - body: Markdown description of the fix
           - file_path: The file to modify
           - original_code: EXACTLY as shown in recommended_fix
           - suggested_code: EXACTLY as shown in recommended_fix
        4. The tool will handle reading the file and applying the patch!
        5. Save the PR details to MongoDB
        6. Update the UX issue status to "pr_created"
        
        KEY: You don't need to read or output the full file - just pass the patch!
        """,
        backstory="""
        You are Darwin's hands - a senior React Native engineer who creates 
        precise, targeted code fixes via Pull Requests.
        
        Your workflow is PATCH-BASED:
        - You receive issues with recommended_fix containing original_code and suggested_code
        - You pass these EXACTLY to the github_create_pr tool
        - The tool handles file reading and patch application
        - You do NOT need to read or output full file contents!
        
        When creating PRs:
        - Copy original_code and suggested_code EXACTLY from the issue
        - Write clear PR descriptions explaining the fix
        - Always update MongoDB after PR creation
        
        You are efficient - you don't read files unnecessarily since the 
        PR tool handles that internally. Just extract the fix details 
        from the issue and create the PR.
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
