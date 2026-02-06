"""
Darwin Multi-Agent System - Crew Orchestration
==============================================
Main crew that orchestrates Watcher → Analyst → Engineer pipeline.
"""

from crewai import Crew, Process
from typing import Optional, Literal

from src.agents import (
    create_watcher_agent,
    create_analyst_agent,
    create_engineer_agent,
    get_gemini_llm,
)
from src.tasks import (
    create_detect_signals_task,
    create_analyze_issues_task,
    create_fix_and_pr_task,
)
from src.config.settings import get_settings


def create_darwin_crew(
    mode: Literal["full", "analyze", "engineer"] = "full",
    verbose: bool = True,
) -> Crew:
    """
    Create the Darwin crew with all agents and tasks.
    
    Modes:
    - full: Run complete pipeline (Watcher → Analyst → Engineer) - NO approval
    - analyze: Watcher + Analyst only (detect & diagnose) - SAFE, no PR
    - engineer: Engineer only (create PRs for approved issues)
    
    Args:
        mode: Pipeline mode to run
        verbose: Enable verbose output
    
    Returns:
        Configured Crew ready to kickoff
    """
    settings = get_settings()
    
    # Create shared LLM instance
    llm = get_gemini_llm()
    
    # Create tasks based on mode
    agents = []
    tasks = []
    
    if mode == "full":
        # Full pipeline: Watcher → Analyst → Engineer (no approval step)
        watcher = create_watcher_agent(llm)
        analyst = create_analyst_agent(llm)
        engineer = create_engineer_agent(llm)
        
        task1 = create_detect_signals_task(watcher)
        task2 = create_analyze_issues_task(analyst, context_tasks=[task1])
        task3 = create_fix_and_pr_task(engineer, context_tasks=[task2])
        
        agents = [watcher, analyst, engineer]
        tasks = [task1, task2, task3]
        
    elif mode == "analyze":
        # Watcher + Analyst only (SAFE mode - no PR created)
        # User should run --mode review after this to approve fixes
        watcher = create_watcher_agent(llm)
        analyst = create_analyst_agent(llm)
        
        task1 = create_detect_signals_task(watcher)
        task2 = create_analyze_issues_task(analyst, context_tasks=[task1])
        
        agents = [watcher, analyst]
        tasks = [task1, task2]
        
    elif mode == "engineer":
        # Engineer only (create PRs for approved issues)
        engineer = create_engineer_agent(llm)
        task3 = create_fix_and_pr_task(engineer)
        
        agents = [engineer]
        tasks = [task3]
    
    # Create and return the crew
    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential,  # Tasks run in order
        verbose=verbose,
        memory=False,  # Disable memory for simpler execution
        full_output=True,  # Get detailed output
    )
    
    return crew


def run_darwin(
    mode: Literal["full", "analyze", "engineer"] = "full",
    verbose: bool = True,
) -> dict:
    """
    Run the Darwin pipeline.
    
    Args:
        mode: Pipeline mode (full, analyze, engineer)
        verbose: Enable verbose output
    
    Returns:
        Dictionary with execution results
    """
    from rich.console import Console
    from rich.panel import Panel
    
    console = Console()
    
    # Display mode info
    mode_info = {
        "full": "🔄 Full Pipeline: Watcher → Analyst → Engineer",
        "analyze": "🧠 Analyze Mode: Analyst → Engineer (using existing signals)",
        "engineer": "👩‍💻 Engineer Mode: Engineer only (using existing tasks)",
    }
    
    console.print()
    console.print(Panel(
        f"[bold cyan]🧬 Darwin - AI Growth Engineer[/bold cyan]\n\n"
        f"[dim]{mode_info.get(mode, mode)}[/dim]",
        border_style="cyan"
    ))
    console.print()
    
    try:
        # Create crew
        console.print("[yellow]Creating Darwin crew...[/yellow]")
        crew = create_darwin_crew(mode=mode, verbose=verbose)
        console.print(f"[green]✅ Crew created with {len(crew.agents)} agent(s) and {len(crew.tasks)} task(s)[/green]")
        console.print()
        
        # Run the crew
        console.print("[yellow]🚀 Starting Darwin pipeline...[/yellow]")
        console.print("-" * 50)
        
        result = crew.kickoff()
        
        console.print("-" * 50)
        console.print()
        
        # Return results
        return {
            "success": True,
            "mode": mode,
            "result": result,
            "agents_used": len(crew.agents),
            "tasks_completed": len(crew.tasks),
        }
        
    except Exception as e:
        console.print(f"[red]❌ Error running Darwin: {str(e)}[/red]")
        return {
            "success": False,
            "mode": mode,
            "error": str(e),
        }


# Convenience functions for specific modes
def run_full_pipeline(verbose: bool = True) -> dict:
    """Run the complete Darwin pipeline."""
    return run_darwin(mode="full", verbose=verbose)


def run_analysis_only(verbose: bool = True) -> dict:
    """Run analysis on existing signals."""
    return run_darwin(mode="analyze", verbose=verbose)


def run_engineer_only(verbose: bool = True) -> dict:
    """Run engineer on existing tasks."""
    return run_darwin(mode="engineer", verbose=verbose)
