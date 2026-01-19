"""User-related API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.database import User

router = APIRouter()


@router.get("/me")
async def get_current_user(db: Session = Depends(get_db)):
    """Get current user profile."""
    # TODO: Get user from JWT token
    return {"message": "Current user endpoint - JWT authentication required"}


@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Don't return password hash
    return {
        "id": user.id,
        "username": user.username,
        "name": user.name,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at
    }


@router.put("/me")
async def update_user(
    name: str = None,
    bio: str = None,
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    # TODO: Get current user from JWT
    return {"message": "Update user endpoint - JWT authentication required"}


@router.post("/{user_id}/follow")
async def follow_user(user_id: int, db: Session = Depends(get_db)):
    """Follow/unfollow a user."""
    # TODO: Implement follow functionality
    return {"message": "Follow endpoint - to be implemented"}
