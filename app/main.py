"""
Timetide - Travel Diary Application
Main FastAPI application entry point
"""

from fastapi import FastAPI, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from app.models import init_db, get_db
from app.models.database import User, Trip, Entry
from app.routes import trips, entries, users
from app.routes import auth_jwt as auth_routes
from app.routes import my_trips
from app.auth.session import get_current_user_from_request

# Initialize FastAPI app
app = FastAPI(
    title="Timetide",
    description="A calm, premium travel diary for documenting journeys",
    version="1.0.0"
)

# Custom exception handler for Pydantic validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with user-friendly messages."""
    if exc.errors():
        errors = exc.errors()
        # For signup/login, show the first validation error
        first_error = errors[0]
        
        # Get field name from loc tuple (e.g., ('body', 'password') -> 'password')
        field = first_error.get('loc', ('unknown',))[-1] if first_error.get('loc') else 'unknown'
        
        # Get error message
        msg = first_error.get('msg', 'Invalid input')
        
        # Provide more user-friendly messages based on field and error type
        if field == 'email' and 'valid email' in msg.lower():
            detail = "Please enter a valid email address."
        elif field == 'password':
            detail = msg  # Use validation message from schema
        elif field == 'name':
            detail = "Name is required."
        else:
            detail = f"{field}: {msg}"
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": detail}
        )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "Validation error"}
    )

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Add custom Jinja2 filters
from datetime import timedelta
templates.env.globals['timedelta'] = timedelta

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()

# Include routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(trips.router, prefix="/trips", tags=["Trips"])
app.include_router(entries.router, prefix="/entries", tags=["Entries"])
app.include_router(my_trips.router, tags=["Pages"])


# ========================================
# PAGE ROUTES
# ========================================

@app.get("/")
async def root():
    """Redirect root to dashboard."""
    return RedirectResponse(url="/dashboard")


@app.get("/trip/")
async def trip_root_redirect():
    """Gracefully handle /trip/ without an id by returning to the dashboard."""
    return RedirectResponse(url="/dashboard")


