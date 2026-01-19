#!/usr/bin/env python3
"""Initialize test data for Timetide."""

import sys
from datetime import date

# Add the project to the path
sys.path.insert(0, '/timetide')

from app.models.database import Base, User, Trip
from app.models import SessionLocal, engine
from app.auth.jwt import get_password_hash

# Create tables
Base.metadata.create_all(engine)

# Create session
db = SessionLocal()

# Create test user
user = User(
    email="test@example.com",
    username="testuser",
    name="Test User",
    hashed_password=get_password_hash("password123")
)
db.add(user)
db.commit()
db.refresh(user)

# Create test trip
trip = Trip(
    title="Test Trip",
    location="New York",
    description="A test trip",
    start_date=date(2025, 1, 15),
    end_date=date(2025, 1, 20),
    owner_id=user.id
)
db.add(trip)
db.commit()

print(f"✓ User created: {user.email}")
print(f"✓ Trip created: {trip.title}")
print("✓ Database initialized successfully!")

db.close()
