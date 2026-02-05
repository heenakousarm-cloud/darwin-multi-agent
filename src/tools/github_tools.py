"""
Darwin Multi-Agent System - GitHub Tools
========================================
Custom CrewAI tools for GitHub operations.
"""

from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from github import Github, Auth
from github.GithubException import GithubException
import base64

from src.config.settings import get_settings


class GitHubReadInput(BaseModel):
    """Input schema for GitHub read tool."""
    file_path: str = Field(
        description="Path to the file in the repository (e.g., 'app/product/[id].tsx')"
    )
    branch: str = Field(
        default="main",
        description="Branch to read from"
    )


class GitHubReadTool(BaseTool):
    """
    Read file contents from a GitHub repository.
    
    Used by: Analyst Agent, Engineer Agent
    """
    
    name: str = "github_read_file"
    description: str = """
    Read the contents of a file from the GitHub repository.
    Use this to examine source code that may be causing UX issues.
    Provide the file path relative to the repository root.
    Returns the file contents as a string.
    """
    args_schema: Type[BaseModel] = GitHubReadInput
    
    def _run(self, file_path: str, branch: str = "main") -> str:
        """Read file from GitHub."""
        settings = get_settings()
        
        try:
            auth = Auth.Token(settings.GITHUB_TOKEN)
            g = Github(auth=auth)
            
            repo = g.get_repo(f"{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}")
            
            try:
                file_content = repo.get_contents(file_path, ref=branch)
                
                if isinstance(file_content, list):
                    return f"Error: '{file_path}' is a directory, not a file."
                
                # Decode content
                content = base64.b64decode(file_content.content).decode('utf-8')
                
                # Add line numbers for reference
                lines = content.split('\n')
                numbered_content = '\n'.join(
                    f"{i+1:4d} | {line}" for i, line in enumerate(lines)
                )
                
                return f"## File: {file_path}\n\n```\n{numbered_content}\n```\n\n*{len(lines)} lines*"
                
            except GithubException as e:
                if e.status == 404:
                    return f"File not found: {file_path} on branch '{branch}'"
                raise
                
        except Exception as e:
            return f"Error reading file: {str(e)}"


class GitHubPRInput(BaseModel):
    """Input schema for GitHub PR tool."""
    title: str = Field(
        description="PR title (e.g., '🧬 Darwin Fix: Increase button touch target')"
    )
    body: str = Field(
        description="PR description in markdown format"
    )
    file_path: str = Field(
        description="Path to the file to modify"
    )
    new_content: str = Field(
        description="New content for the file"
    )
    branch_name: Optional[str] = Field(
        default=None,
        description="Branch name (auto-generated if not provided)"
    )
    base_branch: str = Field(
        default="main",
        description="Target branch for the PR"
    )


class GitHubPRTool(BaseTool):
    """
    Create a GitHub Pull Request with code changes.
    
    Used by: Engineer Agent
    """
    
    name: str = "github_create_pr"
    description: str = """
    Create a GitHub Pull Request with code fixes.
    This tool will:
    1. Create a new branch
    2. Commit the file changes
    3. Open a Pull Request
    
    Provide the PR title, description, file path, and new file content.
    Returns the PR URL on success.
    """
    args_schema: Type[BaseModel] = GitHubPRInput
    
    def _run(
        self,
        title: str,
        body: str,
        file_path: str,
        new_content: str,
        branch_name: Optional[str] = None,
        base_branch: str = "main"
    ) -> str:
        """Create a PR with the specified changes."""
        settings = get_settings()
        
        try:
            auth = Auth.Token(settings.GITHUB_TOKEN)
            g = Github(auth=auth)
            
            repo = g.get_repo(f"{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}")
            
            # Generate branch name if not provided
            if not branch_name:
                import time
                timestamp = int(time.time())
                # Clean title for branch name
                clean_title = title.lower()
                clean_title = ''.join(c if c.isalnum() or c == ' ' else '' for c in clean_title)
                clean_title = clean_title.replace(' ', '-')[:30]
                branch_name = f"darwin/{clean_title}-{timestamp}"
            
            # Get the base branch SHA
            base_ref = repo.get_branch(base_branch)
            base_sha = base_ref.commit.sha
            
            # Create new branch
            try:
                repo.create_git_ref(
                    ref=f"refs/heads/{branch_name}",
                    sha=base_sha
                )
            except GithubException as e:
                if e.status == 422:  # Branch already exists
                    pass
                else:
                    raise
            
            # Get current file SHA (needed for update)
            try:
                current_file = repo.get_contents(file_path, ref=branch_name)
                file_sha = current_file.sha
                
                # Update file
                repo.update_file(
                    path=file_path,
                    message=f"🧬 Darwin: {title}",
                    content=new_content,
                    sha=file_sha,
                    branch=branch_name
                )
            except GithubException as e:
                if e.status == 404:
                    # File doesn't exist, create it
                    repo.create_file(
                        path=file_path,
                        message=f"🧬 Darwin: {title}",
                        content=new_content,
                        branch=branch_name
                    )
                else:
                    raise
            
            # Create Pull Request
            pr = repo.create_pull(
                title=title,
                body=body,
                head=branch_name,
                base=base_branch
            )
            
            # Add labels
            try:
                pr.add_to_labels("darwin-fix", "auto-generated")
            except:
                pass  # Labels might not exist
            
            return f"""## ✅ Pull Request Created Successfully!

**PR Number:** #{pr.number}
**PR URL:** {pr.html_url}
**Branch:** `{branch_name}` → `{base_branch}`

### Changes Made:
- Modified: `{file_path}`

### Next Steps:
1. Review the changes at {pr.html_url}
2. Request review from team members
3. Merge when approved
"""
            
        except GithubException as e:
            return f"GitHub API Error: {e.status} - {e.data.get('message', str(e))}"
        except Exception as e:
            return f"Error creating PR: {str(e)}"