@app.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Display rich dashboard with featured trip and journey grid."""
    # Get current user from request (don't redirect if not authenticated)
    current_user = get_current_user_from_request(request, db)

    return templates.TemplateResponse(
        "dashboard_refactored.html",
        {
            "request": request,
            "current_user": current_user,
            "is_authenticated": current_user is not None,
            "active_page": "dashboard"
        }
    )


@app.get("/login")
async def login_page(request: Request):
    """Render login page."""
    return templates.TemplateResponse(
        "auth_login.html",
        {
            "request": request,
            "active_page": None,
            "current_user": None,
        },
    )


@app.get("/signup")
async def signup_page(request: Request):
    """Render signup page."""
    return templates.TemplateResponse(
        "signup.html",
        {
            "request": request,
            "active_page": None,
            "current_user": None,
        },
    )


@app.get("/logout")
async def logout(request: Request, response_class=None):
    """Logout the current user by clearing tokens and redirecting to login."""
    # Create a redirect response
    response = RedirectResponse(url="/login", status_code=302)
    
    # Clear authentication tokens from cookies if they exist
    response.delete_cookie("timetide_token", path="/")
    response.delete_cookie("access_token", path="/")
    
    return response


@app.get("/trip/new")
async def create_trip_page(request: Request, db: Session = Depends(get_db)):
    """Render the enhanced create trip page."""
    # Get current user from request
    current_user = get_current_user_from_request(request, db)
    
    # Redirect to login if not authenticated
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "create_trip.html",
        {
            "request": request,
            "active_page": "dashboard",
            "current_user": current_user
        }
    )


@app.get("/trip/{trip_id}")
async def trip_view(trip_id: int, request: Request, db: Session = Depends(get_db)):
    """Display single trip with calendar strip."""
    # Get current user from request
    current_user = get_current_user_from_request(request, db)
    
    # Redirect to login if not authenticated
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Just pass the trip_id to the template, let JavaScript fetch the full data
    return templates.TemplateResponse(
        "trip_detail.html",
        {
            "request": request,
            "trip_id": trip_id,
            "active_page": "dashboard",
            "current_user": current_user
        }
    )


@app.get("/trip/{trip_id}/edit")
async def edit_trip_redirect(trip_id: int):
    """Temporary edit route that forwards to trip view until edit UI exists."""
    return RedirectResponse(url=f"/trip/{trip_id}")


@app.get("/trip/{trip_id}/entry/new")
async def create_entry_page(trip_id: int, request: Request, db: Session = Depends(get_db)):
    """Render the create entry page."""
    # Get current user from request
    current_user = get_current_user_from_request(request, db)
    
    # Redirect to login if not authenticated
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Verify trip exists and user has access
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    # Only owner can add entries (for now)
    if trip.owner_id != current_user.id:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=403)
    
    return templates.TemplateResponse(
        "create_entry.html",
        {
            "request": request,
            "trip_id": trip_id,
            "active_page": "dashboard",
            "current_user": current_user
        }
    )


@app.get("/trip/{trip_id}/day/{date}")
async def day_view(trip_id: int, date: str, request: Request, db: Session = Depends(get_db)):
    """Display timeline for a specific day."""
    from datetime import datetime
    
    # Get current user from request
    current_user = get_current_user_from_request(request, db)
    
    # Redirect to login if not authenticated
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    # Verify user owns this trip
    if trip.owner_id != current_user.id:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=403)
    
    # Parse date
    day_date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Get entries for this specific day
    entries_list = db.query(Entry).filter(
        Entry.trip_id == trip_id,
        Entry.entry_date == day_date
    ).order_by(Entry.entry_time).all()
    
    return templates.TemplateResponse(
        "day.html",
        {
            "request": request,
            "trip": trip,
            "day_date": day_date,
            "entries": entries_list,
            "active_page": "dashboard",
            "current_user": current_user
        }
    )


@app.get("/explore")
async def explore_page(request: Request, db: Session = Depends(get_db)):
    """Display explore page with interactive map of all trips."""
    current_user = get_current_user_from_request(request, db)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "explore.html",
        {
            "request": request,
            "active_page": "explore",
            "current_user": current_user
        }
    )


@app.get("/calendar")
async def calendar_view(request: Request, month: str = None, db: Session = Depends(get_db)):
    """Display calendar view with all activity."""
    from datetime import datetime
    from collections import defaultdict
    
    # Get current user from request
    current_user = get_current_user_from_request(request, db)
    
    # Redirect to login if not authenticated
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get current month/year from query params or default to now
    if month:
        try:
            current_date = datetime.strptime(month + "-01", "%Y-%m-%d")
        except ValueError:
            current_date = datetime.now()
    else:
        current_date = datetime.now()
    
    # Get all entries for the current user
    entries_list = db.query(Entry).filter(Entry.author_id == current_user.id).all()
    
    # Create a set of dates with activity
    active_dates = set(entry.entry_date for entry in entries_list)

    # Build day previews: photo thumbnail + excerpt per date
    day_previews = defaultdict(list)
    for entry in entries_list:
        date_key = entry.entry_date.strftime('%Y-%m-%d') if entry.entry_date else None
        if not date_key:
            continue

        thumb_url = None
        try:
            photos = getattr(entry, "photos", None) or []
            if photos:
                first_photo = photos[0]
                thumb_url = getattr(first_photo, "url", None) or getattr(first_photo, "path", None)
        except Exception:
            thumb_url = None

        excerpt = (entry.content or "").strip()
        if len(excerpt) > 220:
            excerpt = excerpt[:220].rstrip() + "…"

        day_previews[date_key].append(
            {
                "entry_id": getattr(entry, "id", None),
                "trip_id": getattr(entry, "trip_id", None),
                "trip_title": getattr(getattr(entry, "trip", None), "title", None),
                "photo": thumb_url,
                "excerpt": excerpt,
            }
        )
    
    return templates.TemplateResponse(
        "calendar.html",
        {
            "request": request,
            "current_date": current_date,
            "active_dates": active_dates,
            "day_previews": day_previews,
            "active_page": "calendar",
            "current_user": current_user
        }
    )


@app.get("/families")
async def families_view(request: Request, db: Session = Depends(get_db)):
    """Display user's family groups."""
    # Get current user from request
    current_user = get_current_user_from_request(request, db)
    
    # Redirect to login if not authenticated
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "families.html",
        {
            "request": request,
            "families": [],
            "active_page": "families",
            "current_user": current_user
        }
    )


@app.get("/profile")
async def profile_view(request: Request, db: Session = Depends(get_db)):
    """Display user profile."""
    # Get current user from request
    current_user = get_current_user_from_request(request, db)
    
    # Redirect to login if not authenticated
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "active_page": "profile",
            "current_user": current_user
        }
    )


@app.get("/settings")
async def settings_view(request: Request, db: Session = Depends(get_db)):
    """Display user settings."""
    # Get current user from request
    current_user = get_current_user_from_request(request, db)
    
    # Redirect to login if not authenticated
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "active_page": "settings",
            "current_user": current_user
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
