#!/usr/bin/env python3
"""Create a test user for development."""

from app.models import SessionLocal, engine
from app.models.database import User, Base
from app.core.security import get_password_hash
from datetime import datetime

# Initialize database
Base.metadata.create_all(bind=engine)

# Create session
db = SessionLocal()

try:
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "leoyfliu@gmail.com").first()
    
    if existing_user:
        print(f"User {existing_user.email} already exists!")
        print("Updating password to: 26mana26")
        existing_user.hashed_password = get_password_hash("26mana26")
        db.commit()
        print(f"✅ Password updated!")
        print(f"Email: {existing_user.email}")
        print(f"Password: 26mana26")
    else:
        # Create new user
        new_user = User(
            email="leoyfliu@gmail.com",
            username="leoyfliu",
            name="Leo Liu",
            hashed_password=get_password_hash("26mana26"),  # Your original password
            bio="Travel enthusiast documenting journeys",
            is_profile_public=False,
            language="en",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"✅ User created successfully!")
        print(f"Email: {new_user.email}")
        print(f"Username: {new_user.username}")
        print(f"Password: 26mana26")
        print(f"\nYou can now login with these credentials.")

finally:
    db.close()
