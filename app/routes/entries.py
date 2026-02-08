"""Entry-related API routes."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional
import base64
import io
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from app.models import get_db
from app.models.database import Entry, Photo, Like, User, Location, Trip
from app.core.security import decode_token as decode_token_core
from app.auth.jwt import decode_token as decode_token_legacy

router = APIRouter()


# Helper functions for GPS extraction
def get_decimal_from_dms(dms, ref):
    """Convert GPS coordinates from DMS to decimal format."""
    try:
        degrees = float(dms[0])
        minutes = float(dms[1])
        seconds = float(dms[2])
        
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        
        if ref in ['S', 'W']:
            decimal = -decimal
        
        return decimal
    except (IndexError, TypeError, ValueError):
        return None


def extract_gps_from_image(image_data_url: str) -> dict:
    """Extract GPS coordinates from image EXIF data."""
    try:
        # Remove data URL prefix
        if ',' in image_data_url:
            image_data = image_data_url.split(',', 1)[1]
        else:
            image_data = image_data_url
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Get EXIF data
        exif_data = image._getexif()
        if not exif_data:
            return {"latitude": None, "longitude": None}
        
        # Extract GPS info
        gps_info = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == "GPSInfo":
                for gps_tag in value:
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[gps_tag_name] = value[gps_tag]
        
        if not gps_info:
            return {"latitude": None, "longitude": None}
        
        # Extract latitude
        latitude = None
        if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
            latitude = get_decimal_from_dms(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
        
        # Extract longitude
        longitude = None
        if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
            longitude = get_decimal_from_dms(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
        
        return {
            "latitude": str(latitude) if latitude is not None else None,
            "longitude": str(longitude) if longitude is not None else None
        }
    
    except Exception as e:
        print(f"Error extracting GPS data: {e}")
        return {"latitude": None, "longitude": None}


def extract_metadata_from_image(image_data_url: str) -> dict:
    """Extract comprehensive metadata from image EXIF data (GPS, date, time, location)."""
    try:
        # Remove data URL prefix
        if ',' in image_data_url:
            image_data = image_data_url.split(',', 1)[1]
        else:
            image_data = image_data_url
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Get EXIF data
        exif_data = image._getexif()
        result = {
            "latitude": None,
            "longitude": None,
            "date": None,
            "time": None,
            "place_name": None
        }
        
        if not exif_data:
            return result
        
        # Extract datetime
        datetime_value = None
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                datetime_value = value
                break
        
        if datetime_value:
            try:
                # Handle various datetime formats from EXIF
                datetime_value = str(datetime_value).strip()
                
                # Try standard format first: "YYYY:MM:DD HH:MM:SS"
                if ' ' in datetime_value and ':' in datetime_value:
                    parts = datetime_value.split(' ', 1)
                    date_part = parts[0]
                    time_part = parts[1] if len(parts) > 1 else None
                    
                    # Convert date from YYYY:MM:DD to YYYY-MM-DD
                    if ':' in date_part and len(date_part) == 10:
                        formatted_date = date_part.replace(':', '-')
                        # Validate the date format (YYYY-MM-DD)
                        if len(formatted_date) == 10 and formatted_date[4] == '-' and formatted_date[7] == '-':
                            result["date"] = formatted_date
                    
                    # Keep time as is if valid (HH:MM:SS format)
                    if time_part and time_part.count(':') == 2:
                        time_part = time_part.strip()
                        # Validate time format (HH:MM:SS)
                        if len(time_part) >= 5 and time_part[2] == ':' and time_part[5] == ':':
                            result["time"] = time_part
                
                # Fallback: try parsing just the date part even without time
                elif ':' in datetime_value and len(datetime_value) >= 10:
                    date_part = datetime_value[:10]
                    if ':' in date_part and len(date_part) == 10:
                        formatted_date = date_part.replace(':', '-')
                        # Validate the date format
                        if len(formatted_date) == 10 and formatted_date[4] == '-' and formatted_date[7] == '-':
                            result["date"] = formatted_date
                    
                    # Try to get time from the remaining part
                    if len(datetime_value) > 11:
                        time_part = datetime_value[11:].strip()
                        if time_part and time_part.count(':') == 2:
                            # Validate time format (HH:MM:SS)
                            if len(time_part) >= 5 and time_part[2] == ':' and time_part[5] == ':':
                                result["time"] = time_part
            except Exception as e:
                print(f"Error parsing datetime from EXIF: {e}")
                pass
        
        # Extract GPS info
        gps_info = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == "GPSInfo":
                for gps_tag in value:
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[gps_tag_name] = value[gps_tag]
        
        if gps_info:
            # Extract latitude
            if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
                latitude = get_decimal_from_dms(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
                if latitude is not None:
                    result["latitude"] = str(latitude)
            
            # Extract longitude
            if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
                longitude = get_decimal_from_dms(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
                if longitude is not None:
                    result["longitude"] = str(longitude)
            
            # Try to extract place name from GPS info if available
            # Some cameras store location info in GPSMapDatum or other fields
            if 'GPSMapDatum' in gps_info:
                result["place_name"] = str(gps_info.get('GPSMapDatum', '')).strip() or None
        
        return result
    
    except Exception as e:
        print(f"Error extracting metadata from image: {e}")
        return {
            "latitude": None,
            "longitude": None,
            "date": None,
            "time": None,
            "place_name": None
        }


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


class EntryUpdate(BaseModel):
    """Schema for updating an entry."""
    content: Optional[str] = Field(None, min_length=1)
    entry_date: Optional[date] = None
    entry_time: Optional[str] = None
    location: Optional[LocationCreate] = None
    photos: Optional[List[PhotoCreate]] = None


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
    payload = decode_token_core(token)
    if not payload:
        payload = decode_token_legacy(token)
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
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
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


@router.post("/extract-gps")
async def extract_gps_from_photo(photo_data: dict):
    """Extract GPS coordinates from a photo's EXIF data."""
    try:
        image_url = photo_data.get("image_url")
        if not image_url:
            return {"latitude": None, "longitude": None, "error": "No image data provided"}
        
        gps_data = extract_gps_from_image(image_url)
        return gps_data
    
    except Exception as e:
        print(f"Error in extract_gps_from_photo endpoint: {e}")
        return {"latitude": None, "longitude": None, "error": str(e)}


