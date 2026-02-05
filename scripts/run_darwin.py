#!/usr/bin/env python3
"""
Darwin Multi-Agent System - Main Entry Script
=============================================
Run the Darwin AI Growth Engineer pipeline.

Usage:
    python scripts/run_darwin.py              # Full pipeline
    python scripts/run_darwin.py --mode full  # Full pipeline
    python scripts/run_darwin.py --mode analyze  # Skip Watcher
    python scripts/run_darwin.py --mode engineer # Skip to Engineer
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
  full      Run complete pipeline: Watcher → Analyst → Engineer
  analyze   Skip Watcher, analyze existing signals
  engineer  Skip to Engineer, fix existing tasks
  demo      Seed demo data and run analyze mode

Examples:
  python scripts/run_darwin.py                    # Full pipeline
  python scripts/run_darwin.py --mode demo        # Demo with seeded data
  python scripts/run_darwin.py --mode analyze     # Analyze existing signals
        """
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=["full", "analyze", "engineer", "demo"],
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
        mode = "analyze"  # Run analyze after seeding
    
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
