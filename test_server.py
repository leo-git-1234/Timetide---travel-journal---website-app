#!/usr/bin/env python3
"""Simple HTTP test script."""

import subprocess
import time
import requests
import sys

# Start the server in the background
print("Starting server...")
server = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd="c:\\timetide"
)

# Wait for server to start
print("Waiting for server to start...")
time.sleep(5)

try:
    # Test login
    print("Testing login...")
    response = requests.post(
        "http://127.0.0.1:8000/auth/login",
        data={"username": "test@example.com", "password": "password123"},
        timeout=5
    )
    print(f"Login status: {response.status_code}")
    print(f"Login response: {response.text[:200]}")
    
    # Get cookie
    if response.status_code == 200:
        cookies = response.cookies
        
        # Test trips
        print("\nTesting trips endpoint...")
        trips_response = requests.get(
            "http://127.0.0.1:8000/trips/",
            cookies=cookies,
            timeout=5
        )
        print(f"Trips status: {trips_response.status_code}")
        print(f"Trips response: {trips_response.text}")
    
except Exception as e:
    print(f"Error: {e}")

finally:
    print("\nShutting down server...")
    server.terminate()
    server.wait()