@router.post("/extract-metadata")
async def extract_metadata_from_photo(photo_data: dict):
    """Extract comprehensive metadata from a photo's EXIF data (date, time, location, GPS)."""
    try:
        image_url = photo_data.get("image_url")
        if not image_url:
            return {
                "latitude": None,
                "longitude": None,
                "date": None,
                "time": None,
                "place_name": None,
                "error": "No image data provided"
            }
        
        metadata = extract_metadata_from_image(image_url)
        return metadata
    
    except Exception as e:
        print(f"Error in extract_metadata_from_photo endpoint: {e}")
        return {
            "latitude": None,
            "longitude": None,
            "date": None,
            "time": None,
            "place_name": None,
            "error": str(e)
        }


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
    update_data: EntryUpdate,
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
    
    fields_set = getattr(update_data, "model_fields_set", None)
    if fields_set is None:
        fields_set = update_data.__fields_set__

    if update_data.content is not None:
        entry.content = update_data.content
    if update_data.entry_date is not None:
        entry.entry_date = update_data.entry_date
    if update_data.entry_time is not None:
        entry.entry_time = update_data.entry_time

    # Update location (allow clearing if explicitly provided as null)
    if "location" in fields_set:
        if update_data.location is None:
            entry.location_id = None
        else:
            if entry.location:
                entry.location.place_name = update_data.location.place_name
                entry.location.latitude = update_data.location.latitude
                entry.location.longitude = update_data.location.longitude
            else:
                location = Location(
                    place_name=update_data.location.place_name,
                    latitude=update_data.location.latitude,
                    longitude=update_data.location.longitude
                )
                db.add(location)
                db.flush()
                entry.location_id = location.id

    # Replace photos if provided (empty list clears all photos)
    if "photos" in fields_set:
        db.query(Photo).filter(Photo.entry_id == entry.id).delete()
        if update_data.photos:
            for photo_data in update_data.photos:
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
