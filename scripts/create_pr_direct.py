#!/usr/bin/env python3
"""
Darwin Direct PR Creator
========================
Creates GitHub PRs directly without using the LLM for code generation.
Uses the recommended_fix from MongoDB which already has the exact changes.

This bypasses the LLM context/output limit issues.
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from github import Github, Auth
from github.GithubException import GithubException
import base64

from src.config.settings import get_settings
from src.db import find_many, update_by_id, insert_one

console = Console()


def get_file_from_github(repo, file_path: str, branch: str = "main") -> str:
    """Read file content from GitHub."""
    try:
        file_content = repo.get_contents(file_path, ref=branch)
        if isinstance(file_content, list):
            raise ValueError(f"'{file_path}' is a directory")
        return base64.b64decode(file_content.content).decode('utf-8')
    except GithubException as e:
        if e.status == 404:
            raise FileNotFoundError(f"File not found: {file_path}")
        raise


def apply_fix(original_content: str, original_code: str, suggested_code: str) -> str:
    """Apply the fix by replacing original_code with suggested_code."""
    # Normalize line endings
    original_content = original_content.replace('\r\n', '\n')
    original_code = original_code.replace('\r\n', '\n')
    suggested_code = suggested_code.replace('\r\n', '\n')
    
    if original_code in original_content:
        return original_content.replace(original_code, suggested_code, 1)
    
    # Try with normalized whitespace
    original_lines = [line.strip() for line in original_code.split('\n')]
    content_lines = original_content.split('\n')
    
    # Find matching section
    for i in range(len(content_lines) - len(original_lines) + 1):
        match = True
        for j, orig_line in enumerate(original_lines):
            if content_lines[i + j].strip() != orig_line:
                match = False
                break
        
        if match:
            # Found the match - replace preserving indentation
            result_lines = content_lines[:i]
            
            # Get base indentation from first line
            base_indent = len(content_lines[i]) - len(content_lines[i].lstrip())
            indent = ' ' * base_indent
            
            # Add suggested code with proper indentation
            for suggested_line in suggested_code.split('\n'):
                if suggested_line.strip():
                    result_lines.append(indent + suggested_line.lstrip())
                else:
                    result_lines.append('')
            
            result_lines.extend(content_lines[i + len(original_lines):])
            return '\n'.join(result_lines)
    
    raise ValueError("Could not find original code in file content")


def create_pr(repo, file_path: str, new_content: str, title: str, body: str, base_branch: str = "main"):
    """Create a PR with the changes."""
    # Generate branch name
    timestamp = int(time.time())
    clean_title = title.lower()
    clean_title = ''.join(c if c.isalnum() or c == ' ' else '' for c in clean_title)
    clean_title = clean_title.replace(' ', '-')[:30]
    branch_name = f"darwin/{clean_title}-{timestamp}"
    
    # Get base branch ref
    base_ref = repo.get_git_ref(f"heads/{base_branch}")
    base_sha = base_ref.object.sha
    
    # Create new branch
    repo.create_git_ref(f"refs/heads/{branch_name}", base_sha)
    console.print(f"[green]✅ Created branch: {branch_name}[/green]")
    
    # Get current file SHA
    file_obj = repo.get_contents(file_path, ref=base_branch)
    
    # Commit the change
    repo.update_file(
        path=file_path,
        message=f"🧬 Darwin Fix: {title}",
        content=new_content,
        sha=file_obj.sha,
        branch=branch_name
    )
    console.print(f"[green]✅ Committed changes to {file_path}[/green]")
    
    # Create PR
    pr = repo.create_pull(
        title=title,
        body=body,
        head=branch_name,
        base=base_branch
    )
    console.print(f"[green]✅ Created PR: {pr.html_url}[/green]")
    
    return {
        "pr_number": pr.number,
        "pr_url": pr.html_url,
        "branch_name": branch_name
    }


def main():
    console.print()
    console.print(Panel(
        "[bold cyan]🧬 Darwin Direct PR Creator[/bold cyan]\n\n"
        "Creates PRs directly using fixes from MongoDB",
        border_style="cyan"
    ))
    console.print()
    
    settings = get_settings()
    
    # Connect to GitHub
    auth = Auth.Token(settings.GITHUB_TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(f"{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}")
    console.print(f"[green]✅ Connected to GitHub: {settings.GITHUB_OWNER}/{settings.GITHUB_REPO}[/green]")
    
    # Find approved issues (or diagnosed if none approved)
    issues = find_many("ux_issues", {"status": "approved"}, limit=1)
    
    if not issues:
        console.print("[yellow]No approved issues found. Looking for diagnosed issues...[/yellow]")
        issues = find_many("ux_issues", {"status": "diagnosed"}, limit=1)
    
    if not issues:
        console.print("[red]❌ No issues found to process.[/red]")
        return
    
    issue = issues[0]
    issue_id = str(issue.get("_id"))
    
    console.print()
    console.print(Panel(
        f"[bold]Issue: {issue.get('title', 'Untitled')}[/bold]\n\n"
        f"[cyan]File:[/cyan] {issue.get('file_path', 'N/A')}\n"
        f"[cyan]Status:[/cyan] {issue.get('status', 'N/A')}\n"
        f"[cyan]Priority:[/cyan] {issue.get('priority', 'N/A')}",
        title="📋 Processing Issue",
        border_style="yellow"
    ))
    
    # Get the recommended fix
    fix = issue.get("recommended_fix", {})
    
    if isinstance(fix, list):
        fix = fix[0] if fix else {}
    
    if not fix:
        console.print("[red]❌ No recommended fix found in issue.[/red]")
        return
    
    file_path = fix.get("file_path") or issue.get("file_path")
    original_code = fix.get("original_code", "")
    suggested_code = fix.get("suggested_code", "")
    
    if not file_path or file_path in ["N/A", "unknown"]:
        console.print("[red]❌ Invalid file path.[/red]")
        return
    
    if not original_code or not suggested_code:
        console.print("[red]❌ Missing original_code or suggested_code in fix.[/red]")
        return
    
    console.print()
    console.print(f"[cyan]📁 File:[/cyan] {file_path}")
    
    # Show the fix
    console.print()
    console.print("[red]━━━ BEFORE ━━━[/red]")
    console.print(Syntax(original_code, "typescript", theme="monokai"))
    console.print()
    console.print("[green]━━━ AFTER ━━━[/green]")
    console.print(Syntax(suggested_code, "typescript", theme="monokai"))
    console.print()
    
    # Read current file from GitHub
    console.print("[cyan]📖 Reading file from GitHub...[/cyan]")
    try:
        current_content = get_file_from_github(repo, file_path)
        console.print(f"[green]✅ Read {len(current_content)} characters[/green]")
    except Exception as e:
        console.print(f"[red]❌ Failed to read file: {e}[/red]")
        return
    
    # Apply the fix
    console.print("[cyan]🔧 Applying fix...[/cyan]")
    try:
        new_content = apply_fix(current_content, original_code, suggested_code)
        console.print(f"[green]✅ Fix applied successfully[/green]")
    except Exception as e:
        console.print(f"[red]❌ Failed to apply fix: {e}[/red]")
        return
    
    # Create PR
    console.print()
    console.print("[cyan]🚀 Creating Pull Request...[/cyan]")
    
    pr_title = f"🧬 Darwin Fix: {fix.get('title', issue.get('title', 'UX Improvement'))}"
    pr_body = f"""## 🧬 Darwin Auto-Fix

