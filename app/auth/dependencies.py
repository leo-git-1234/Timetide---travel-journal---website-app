from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.models import get_db
from app.models.database import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception

    # We store user id as subject
    try:
        user = db.query(User).filter(User.id == int(sub)).first()
        if user is None:
            raise credentials_exception
        return user
    except (ValueError, TypeError):
        raise credentials_exception
