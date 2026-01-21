"""JWT authentication utilities for Timetide."""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import hashlib

from app.models import get_db
from app.models.database import User

# Load environment variables
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# Use argon2 which doesn't have the 72-byte limitation
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def _preprocess_password(password: str) -> str:
    """Pre-hash very long passwords with SHA256 for consistency."""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 512:  # Pre-hash only if extremely long
        return hashlib.sha256(password_bytes).hexdigest()
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    preprocessed = _preprocess_password(plain_password)
    return pwd_context.verify(preprocessed, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password with support for any length."""
    preprocessed = _preprocess_password(password)
    return pwd_context.hash(preprocessed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.InvalidTokenError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


def authenticate_user(db: Session, username_or_email: str, password: str) -> Optional[User]:
    """Authenticate a user by username or email and password."""
    # Try to find user by email first, then by username
    user = db.query(User).filter(User.email == username_or_email).first()
    if not user:
        user = db.query(User).filter(User.username == username_or_email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
