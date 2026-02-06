#!/usr/bin/env python3
"""
Darwin Multi-Agent System - Main Entry Script
=============================================
Run the Darwin AI Growth Engineer pipeline.

Usage:
    python scripts/run_darwin.py              # Full pipeline (no approval)
    python scripts/run_darwin.py --mode full  # Full pipeline (no approval)
    python scripts/run_darwin.py --mode analyze  # Watcher + Analyst only (no PR)
    python scripts/run_darwin.py --mode review   # Review issues & approve before PR
    python scripts/run_darwin.py --mode engineer # Skip to Engineer (create PR)
    python scripts/run_darwin.py --mode demo  # Seed data + analyze
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.prompt import Confirm
from rich import print as rprint

console = Console()


# ASCII Banner
DARWIN_BANNER = """
[bold cyan]
    ██████╗  █████╗ ██████╗ ██╗    ██╗██╗███╗   ██╗
    ██╔══██╗██╔══██╗██╔══██╗██║    ██║██║████╗  ██║
    ██║  ██║███████║██████╔╝██║ █╗ ██║██║██╔██╗ ██║
    ██║  ██║██╔══██║██╔══██╗██║███╗██║██║██║╚██╗██║
    ██████╔╝██║  ██║██║  ██║╚███╔███╔╝██║██║ ╚████║
    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚═╝╚═╝  ╚═══╝
