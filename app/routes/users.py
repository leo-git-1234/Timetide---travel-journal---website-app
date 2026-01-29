"""User-related API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.models import get_db
from app.models.database import User, Trip, Entry
from app.auth.dependencies import get_current_user
from app.core.security import get_password_hash, verify_password

router = APIRouter()


# Pydantic schemas
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class ChangeEmailRequest(BaseModel):
    new_email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ChangeUsernameRequest(BaseModel):
    new_username: str
    password: str


class ProfileVisibilityUpdate(BaseModel):
    is_profile_public: bool


@router.get("/me")
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "name": current_user.name,
        "bio": current_user.bio,
        "avatar_url": current_user.avatar_url,
        "is_profile_public": current_user.is_profile_public,
        "created_at": current_user.created_at,
    }


@router.get("/me/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user statistics including trip and entry counts."""
    num_trips = db.query(Trip).filter(Trip.owner_id == current_user.id).count()
    num_entries = db.query(Entry).filter(Entry.author_id == current_user.id).count()
    num_families = len(current_user.families)
    
    return {
        "trips": num_trips,
        "entries": num_entries,
        "families": num_families
    }


@router.get("/me/recent-activity")
async def get_recent_activity(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """Get user's recent journal entries (latest journaling moments)."""
    entries = (
        db.query(Entry)
        .filter(Entry.author_id == current_user.id)
        .order_by(Entry.created_at.desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": entry.id,
            "trip_id": entry.trip_id,
            "trip_title": entry.trip.title if entry.trip else "Unknown Trip",
            "content": entry.content[:200] + "..." if len(entry.content) > 200 else entry.content,
            "entry_date": entry.entry_date,
            "entry_time": entry.entry_time,
            "created_at": entry.created_at,
            "photos_count": len(entry.photos),
            "first_photo": entry.photos[0].url if entry.photos else None
        }
        for entry in entries
    ]


@router.put("/me/profile")
async def update_profile(
    update_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile information."""
    if update_data.name:
        current_user.name = update_data.name.strip()
    
    if update_data.bio is not None:
        current_user.bio = update_data.bio.strip() if update_data.bio else None
    
    if update_data.avatar_url is not None:
        current_user.avatar_url = update_data.avatar_url if update_data.avatar_url else None
    
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "name": current_user.name,
        "bio": current_user.bio,
        "avatar_url": current_user.avatar_url,
        "message": "Profile updated successfully"
    }


@router.post("/me/change-email")
async def change_email(
    request: ChangeEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user's email address."""
    # Verify current password
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    # Check if new email is already in use
    existing_user = db.query(User).filter(User.email == request.new_email.lower()).first()
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use by another account"
        )
    
    current_user.email = request.new_email.lower()
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Email changed successfully", "email": current_user.email}


@router.post("/me/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user's password."""
    # Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
    
    # Validate new password
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters"
        )
    
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/me/change-username")
async def change_username(
    request: ChangeUsernameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user's username."""
    # Verify password
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    # Validate new username
    if len(request.new_username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters"
        )
    
    # Check if username is already taken
    existing_user = db.query(User).filter(User.username == request.new_username.lower()).first()
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    current_user.username = request.new_username.lower()
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Username changed successfully", "username": current_user.username}


@router.put("/me/profile-visibility")
async def update_profile_visibility(
    update_data: ProfileVisibilityUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update profile visibility setting."""
    current_user.is_profile_public = update_data.is_profile_public
    db.commit()
    
    visibility_status = "public" if update_data.is_profile_public else "private"
    return {"message": f"Profile is now {visibility_status}", "is_profile_public": update_data.is_profile_public}


@router.delete("/me")
async def delete_account(
    password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account and all associated data."""
    # Verify password
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    user_id = current_user.id
    db.delete(current_user)
    db.commit()
    
    return {"message": "Account deleted successfully"}


@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get public user profile by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_profile_public:
        raise HTTPException(status_code=403, detail="This profile is private")
    
    # Return public profile info
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at
    }


@router.post("/{user_id}/follow")
async def follow_user(user_id: int, db: Session = Depends(get_db)):
    """Follow/unfollow a user."""
    # TODO: Implement follow functionality
    return {"message": "Follow endpoint - to be implemented"}
