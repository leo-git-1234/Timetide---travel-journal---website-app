"""Trip-related API routes with owner-based access control."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field

from app.models import get_db
from app.models.database import Trip, User, TripMedia
from app.core.security import decode_token
from fastapi import Request, Cookie
from typing import Optional, List


# Pydantic Schemas
class TripCreate(BaseModel):
    """Schema for creating a new trip."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    start_date: date
    end_date: date
    cover_image: Optional[str] = Field(None, max_length=2000)  # Can be base64
    media_files: Optional[List[dict]] = Field(None)  # List of {url, type, name}


class TripUpdate(BaseModel):
    """Schema for updating a trip."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    cover_image: Optional[str] = Field(None, max_length=500)


class TripOut(BaseModel):
    """Schema for trip response."""
    id: int
    title: str
    description: Optional[str]
    start_date: date
    end_date: date
    cover_image: Optional[str]
    owner_id: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


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


@router.get("/", response_model=List[TripOut])
async def get_trips(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie)):
    """Get all trips for the current user."""
    trips = db.query(Trip).filter(Trip.owner_id == current_user.id).order_by(Trip.start_date.desc()).all()
    return trips


@router.get("/{trip_id}", response_model=TripOut)
async def get_trip(trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie)):
    """Get a single trip by ID. Users can only access their own trips."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    # Enforce ownership
    if trip.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to access this trip")
    
    return trip


@router.post("/", response_model=TripOut, status_code=status.HTTP_201_CREATED)
async def create_trip(trip_data: TripCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie)):
    """Create a new trip for the current user."""
    # Validate dates
    if trip_data.end_date < trip_data.start_date:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End date must be after start date")
    
    trip = Trip(
        title=trip_data.title,
        description=trip_data.description,
        start_date=trip_data.start_date,
        end_date=trip_data.end_date,
        cover_image=trip_data.cover_image,
        owner_id=current_user.id,
        location="Location TBA"  # Placeholder, can be extracted from entries later
    )
    db.add(trip)
    db.flush()  # Get the trip ID without committing yet
    
    # Add media files if provided
    if trip_data.media_files:
        for idx, media_file in enumerate(trip_data.media_files):
            media = TripMedia(
                trip_id=trip.id,
                url=media_file.get('url'),
                media_type=media_file.get('type', 'image'),
                file_name=media_file.get('name'),
                order=idx
            )
            db.add(media)
    
    db.commit()
    db.refresh(trip)
    return trip


@router.put("/{trip_id}", response_model=TripOut)
async def update_trip(trip_id: int, trip_data: TripUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie)):
    """Update an existing trip. Only the owner can update."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    # Enforce ownership
    if trip.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to update this trip")
    
    # Validate dates if both provided
    if trip_data.start_date and trip_data.end_date:
        if trip_data.end_date < trip_data.start_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="End date must be after start date")
    
    # Update only provided fields
    if trip_data.title is not None:
        trip.title = trip_data.title
    if trip_data.description is not None:
        trip.description = trip_data.description
    if trip_data.start_date is not None:
        trip.start_date = trip_data.start_date
    if trip_data.end_date is not None:
        trip.end_date = trip_data.end_date
    if trip_data.cover_image is not None:
        trip.cover_image = trip_data.cover_image
    
    db.commit()
    db.refresh(trip)
    return trip


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(trip_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie)):
    """Delete a trip. Only the owner can delete."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    # Enforce ownership
    if trip.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to delete this trip")
    
    db.delete(trip)
    db.commit()
    return None