**Issue:** {issue.get('title', 'UX Issue')}

### Root Cause
{issue.get('root_cause', 'See issue details')}

### User Impact
{issue.get('user_impact', 'Improved user experience')}

### Changes Made
{fix.get('description', 'Applied recommended fix')}

---
*This PR was automatically generated by Darwin AI Growth Engineer*
"""
    
    try:
        pr_result = create_pr(repo, file_path, new_content, pr_title, pr_body)
        
        # Save PR to MongoDB
        pr_doc = {
            "issue_id": issue_id,
            "pr_number": pr_result["pr_number"],
            "pr_url": pr_result["pr_url"],
            "branch_name": pr_result["branch_name"],
            "file_path": file_path,
            "status": "open",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")
        }
        insert_one("pull_requests", pr_doc)
        console.print("[green]✅ PR details saved to MongoDB[/green]")
        
        # Update issue status
        update_by_id("ux_issues", issue_id, {"status": "pr_created"})
        console.print("[green]✅ Issue status updated to 'pr_created'[/green]")
        
        console.print()
        console.print(Panel(
            f"[bold green]✅ PR Created Successfully![/bold green]\n\n"
            f"[cyan]PR URL:[/cyan] {pr_result['pr_url']}\n"
            f"[cyan]Branch:[/cyan] {pr_result['branch_name']}",
            title="🎉 Success",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Failed to create PR: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
