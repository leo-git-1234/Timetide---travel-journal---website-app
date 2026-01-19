#!/usr/bin/env python3
"""Test the trips endpoint."""

import requests
import json
from datetime import datetime

# First, login to get a token
login_response = requests.post(
    "http://127.0.0.1:8000/auth/login",
    data={"username": "test@example.com", "password": "password123"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
else:
    print(f"✓ Login successful")
    cookies = login_response.cookies
    
    # Now test the trips endpoint
    trips_response = requests.get(
        "http://127.0.0.1:8000/trips/",
        cookies=cookies
    )
    
    if trips_response.status_code != 200:
        print(f"❌ Trips endpoint failed: {trips_response.status_code}")
        print(trips_response.text)
    else:
        print(f"✓ Trips endpoint successful")
        trips = trips_response.json()
        print(f"\nTrips data:")
        print(json.dumps(trips, indent=2, default=str))
