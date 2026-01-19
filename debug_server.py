#!/usr/bin/env python3
"""Debug server startup."""

import uvicorn
import sys
import traceback

print("Starting server debug...", flush=True)

try:
    print("Importing app...", flush=True)
    from app.main import app
    print("App imported successfully", flush=True)
    
    print("Running uvicorn...", flush=True)
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        log_level="info"
    )
except KeyboardInterrupt:
    print("Server interrupted")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}", flush=True)
    traceback.print_exc()
    sys.exit(1)
