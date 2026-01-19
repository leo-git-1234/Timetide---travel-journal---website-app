"""Entry-related API routes."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional

from app.models import get_db
from app.models.database import Entry, Photo, Like, User, Location, Trip
from app.core.security import decode_token

router = APIRouter()


# Pydantic Schemas
class LocationCreate(BaseModel):
    """Schema for creating a location."""
    place_name: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class PhotoCreate(BaseModel):
    """Schema for creating a photo."""
    url: str
    caption: Optional[str] = None
    order: int = 0


class EntryCreate(BaseModel):
    """Schema for creating an entry."""
    trip_id: int
    content: str = Field(..., min_length=1)
    entry_date: date
    entry_time: Optional[str] = None
    location: Optional[LocationCreate] = None
    photos: Optional[List[PhotoCreate]] = []


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


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_entry(
    entry_data: EntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    """Create a new entry with photos and optional location."""
    # Verify trip exists and user has access
    trip = db.query(Trip).filter(Trip.id == entry_data.trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    # Check if user is owner or family member
    if trip.owner_id != current_user.id:
        # TODO: Also check if user is in trip's family
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add entries to this trip")
    
    # Create location if provided
    location = None
    if entry_data.location:
        location = Location(
            place_name=entry_data.location.place_name,
            latitude=entry_data.location.latitude,
            longitude=entry_data.location.longitude
        )
        db.add(location)
        db.flush()  # Get location ID
    
    # Create entry
    entry = Entry(
        trip_id=entry_data.trip_id,
        content=entry_data.content,
        entry_date=entry_data.entry_date,
        entry_time=entry_data.entry_time,
        author_id=current_user.id,
        location_id=location.id if location else None
    )
    db.add(entry)
    db.flush()  # Get entry ID
    
    # Add photos if provided
    if entry_data.photos:
        for photo_data in entry_data.photos:
            photo = Photo(
                entry_id=entry.id,
                url=photo_data.url,
                caption=photo_data.caption,
                order=photo_data.order
            )
            db.add(photo)
    
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
