#!/usr/bin/env python3
"""Test without leaving server."""

import time
time.sleep(2)

import requests

try:
    # Login
    print("Testing login...", flush=True)
    login_response = requests.post(
        "http://127.0.0.1:8001/auth/login",
        data={"username": "test@example.com", "password": "password123"},
        timeout=5
    )
    print(f"Login: {login_response.status_code}", flush=True)
    
    if login_response.status_code == 200:
        # Test trips
        print("Testing /trips/...", flush=True)
        trips_response = requests.get(
            "http://127.0.0.1:8001/trips/",
            cookies=login_response.cookies,
            timeout=5
        )
        print(f"Trips: {trips_response.status_code}", flush=True)
        
        if trips_response.status_code == 200:
            print("✓ SUCCESS - Trips endpoint is working!", flush=True)
            import json
            print(json.dumps(trips_response.json(), indent=2, default=str), flush=True)
        else:
            print(f"✗ Trips failed: {trips_response.text}", flush=True)
    else:
        print(f"✗ Login failed: {login_response.text}", flush=True)
except Exception as e:
    print(f"Error: {e}", flush=True)
    import traceback
    traceback.print_exc()
