#!/usr/bin/env python3
"""
Darwin Multi-Agent System - Connection Tester
==============================================
Tests all external service connections before running the pipeline.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()


def test_mongodb():
    """Test MongoDB connection."""
    try:
        from pymongo import MongoClient
        from src.config.settings import get_settings
        
        settings = get_settings()
        client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # Force connection
        client.admin.command('ping')
        
        db = client[settings.MONGODB_DATABASE]
        collections = db.list_collection_names()
        
        return True, f"Connected to '{settings.MONGODB_DATABASE}' ({len(collections)} collections)"
    except Exception as e:
        return False, str(e)


def test_posthog():
    """Test PostHog API connection."""
    try:
        import requests
        from src.config.settings import get_settings
        
        settings = get_settings()
        
        response = requests.get(
            f"{settings.POSTHOG_HOST}/api/projects/@current",
            headers={"Authorization": f"Bearer {settings.POSTHOG_API_KEY}"},
            timeout=10
        )
        
        if response.status_code == 200:
            project = response.json()
            return True, f"Project: {project.get('name', 'Unknown')} (ID: {project.get('id')})"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, str(e)


def test_github():
    """Test GitHub API connection."""
    try:
        from github import Github, Auth
        from src.config.settings import get_settings
        
        settings = get_settings()
        
        auth = Auth.Token(settings.GITHUB_TOKEN)
        g = Github(auth=auth)
        
        user = g.get_user()
        repo = g.get_repo(f"{settings.GITHUB_OWNER}/{settings.GITHUB_REPO}")
        
        return True, f"User: {user.login} | Repo: {repo.full_name}"
    except Exception as e:
        return False, str(e)


def test_gemini():
    """Test Gemini API connection."""
    try:
        from google import genai
        from src.config.settings import get_settings
        
        settings = get_settings()
        
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents="Say 'Darwin Ready!' in 2 words"
        )
        
        return True, f"Response: {response.text.strip()[:50]}"
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            return None, "Rate limited (key is valid, quota exhausted)"
        return False, error_msg[:80]


def main():
    """Run all connection tests."""
    
    # Banner
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🧬 Darwin Connection Tester[/bold cyan]\n"
        "[dim]Verifying all external service connections[/dim]",
        border_style="cyan"
    ))
    console.print()
    
    # Run tests
    tests = [
        ("MongoDB", test_mongodb),
        ("PostHog", test_posthog),
        ("GitHub", test_github),
        ("Gemini", test_gemini),
    ]
    
    # Results table
    table = Table(title="Connection Test Results", show_header=True)
    table.add_column("Service", style="cyan", width=12)
    table.add_column("Status", width=10)
    table.add_column("Details", style="dim")
    
    all_passed = True
    
    for name, test_func in tests:
        console.print(f"Testing {name}...", end=" ")
        
        try:
            result, message = test_func()
            
            if result is True:
                status = "[green]✅ OK[/green]"
                console.print("[green]OK[/green]")
            elif result is None:
                status = "[yellow]⚠️ WARN[/yellow]"
                console.print("[yellow]WARN[/yellow]")
            else:
                status = "[red]❌ FAIL[/red]"
                console.print("[red]FAIL[/red]")
                all_passed = False
                
            table.add_row(name, status, message[:60])
            
        except Exception as e:
            table.add_row(name, "[red]❌ ERROR[/red]", str(e)[:60])
            console.print("[red]ERROR[/red]")
            all_passed = False
    
    console.print()
    console.print(table)
    console.print()
    
    # Summary
    if all_passed:
        console.print(Panel(
            "[bold green]✅ All connections successful![/bold green]\n"
            "[dim]Darwin is ready to run.[/dim]",
            border_style="green"
        ))
        return 0
    else:
        console.print(Panel(
            "[bold red]❌ Some connections failed![/bold red]\n"
            "[dim]Please check your .env configuration.[/dim]",
            border_style="red"
        ))
        return 1


if __name__ == "__main__":
    sys.exit(main())
