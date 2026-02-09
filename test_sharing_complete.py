"""
Comprehensive test for the trip sharing functionality.
Tests all endpoints and permission checks.
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_sharing_system():
    """Test the complete sharing system."""
    
    # Test 1: Login as User 1 (tripowner)
    print("\n=== Test 1: Login as User 1 (tripowner) ===")
    response = requests.post(f"{BASE_URL}/login", data={
        "email": "tripowner@example.com",
        "password": "password123"
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user1_token = response.cookies.get('access_token')
        print(f"✓ User 1 logged in, token: {user1_token[:20]}...")
    else:
        print(f"✗ Failed to login User 1: {response.text}")
        return
    
    # Test 2: Get User 1's trips
    print("\n=== Test 2: Get User 1's trips ===")
    headers = {"Authorization": f"Bearer {user1_token}"}
    response = requests.get(f"{BASE_URL}/trips/", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        trips = response.json()
        print(f"✓ Got {len(trips)} trips")
        if trips:
            trip_id = trips[0]['id']
            trip_title = trips[0]['title']
            print(f"  Using Trip: {trip_id} - {trip_title}")
        else:
            print("✗ No trips available to share")
            return
    else:
        print(f"✗ Failed to get trips: {response.text}")
        return
    
    # Test 3: Login as User 2 (tripreceiver)
    print("\n=== Test 3: Login as User 2 (tripreceiver) ===")
    response = requests.post(f"{BASE_URL}/login", data={
        "email": "tripreceiver@example.com",
        "password": "password123"
    })
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        user2_token = response.cookies.get('access_token')
        print(f"✓ User 2 logged in, token: {user2_token[:20]}...")
    else:
        print(f"✗ Failed to login User 2: {response.text}")
        return
    
    # Test 4: Share trip with User 2 (as User 1)
    print("\n=== Test 4: Share trip with User 2 ===")
    headers1 = {"Authorization": f"Bearer {user1_token}", "Content-Type": "application/json"}
    response = requests.post(
        f"{BASE_URL}/sharing/trips/{trip_id}/share",
        headers=headers1,
        json={
            "email": "tripreceiver@example.com",
            "permission_level": "editor"
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        invite_data = response.json()
        invite_id = invite_data['id']
        print(f"✓ Invite created with ID: {invite_id}")
        print(f"  Status: {invite_data['status']}")
        print(f"  Permission: {invite_data['permission_level']}")
    else:
        print(f"✗ Failed to share trip: {response.text}")
        return
    
    # Test 5: User 2 checks pending invites
    print("\n=== Test 5: User 2 checks pending invites ===")
    headers2 = {"Authorization": f"Bearer {user2_token}"}
    response = requests.get(f"{BASE_URL}/sharing/invites", headers=headers2)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        invites_data = response.json()
        pending = invites_data.get('pending', [])
        print(f"✓ Got invites grouped by status")
        print(f"  Pending: {len(pending)}")
        print(f"  Accepted: {len(invites_data.get('accepted', []))}")
        print(f"  Declined: {len(invites_data.get('declined', []))}")
        if pending:
            print(f"  First pending invite: Trip '{pending[0]['trip_title']}'")
    else:
        print(f"✗ Failed to get invites: {response.text}")
        return
    
    # Test 6: User 2 cannot access trip before accepting
    print("\n=== Test 6: User 2 cannot access trip before accepting ===")
    response = requests.get(f"{BASE_URL}/trips/{trip_id}", headers=headers2)
    print(f"Status: {response.status_code}")
    if response.status_code == 403:
        print(f"✓ Correctly denied access (403)")
    else:
        print(f"✗ Should be 403 but got {response.status_code}")
    
    # Test 7: User 2 accepts the invite
    print("\n=== Test 7: User 2 accepts the invite ===")
    response = requests.put(
        f"{BASE_URL}/sharing/invites/{invite_id}/accept",
        headers=headers2,
        json={}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        invite_updated = response.json()
        print(f"✓ Invite accepted")
        print(f"  Status: {invite_updated['status']}")
    else:
        print(f"✗ Failed to accept invite: {response.text}")
        return
    
    # Test 8: User 2 can now access the shared trip
    print("\n=== Test 8: User 2 can now access the shared trip ===")
    response = requests.get(f"{BASE_URL}/trips/{trip_id}", headers=headers2)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        trip = response.json()
        print(f"✓ Trip accessible: {trip['title']}")
    else:
        print(f"✗ Trip not accessible: {response.text}")
        return
    
    # Test 9: User 2 (editor) can create entries on shared trip
    print("\n=== Test 9: User 2 (editor) can create entries ===")
    response = requests.post(
        f"{BASE_URL}/entries/",
        headers={"Authorization": f"Bearer {user2_token}", "Content-Type": "application/json"},
        json={
            "trip_id": trip_id,
            "content": "Test entry from shared user",
            "date": "2024-01-15",
            "mood": 5
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print(f"✓ Entry created by shared editor user")
    else:
        print(f"✗ Failed to create entry: {response.text}")
    
    # Test 10: User 2 sees trip in their shared trips
    print("\n=== Test 10: User 2 sees trip in their shared trips ===")
    response = requests.get(f"{BASE_URL}/trips/", headers=headers2)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        all_trips = response.json()
        shared_found = any(t['id'] == trip_id for t in all_trips)
        if shared_found:
            print(f"✓ Shared trip appears in User 2's trip list")
        else:
            print(f"✗ Shared trip NOT in User 2's trip list")
    
    # Test 11: User 1 (owner) can see who it's shared with
    print("\n=== Test 11: User 1 can see shared recipients ===")
    response = requests.get(
        f"{BASE_URL}/sharing/trips/{trip_id}/shared-with",
        headers=headers1
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        shared_with = response.json()
        print(f"✓ Shared with: {len(shared_with)} users")
        if shared_with:
            print(f"  - {shared_with[0]['invitee_email']} ({shared_with[0]['permission_level']})")
    else:
        print(f"✗ Failed to get shared-with info: {response.text}")
    
    # Test 12: User 1 can revoke access
    print("\n=== Test 12: User 1 revokes access ===")
    response = requests.delete(
        f"{BASE_URL}/sharing/trips/{trip_id}/shared-with/{invite_id}",
        headers=headers1
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Access revoked")
    else:
        print(f"✗ Failed to revoke access: {response.text}")
    
    # Test 13: User 2 can no longer access trip after revoke
    print("\n=== Test 13: User 2 cannot access trip after revoke ===")
    response = requests.get(f"{BASE_URL}/trips/{trip_id}", headers=headers2)
    print(f"Status: {response.status_code}")
    if response.status_code == 403:
        print(f"✓ Correctly denied access after revoke (403)")
    else:
        print(f"✗ Should be 403 but got {response.status_code}")
    
    print("\n=== All tests completed! ===\n")

if __name__ == "__main__":
    print("Starting comprehensive sharing system tests...")
    test_sharing_system()
