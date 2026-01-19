#!/usr/bin/env python3
"""Run Uvicorn directly with error handling."""

import uvicorn
import sys

try:
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="debug"
    )
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)
