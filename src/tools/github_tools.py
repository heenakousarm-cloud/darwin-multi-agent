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
    """Input schema for GitHub PR tool - PATCH BASED (no full file needed)."""
    title: str = Field(
        description="PR title (e.g., '🧬 Darwin Fix: Increase button touch target')"
    )
    body: str = Field(
        description="PR description in markdown format"
    )
    file_path: str = Field(
        description="Path to the file to modify"
    )
    original_code: str = Field(
        description="The original code snippet to find and replace (copy exactly from the file)"
    )
    suggested_code: str = Field(
        description="The new code to replace the original with"
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
    Create a GitHub Pull Request with code changes using PATCH approach.
    
    Used by: Engineer Agent
    
    This tool uses a PATCH-BASED approach:
    - You provide original_code (what to find) and suggested_code (what to replace with)
    - The tool reads the file, applies the replacement, and creates the PR
    - You do NOT need to provide the entire file content!
    """
    
    name: str = "github_create_pr"
    description: str = """
    Create a GitHub Pull Request with code fixes using PATCH approach.
    
    IMPORTANT: This tool uses find-and-replace, NOT full file content!
    
    You need to provide:
    - title: PR title
    - body: PR description
    - file_path: Path to the file
    - original_code: The EXACT code snippet to find (copy from the issue's recommended_fix)
    - suggested_code: The new code to replace it with (copy from the issue's recommended_fix)
    
    The tool will:
    1. Read the current file from GitHub
    2. Find and replace original_code with suggested_code
    3. Create a new branch
    4. Commit the changes
    5. Open a Pull Request
    
    Returns the PR URL on success.
    """
    args_schema: Type[BaseModel] = GitHubPRInput
    
    def _apply_patch(self, content: str, original_code: str, suggested_code: str) -> str:
        """Apply the code patch using find-and-replace."""
        # Normalize line endings
        content = content.replace('\r\n', '\n')
        original_code = original_code.replace('\r\n', '\n')
        suggested_code = suggested_code.replace('\r\n', '\n')
        
        # Also handle escaped newlines from JSON
        original_code = original_code.replace('\\n', '\n')
        suggested_code = suggested_code.replace('\\n', '\n')
        
        # Try direct replacement first
        if original_code in content:
            return content.replace(original_code, suggested_code, 1)
        
        # Try with normalized whitespace (strip trailing spaces from each line)
        original_lines = [line.rstrip() for line in original_code.split('\n')]
        content_lines = content.split('\n')
        content_lines_stripped = [line.rstrip() for line in content_lines]
        
        # Find matching section
        for i in range(len(content_lines) - len(original_lines) + 1):
            match = True
            for j, orig_line in enumerate(original_lines):
                if content_lines_stripped[i + j] != orig_line.rstrip():
                    match = False
                    break
            
            if match:
                # Found the match - replace preserving original indentation
                result_lines = content_lines[:i]
                
                # Get base indentation from first matched line
                first_line = content_lines[i]
                base_indent = len(first_line) - len(first_line.lstrip())
                
                # Add suggested code
                for k, suggested_line in enumerate(suggested_code.split('\n')):
                    if k == 0:
                        # First line keeps original indentation
                        result_lines.append(' ' * base_indent + suggested_line.lstrip())
                    elif suggested_line.strip():
                        # Non-empty lines: preserve relative indentation
                        result_lines.append(' ' * base_indent + suggested_line.lstrip())
                    else:
                        # Empty lines
                        result_lines.append('')
                
                result_lines.extend(content_lines[i + len(original_lines):])
                return '\n'.join(result_lines)
        
        raise ValueError(f"Could not find original code in file. Make sure original_code matches exactly.")
    
    def _run(
        self,
        title: str,
        body: str,
        file_path: str,
        original_code: str,
        suggested_code: str,
        branch_name: Optional[str] = None,
        base_branch: str = "main"
    ) -> str:
        """Create a PR with the specified patch changes."""
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
            
            # Read current file content
            try:
                current_file = repo.get_contents(file_path, ref=base_branch)
                current_content = base64.b64decode(current_file.content).decode('utf-8')
                file_sha = current_file.sha
            except GithubException as e:
                if e.status == 404:
                    return f"Error: File not found: {file_path}"
                raise
            
            # Apply the patch
            try:
                new_content = self._apply_patch(current_content, original_code, suggested_code)
            except ValueError as e:
                return f"Error applying patch: {str(e)}"
            
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
            
            # Update file on the new branch
            repo.update_file(
                path=file_path,
                message=f"🧬 Darwin: {title}",
                content=new_content,
                sha=file_sha,
                branch=branch_name
            )
            
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
- Applied patch: Replaced original code with suggested fix

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