[/bold cyan]
[dim]    🧬 AI Growth Engineer - Auto-Optimize Agent[/dim]
"""


def display_config():
    """Display current configuration."""
    from src.config.settings import get_settings
    
    settings = get_settings()
    
    table = Table(title="Configuration", show_header=True)
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("PostHog Host", settings.POSTHOG_HOST)
    table.add_row("PostHog Project", str(settings.POSTHOG_PROJECT_ID))
    table.add_row("GitHub Owner", settings.GITHUB_OWNER)
    table.add_row("GitHub Repo", settings.GITHUB_REPO)
    table.add_row("MongoDB", settings.MONGODB_URI)
    table.add_row("Database", settings.MONGODB_DATABASE)
    table.add_row("LLM Model", settings.GEMINI_MODEL)
    
    console.print(table)
    console.print()


def display_ux_issues_for_review():
    """Display UX issues pending review and ask for approval."""
    from src.db import find_many, update_by_id
    
    console.print()
    console.print("[bold cyan]📋 UX Issues Pending Review[/bold cyan]")
    console.print()
    
    # Find diagnosed issues that haven't been approved yet
    issues = find_many("ux_issues", {"status": "diagnosed"})
    
    if not issues:
        console.print("[yellow]⚠️ No UX issues found pending review.[/yellow]")
        console.print("[dim]Run --mode analyze first to detect and diagnose issues.[/dim]")
        return None
    
    approved_issues = []
    
    for i, issue in enumerate(issues, 1):
        issue_id = str(issue.get("_id"))
        
        # Display issue details
        console.print(Panel(
            f"[bold]Issue #{i}: {issue.get('title', 'Untitled')}[/bold]\n\n"
            f"[cyan]Priority:[/cyan] {issue.get('priority', 'unknown')}\n"
            f"[cyan]Confidence:[/cyan] {issue.get('confidence', 0) * 100:.0f}%\n"
            f"[cyan]File:[/cyan] {issue.get('file_path', 'unknown')}\n"
            f"[cyan]Page:[/cyan] {issue.get('page', 'unknown')}\n\n"
            f"[yellow]Root Cause:[/yellow]\n{issue.get('root_cause', 'Not specified')}\n\n"
            f"[yellow]User Impact:[/yellow]\n{issue.get('user_impact', 'Not specified')}",
            title=f"🔍 UX Issue - {issue_id[:8]}...",
            border_style="yellow"
        ))
        
        # Display recommended fix(es)
        fix_data = issue.get("recommended_fix", {})
        
        # Handle both single fix (dict) and multiple fixes (list)
        if isinstance(fix_data, list):
            fixes = fix_data
        elif isinstance(fix_data, dict) and fix_data:
            fixes = [fix_data]
        else:
            fixes = []
        
        if fixes:
            for fix_idx, fix in enumerate(fixes, 1):
                console.print()
                fix_title = fix.get('title', 'Untitled') if isinstance(fix, dict) else 'Untitled'
                fix_desc = fix.get('description', '') if isinstance(fix, dict) else ''
                
                if len(fixes) > 1:
                    console.print(f"[bold green]💡 Fix {fix_idx}/{len(fixes)}: {fix_title}[/bold green]")
                else:
                    console.print(f"[bold green]💡 Recommended Fix: {fix_title}[/bold green]")
                console.print(f"[dim]{fix_desc}[/dim]")
                console.print()
                
                # Show original code
                original_code = fix.get("original_code", "") if isinstance(fix, dict) else ""
                if original_code:
                    console.print("[red]━━━ BEFORE (Current Code) ━━━[/red]")
                    syntax = Syntax(original_code, "typescript", theme="monokai", line_numbers=True)
                    console.print(syntax)
                    console.print()
                
                # Show suggested code
                suggested_code = fix.get("suggested_code", "") if isinstance(fix, dict) else ""
                if suggested_code:
                    console.print("[green]━━━ AFTER (Proposed Fix) ━━━[/green]")
                    syntax = Syntax(suggested_code, "typescript", theme="monokai", line_numbers=True)
                    console.print(syntax)
                    console.print()
        
        # Ask for approval
        console.print()
        approved = Confirm.ask(
            f"[bold]Do you approve this fix for PR creation?[/bold]",
            default=False
        )
        
        if approved:
            # Update issue status to approved
            update_by_id("ux_issues", issue_id, {"status": "approved"})
            approved_issues.append(issue)
            console.print(f"[green]✅ Issue approved! Status updated to 'approved'[/green]")
        else:
            console.print(f"[yellow]⏭️ Issue skipped (not approved)[/yellow]")
        
        console.print()
        console.print("─" * 60)
        console.print()
    
    return approved_issues


def seed_demo_data():
    """Seed MongoDB with demo signal data."""
    from src.db import insert_one, count
    from datetime import datetime
    
    console.print("[yellow]🌱 Seeding demo data...[/yellow]")
    
    # Check if signals already exist
    existing = count("signals", {"processed": False})
    if existing > 0:
        console.print(f"[green]✅ Found {existing} existing unprocessed signal(s)[/green]")
        return
    
    # Create a demo signal for rage clicks on Add to Cart
    demo_signal = {
        "type": "rage_click",
        "severity": "high",
        "status": "new",
        "title": "Rage clicks detected on Add to Cart button",
        "description": "Users are repeatedly clicking the Add to Cart button on product pages, indicating frustration with the button's responsiveness or size.",
        "metric_name": "rage_click_count",
        "metric_value": 47,
        "threshold": 20,
        "confidence": 0.85,
        "page": "/product/[id]",
        "element": "Add to Cart button",
        "affected_users": 156,
        "session_count": 89,
        "recording_ids": [],
        "sample_events": [],
        "first_seen": datetime.utcnow().isoformat(),
        "last_seen": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "processed": False,
        "ux_issue_id": None,
    }
    
    doc_id = insert_one("signals", demo_signal)
    console.print(f"[green]✅ Created demo signal: {doc_id}[/green]")
    console.print(f"[dim]   Title: {demo_signal['title']}[/dim]")
    console.print(f"[dim]   Severity: {demo_signal['severity']}[/dim]")
    console.print(f"[dim]   Affected Users: {demo_signal['affected_users']}[/dim]")


def run_pipeline(mode: str, verbose: bool = True):
    """Run the Darwin pipeline."""
    from src.crew import run_darwin
    
    console.print()
    console.print(f"[bold yellow]🚀 Running Darwin in {mode.upper()} mode...[/bold yellow]")
    console.print()
    
    result = run_darwin(mode=mode, verbose=verbose)
    
    console.print()
    
    if result.get("success"):
        console.print(Panel(
            f"[bold green]✅ Darwin completed successfully![/bold green]\n\n"
            f"Mode: {result.get('mode')}\n"
            f"Agents used: {result.get('agents_used')}\n"
            f"Tasks completed: {result.get('tasks_completed')}",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"[bold red]❌ Darwin encountered an error[/bold red]\n\n"
            f"Error: {result.get('error', 'Unknown error')}",
            border_style="red"
        ))
    
    return result


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="🧬 Darwin - AI Growth Engineer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  full      Run complete pipeline: Watcher → Analyst → Engineer (NO approval)
  analyze   Watcher + Analyst only (detect & diagnose, NO PR created)
  review    Review diagnosed issues and approve before PR creation
  engineer  Skip to Engineer, create PRs for approved issues
  demo      Seed demo data and run analyze mode

Recommended Flow (with approval):
  1. python scripts/run_darwin.py --mode analyze   # Detect & diagnose
  2. python scripts/run_darwin.py --mode review    # Review & approve
  3. python scripts/run_darwin.py --mode engineer  # Create PRs

Examples:
  python scripts/run_darwin.py --mode analyze     # Safe: No PR created
  python scripts/run_darwin.py --mode review      # Review issues, approve fixes
  python scripts/run_darwin.py --mode demo        # Demo with seeded data
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["full", "analyze", "review", "engineer", "demo"],
        default="full",
        help="Pipeline mode to run (default: full)"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Reduce output verbosity"
    )
    
    parser.add_argument(
        "--config", "-c",
        action="store_true",
        help="Display configuration and exit"
    )
    
    parser.add_argument(
        "--seed", "-s",
        action="store_true",
        help="Seed demo data and exit"
    )
    
    args = parser.parse_args()
    
    # Display banner
    console.print(DARWIN_BANNER)
    
    # Config only mode
    if args.config:
        display_config()
        return 0
    
    # Display config
    display_config()
    
    # Seed only mode
    if args.seed:
        seed_demo_data()
        return 0
    
    # Handle demo mode
    mode = args.mode
    if mode == "demo":
        seed_demo_data()
        mode = "analyze"  # Run analyze after seeding (safe - no PR)
    
    # Handle review mode (human-in-the-loop approval)
    if mode == "review":
        try:
            approved_issues = display_ux_issues_for_review()
            
            if approved_issues:
                console.print()
                console.print(f"[bold green]✅ {len(approved_issues)} issue(s) approved![/bold green]")
                console.print()
                
                # Ask if user wants to create PRs now
                create_prs = Confirm.ask(
                    "[bold]Do you want to create GitHub PRs for approved issues now?[/bold]",
                    default=True
                )
                
                if create_prs:
                    console.print()
                    console.print("[yellow]🚀 Running Engineer to create PRs...[/yellow]")
                    result = run_pipeline(mode="engineer", verbose=not args.quiet)
                    return 0 if result.get("success") else 1
                else:
                    console.print()
                    console.print("[dim]To create PRs later, run:[/dim]")
                    console.print("[cyan]  python scripts/run_darwin.py --mode engineer[/cyan]")
                    return 0
            else:
                console.print("[yellow]No issues were approved.[/yellow]")
                return 0
                
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
            return 130
        except Exception as e:
            console.print(f"\n[red]❌ Error: {str(e)}[/red]")
            return 1
    
    # For analyze mode, only run Watcher + Analyst (no Engineer)
    if mode == "analyze":
        console.print("[dim]ℹ️  Running in SAFE mode: No PRs will be created.[/dim]")
        console.print("[dim]   After analysis, run --mode review to approve fixes.[/dim]")
        console.print()
    
    # Run the pipeline
    try:
        result = run_pipeline(mode=mode, verbose=not args.quiet)
        return 0 if result.get("success") else 1
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
        return 130
    except Exception as e:
        console.print(f"\n[red]❌ Fatal error: {str(e)}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
