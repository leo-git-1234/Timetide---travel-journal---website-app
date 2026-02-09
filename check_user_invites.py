#!/usr/bin/env python
"""Check invites for a specific user email."""
import sys
sys.path.insert(0, '.')
from app.models import SessionLocal
from app.models.database import User, Trip, TripInvite

db = SessionLocal()

# Find user by email
user = db.query(User).filter(User.email == 'lliu547@aucklanduni.ac.nz').first()
if user:
    print(f'User found: ID={user.id}, Email={user.email}, Name={user.name}')
    
    # Check for any invites for this user
    invites = db.query(TripInvite).filter(TripInvite.invitee_id == user.id).all()
    print(f'\nInvites for this user: {len(invites)}')
    for invite in invites:
        trip = db.query(Trip).filter(Trip.id == invite.trip_id).first()
        print(f'  Trip: {trip.title if trip else "Unknown"} (ID={invite.trip_id})')
        print(f'    Invite ID: {invite.id}')
        print(f'    Status: {invite.status}')
        print(f'    Permission: {invite.permission_level}')
else:
    print('User not found with that email')
    print('\nAll users in database:')
    all_users = db.query(User).all()
    for u in all_users:
        print(f'  {u.id}: {u.email}')

db.close()
