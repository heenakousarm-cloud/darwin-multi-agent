#!/usr/bin/env python3
"""
Darwin API Server Runner

This script starts the Darwin API server using uvicorn.

Usage:
    python scripts/run_api.py [--port PORT] [--host HOST] [--reload]
    
Examples:
    python scripts/run_api.py                    # Start on localhost:8000
    python scripts/run_api.py --port 3000        # Start on localhost:3000
    python scripts/run_api.py --reload           # Start with auto-reload (dev)
    python scripts/run_api.py --host 0.0.0.0     # Allow external connections
"""

import os
import sys
import argparse

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, ".env"))


def main():
    parser = argparse.ArgumentParser(
        description="Start the Darwin API server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/run_api.py                    # Start on localhost:8000
    python scripts/run_api.py --port 3000        # Start on localhost:3000
    python scripts/run_api.py --reload           # Start with auto-reload (dev)
    python scripts/run_api.py --host 0.0.0.0     # Allow external connections
        """
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    # Check for API key
    api_key = os.getenv("DARWIN_API_KEY")
    if not api_key:
        print("⚠️  Warning: DARWIN_API_KEY not set in environment")
        print("   API authentication will fail!")
        print("   Add DARWIN_API_KEY to your .env file")
        print()
    else:
        print(f"🔑 API Key configured: {api_key[:15]}...")
    
    # Print startup info
    print()
    print("=" * 60)
    print("🧬 Darwin API Server")
    print("=" * 60)
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Reload: {args.reload}")
    print()
    print(f"📍 API URL: http://{args.host}:{args.port}")
    print(f"📖 API Docs: http://{args.host}:{args.port}/docs")
    print(f"❤️  Health: http://{args.host}:{args.port}/health")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    # Import and run uvicorn
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
