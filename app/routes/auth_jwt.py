from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import access_token_expires_delta
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import get_db
from app.models.database import User
from app.schemas.auth import Token, UserCreate, UserLogin, UserOut
from app.auth.dependencies import get_current_user


router = APIRouter()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


@router.post("/signup", response_model=Token, status_code=201)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.

    Returns:
    - 201: User created successfully with access token
    - 400: Email already registered or validation error
    - 500: Unexpected server error
    """
    # Ensure email uniqueness
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please sign in or use a different email."
        )

    # Validate name is not empty
    if not payload.name or not payload.name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Name is required."
        )

    try:
        user = User(
            email=payload.email.lower(),
            name=payload.name.strip(),
            hashed_password=get_password_hash(payload.password),
            username=payload.email.lower().split("@")[0]
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        print(f"Signup error: {str(e)}")  # Log actual error for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account. Please try again later."
        )

    token = create_access_token(subject=str(user.id), expires_delta=access_token_expires_delta())
    return Token(access_token=token)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user with email and password.

    Returns:
    - 200: Authentication successful with access token
    - 401: Invalid credentials
    - 400: Account configuration error
    """
    # OAuth2PasswordRequestForm uses 'username' field which we treat as email
    user = get_user_by_email(db, form_data.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account not configured. Please contact support."
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=str(user.id), expires_delta=access_token_expires_delta())
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user details."""
    return current_user
