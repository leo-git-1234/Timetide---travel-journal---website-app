#!/usr/bin/env python3
"""Test trips endpoint on port 8001."""

import requests
import json

# Login
login_response = requests.post(
    "http://127.0.0.1:8001/auth/login",
    data={"username": "test@example.com", "password": "password123"}
)

print(f"Login Status: {login_response.status_code}")

if login_response.status_code == 200:
    cookies = login_response.cookies
    
    # Test trips
    trips_response = requests.get(
        "http://127.0.0.1:8001/trips/",
        cookies=cookies
    )
    
    print(f"Trips Status: {trips_response.status_code}")
    if trips_response.status_code == 200:
        print("✓ Trips endpoint working!")
        trips = trips_response.json()
        print(json.dumps(trips, indent=2, default=str))
    else:
        print(f"✗ Trips failed: {trips_response.text}")
else:
    print(f"✗ Login failed: {login_response.text}")
