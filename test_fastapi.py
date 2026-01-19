#!/usr/bin/env python3
"""Direct FastAPI test."""

import sys
from app.main import app

if __name__ == "__main__":
    # Try to trigger any import errors
    print(f"FastAPI app loaded: {app}")
    print(f"Routes count: {len(app.routes)}")
    print("Routers included successfully")
    
    # List all routes
    for route in app.routes:
        print(f"  - {route}")
