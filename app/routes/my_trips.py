from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth.session import get_current_user_from_request
from app.models import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/my-trips", response_class=HTMLResponse)
async def my_trips_page(request: Request, db: Session = Depends(get_db)):
    """Render the My Trips page template"""
    current_user = get_current_user_from_request(request, db)
    if not current_user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("my_trips.html", {
        "request": request,
        "current_user": current_user,
        "active_page": "my-trips"
    })
