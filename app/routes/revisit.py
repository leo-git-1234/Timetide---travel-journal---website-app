"""Revisit page route - Memory-driven reflection of past journeys."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import get_db
from app.models.database import Trip, User, Entry, TripFavorite
from app.core.security import decode_token as decode_token_core
from app.auth.jwt import decode_token as decode_token_legacy
from fastapi import Cookie
import os
import random

router = APIRouter(prefix="", tags=["pages"])

# Setup Jinja2 templates
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


def get_current_user_from_cookie(request: Request, timetide_token: str = Cookie(None), db: Session = Depends(get_db)):
    """Extract and validate user from cookie."""
    if not timetide_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        user_data = decode_token_core(timetide_token)
    except:
        try:
            user_data = decode_token_legacy(timetide_token)
        except:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = user_data.get('sub')
    if user_id:
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            pass
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.get("/revisit")
async def revisit_page(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Render the Revisit page."""
    
    # Get all user trips
    all_trips = db.query(Trip).filter(Trip.owner_id == current_user.id).all()
    
    if not all_trips:
        return templates.TemplateResponse("revisit.html", {
            "request": request,
            "current_user": current_user,
            "active_page": "revisit",
            "page_title": "Recent Highlight",
            "page_subtitle": "A window back into your memories.",
            "featured_trip": None,
            "trips_by_year": [],
            "recent_trips": [],
            "past_journeys": []
        })
    
    # Add favorite status to each trip
    for trip in all_trips:
        # Check if favorite
        favorite = db.query(TripFavorite).filter(
            TripFavorite.trip_id == trip.id,
            TripFavorite.user_id == current_user.id
        ).first()
        trip.is_favorite = favorite is not None
    
    # Select a random featured trip
    featured_trip = random.choice(all_trips)
    page_title = "Revisit"
    page_subtitle = "Discover moments from your journeys."
    
    # Get trips by year for "Places That Spanned Years" (first trip per year, including all years)
    trips_by_year_dict = {}
    for trip in all_trips:
        try:
            trip_start = datetime.strptime(str(trip.start_date), '%Y-%m-%d')
        except:
            trip_start = datetime.fromisoformat(str(trip.start_date))
        year = trip_start.year
        if year not in trips_by_year_dict:
            trips_by_year_dict[year] = trip
    
    trips_by_year = [
        {"year": year, "trip": trip}
        for year, trip in sorted(trips_by_year_dict.items(), key=lambda x: x[0], reverse=True)
    ]  # Show all years
    
    # Get recent trips (all trips sorted by date, limited to 5)
    try:
        sorted_trips = sorted(all_trips, key=lambda t: datetime.strptime(str(t.start_date), '%Y-%m-%d'), reverse=True)
    except:
        sorted_trips = sorted(all_trips, key=lambda t: datetime.fromisoformat(str(t.start_date)), reverse=True)
    
    recent_trips = sorted_trips[:5]
    
    # Get trips grouped by year for "Past Journeys" (all trips)
    trips_by_year_dict_all = {}
    for trip in all_trips:
        try:
            trip_start = datetime.strptime(str(trip.start_date), '%Y-%m-%d')
        except:
            trip_start = datetime.fromisoformat(str(trip.start_date))
        year = trip_start.year
        if year not in trips_by_year_dict_all:
            trips_by_year_dict_all[year] = []
        trips_by_year_dict_all[year].append(trip)
    
    past_journeys = []
    for year, trips in sorted(trips_by_year_dict_all.items(), key=lambda x: x[0], reverse=True):
        try:
            sorted_trips = sorted(trips, key=lambda t: datetime.strptime(str(t.start_date), '%Y-%m-%d'), reverse=True)
        except:
            sorted_trips = sorted(trips, key=lambda t: datetime.fromisoformat(str(t.start_date)), reverse=True)
        if sorted_trips:  # Only add if there are trips for this year
            past_journeys.append({
                "year": year,
                "trips": sorted_trips[:5]  # Limit to 5 trips per year
            })
    
    return templates.TemplateResponse("revisit.html", {
        "request": request,
        "current_user": current_user,
        "active_page": "revisit",
        "page_title": page_title,
        "page_subtitle": page_subtitle,
        "featured_trip": featured_trip,
        "trips_by_year": trips_by_year,
        "recent_trips": recent_trips,
        "past_journeys": past_journeys
    })
