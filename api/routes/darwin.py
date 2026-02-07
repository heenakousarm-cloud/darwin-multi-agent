"""
Darwin Pipeline API Routes

Endpoints for triggering Darwin agent pipelines.
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Optional
from enum import Enum
import subprocess
import os
import sys

router = APIRouter()


class PipelineMode(str, Enum):
    analyze = "analyze"
    engineer = "engineer"
    review = "review"
    full = "full"


@router.post("/run")
async def run_darwin_pipeline(
    mode: PipelineMode = Body(..., description="Pipeline mode to run"),
    dry_run: bool = Body(default=False, description="If true, only validate without running"),
):
    """
    Trigger a Darwin pipeline run.
    
    Modes:
    - analyze: Run Watcher + Analyst (detect signals, diagnose issues)
    - engineer: Run Engineer (create PRs for approved issues)
    - review: Interactive review mode (not recommended via API)
    - full: Run all agents (Watcher → Analyst → Engineer)
    
    Note: 'review' mode requires interactive input and may not work well via API.
    """
    if mode == PipelineMode.review:
        return {
            "success": False,
            "message": "Review mode requires interactive input. Use the CLI instead: python scripts/run_darwin.py --mode review",
            "mode": mode,
        }
    
    if dry_run:
        return {
            "success": True,
            "message": f"Dry run: Would execute Darwin pipeline in '{mode}' mode",
            "mode": mode,
            "dry_run": True,
        }
    
    # Get the project root directory
    # __file__ = api/routes/darwin.py, need to go up 3 levels to reach project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    script_path = os.path.join(project_root, "scripts", "run_darwin.py")
    venv_python = os.path.join(project_root, "venv", "bin", "python")
    
    # Check if script exists
    if not os.path.exists(script_path):
        raise HTTPException(
            status_code=500,
            detail=f"Darwin script not found at {script_path}"
        )
    
    # Use venv python if available, otherwise system python
    python_cmd = venv_python if os.path.exists(venv_python) else sys.executable
    
    try:
        # Run the Darwin pipeline
        result = subprocess.run(
            [python_cmd, script_path, "--mode", mode.value],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=project_root,
            env={**os.environ, "PYTHONPATH": project_root},
        )
        
        return {
            "success": result.returncode == 0,
            "message": f"Darwin pipeline '{mode}' completed" if result.returncode == 0 else f"Darwin pipeline '{mode}' failed",
            "mode": mode,
            "exit_code": result.returncode,
            "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,  # Truncate if too long
            "stderr": result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr,
        }
        
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail=f"Darwin pipeline '{mode}' timed out after 5 minutes"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running Darwin pipeline: {str(e)}"
        )


@router.get("/status")
async def get_darwin_status():
    """
    Get the current status of Darwin system.
    
    Returns information about available modes and system health.
    """
    # __file__ = api/routes/darwin.py, need to go up 3 levels to reach project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Check if key files exist
    checks = {
        "run_darwin_script": os.path.exists(os.path.join(project_root, "scripts", "run_darwin.py")),
        "venv_exists": os.path.exists(os.path.join(project_root, "venv")),
        "agents_folder": os.path.exists(os.path.join(project_root, "src", "agents")),
        "tools_folder": os.path.exists(os.path.join(project_root, "src", "tools")),
    }
    
    return {
        "status": "healthy" if all(checks.values()) else "degraded",
        "available_modes": ["analyze", "engineer", "full"],
        "interactive_modes": ["review"],
        "checks": checks,
    }