class GitHubBranchInput(BaseModel):
    """Input schema for GitHub branch check tool."""
    branch_name: str = Field(
        description="Branch name to check"
    )


class GitHubCheckBranchTool(BaseTool):
    """
    Check if a branch exists in the repository.
    
    Used by: Engineer Agent
    """
    
    name: str = "github_check_branch"
    description: str = """
    Check if a branch exists in the GitHub repository.
    Returns True if branch exists, False otherwise.
    """
    args_schema: Type[BaseModel] = GitHubBranchInput
    
    def _run(self, branch_name: str) -> str:
        """Check if branch exists."""
        settings = get_settings()
        
        try:
            auth = Auth.Token(settings.GITHUB_TOKEN)
            g = Github(auth=auth)
            
            repo = g.get_repo(f"{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}")
            
            try:
                repo.get_branch(branch_name)
                return f"Branch '{branch_name}' exists."
            except GithubException as e:
                if e.status == 404:
                    return f"Branch '{branch_name}' does not exist."
                raise
                
        except Exception as e:
            return f"Error checking branch: {str(e)}"


class GitHubListFilesInput(BaseModel):
    """Input schema for GitHub list files tool."""
    directory: str = Field(
        default="",
        description="Directory path to list (empty for root)"
    )
    branch: str = Field(
        default="main",
        description="Branch to list from"
    )


class GitHubListFilesTool(BaseTool):
    """
    List files in a directory of the repository.
    
    Used by: Analyst Agent, Engineer Agent
    """
    
    name: str = "github_list_files"
    description: str = """
    List files and directories in the GitHub repository.
    Useful for exploring the codebase structure.
    Provide a directory path or leave empty for root.
    """
    args_schema: Type[BaseModel] = GitHubListFilesInput
    
    def _run(self, directory: str = "", branch: str = "main") -> str:
        """List files in directory."""
        settings = get_settings()
        
        try:
            auth = Auth.Token(settings.GITHUB_TOKEN)
            g = Github(auth=auth)
            
            repo = g.get_repo(f"{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}")
            
            try:
                contents = repo.get_contents(directory or "", ref=branch)
                
                if not isinstance(contents, list):
                    contents = [contents]
                
                dirs = []
                files = []
                
                for item in contents:
                    if item.type == "dir":
                        dirs.append(f"📁 {item.path}/")
                    else:
                        size = item.size
                        files.append(f"📄 {item.path} ({size} bytes)")
                
                output = f"## Contents of `{directory or '/'}`\n\n"
                
                if dirs:
                    output += "### Directories\n"
                    output += '\n'.join(sorted(dirs)) + '\n\n'
                
                if files:
                    output += "### Files\n"
                    output += '\n'.join(sorted(files)) + '\n'
                
                output += f"\n*{len(dirs)} directories, {len(files)} files*"
                return output
                
            except GithubException as e:
                if e.status == 404:
                    return f"Directory not found: {directory}"
                raise
                
        except Exception as e:
            return f"Error listing files: {str(e)}"
