#!/usr/bin/env python3

import sys
import os

# Try to start the server
print("=== Timetide Server Startup ===")
print(f"Working directory: {os.getcwd()}")
print(f"Python: {sys.executable}")

try:
    print("\n1. Importing uvicorn...")
    import uvicorn
    print("   ✓ uvicorn imported")
    
    print("\n2. Importing FastAPI app...")
    from app.main import app
    print("   ✓ app imported")
    
    print("\n3. Starting server on 127.0.0.1:8000...")
    # Run directly without catching exceptions
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )
except KeyboardInterrupt:
    print("\n\nServer interrupted by user")
    sys.exit(0)
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   Message: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
