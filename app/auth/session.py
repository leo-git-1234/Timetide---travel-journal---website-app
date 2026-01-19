"""Session and authentication utilities for page routes."""

from fastapi import Request
from sqlalchemy.orm import Session
from app.models.database import User
from app.core.security import decode_token


def get_current_user_from_request(request: Request, db: Session) -> User | None:
    """
    Extract and verify current user from request token.
    
    Checks Authorization header and timetide_token cookie.
    Returns None if token is invalid, expired, or not found.
    """
    token = None
    
    try:
        # Try to get token from Authorization header
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        # Try to get token from cookies
        elif "timetide_token" in request.cookies:
            token = request.cookies["timetide_token"]
        
        if token:
            # Verify and decode token
            payload = decode_token(token)
            if payload:
                user_id = payload.get("sub")
                if user_id:
                    current_user = db.query(User).filter(User.id == user_id).first()
                    if current_user:
                        return current_user
    except Exception as e:
        print(f"Auth error: {str(e)}")
