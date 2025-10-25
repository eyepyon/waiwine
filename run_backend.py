#!/usr/bin/env python3
"""
Backend server runner script.
Run this from the project root directory.
"""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import and run the backend
from backend.api_app import app
import uvicorn

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    print(f"🚀 Starting Wai Wine backend server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )