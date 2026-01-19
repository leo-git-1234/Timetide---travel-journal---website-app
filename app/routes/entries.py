"""Entry-related API routes."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import date

from app.models import get_db
from app.models.database import Entry, Photo, Like, User
from app.core.security import decode_token

router = APIRouter()


# Helper function to get current user from cookies
async def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> User:
    """Extract and verify user from JWT token in cookies."""
    # Get token from cookie
    token = request.cookies.get("timetide_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    # Decode token
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


@router.get("/trip/{trip_id}")
async def get_trip_entries(trip_id: int, db: Session = Depends(get_db)):
    """Get all entries for a trip."""
    entries = db.query(Entry).filter(Entry.trip_id == trip_id).all()
    return entries


@router.get("/{entry_id}")
async def get_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get a single entry by ID."""
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.post("/")
async def create_entry(
    trip_id: int,
    content: str,
    entry_date: date,
    entry_time: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Create a new entry."""
    entry = Entry(
        trip_id=trip_id,
        content=content,
        entry_date=entry_date,
        entry_time=entry_time,
        author_id=current_user.id
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.put("/{entry_id}")
async def update_entry(
    entry_id: int,
    content: str = None,
    entry_time: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Update an existing entry."""
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # Ensure only author can update
    if entry.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not permitted to edit this entry")
    
    if content:
        entry.content = content
    if entry_time:
        entry.entry_time = entry_time
    
    db.commit()
    db.refresh(entry)
    return entry


@router.delete("/{entry_id}")
async def delete_entry(entry_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie)):
    """Delete an entry."""
    entry = db.query(Entry).filter(Entry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    if entry.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not permitted to delete this entry")
    
    db.delete(entry)
    db.commit()
    return {"message": "Entry deleted successfully"}


@router.post("/{entry_id}/like")
async def like_entry(entry_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie)):
    """Like an entry (quiet acknowledgement)."""
    user_id = current_user.id
    
    # Check if already liked
    existing_like = db.query(Like).filter(
        Like.entry_id == entry_id,
        Like.user_id == user_id
    ).first()
    
    if existing_like:
        # Unlike
        db.delete(existing_like)
        db.commit()
        return {"message": "Like removed", "liked": False}
    else:
        # Like
        like = Like(entry_id=entry_id, user_id=user_id)
        db.add(like)
        db.commit()
        return {"message": "Entry liked", "liked": True}
