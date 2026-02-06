"""
Darwin API - Main Entry Point

FastAPI application that provides REST API access to Darwin Multi-Agent System.

Run with:
    python scripts/run_api.py
    
Or directly:
    uvicorn api.main:app --reload --port 8000
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.middleware.auth import verify_api_key
from api.routes import signals, ux_issues, pull_requests, darwin, stats

# Create FastAPI app
app = FastAPI(
    title="Darwin API",
    description="""
    REST API for Darwin Multi-Agent System.
    
    Darwin is an AI-powered UX improvement system that:
    - Detects friction signals from PostHog analytics
    - Diagnoses root causes in the codebase
    - Recommends and implements code fixes
    - Creates GitHub Pull Requests
    
    ## Authentication
    
    All endpoints (except `/`, `/health`, `/docs`) require API key authentication.
    
    Include the API key in the Authorization header:
    ```
    Authorization: Bearer darwin_sk_xxxxx
    ```
    
    ## Available Endpoints
    
    - **Signals**: View and filter UX friction signals
    - **UX Issues**: View, approve, or reject diagnosed issues
    - **Pull Requests**: View PRs created by Darwin
    - **Darwin**: Trigger pipeline runs
    - **Stats**: Get dashboard statistics
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Public Endpoints (no authentication required)
# ============================================================================

@app.get("/", tags=["Public"])
async def root():
    """
    API root - returns basic information about the API.
    """
    return {
        "name": "Darwin API",
        "version": "1.0.0",
        "description": "REST API for Darwin Multi-Agent System",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Public"])
async def health():
    """
    Health check endpoint.
    
    Returns the current health status of the API.
    """
    return {
        "status": "healthy",
        "service": "darwin-api",
    }


# ============================================================================
# Protected Endpoints (authentication required)
# ============================================================================

# Signals routes
app.include_router(
    signals.router,
    prefix="/api/signals",
    tags=["Signals"],
    dependencies=[Depends(verify_api_key)],
)

# UX Issues routes
app.include_router(
    ux_issues.router,
    prefix="/api/ux-issues",
    tags=["UX Issues"],
    dependencies=[Depends(verify_api_key)],
)

# Pull Requests routes
app.include_router(
    pull_requests.router,
    prefix="/api/pull-requests",
    tags=["Pull Requests"],
    dependencies=[Depends(verify_api_key)],
)

# Darwin Pipeline routes
app.include_router(
    darwin.router,
    prefix="/api/darwin",
    tags=["Darwin Pipeline"],
    dependencies=[Depends(verify_api_key)],
)

# Statistics routes
app.include_router(
    stats.router,
    prefix="/api/stats",
    tags=["Statistics"],
    dependencies=[Depends(verify_api_key)],
)


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unexpected errors gracefully."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        },
    )


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    print("🚀 Darwin API starting up...")
    print("📖 API Docs: http://localhost:8000/docs")
    print("🔑 API Key authentication enabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    print("👋 Darwin API shutting down...")
