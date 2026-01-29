from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib

from jose import jwt
from jose import exceptions as jose_exceptions
from passlib.context import CryptContext

from .config import SECRET_KEY, ALGORITHM


# Use argon2 which doesn't have the 72-byte limitation
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def _preprocess_password(password: str) -> str:
    """Pre-hash very long passwords with SHA256 for consistency."""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 512:  # Pre-hash only if extremely long
        return hashlib.sha256(password_bytes).hexdigest()
    return password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    preprocessed = _preprocess_password(plain_password)
    return pwd_context.verify(preprocessed, hashed_password)


def get_password_hash(password: str) -> str:
    preprocessed = _preprocess_password(password)
    return pwd_context.hash(preprocessed)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"sub": subject}
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=60))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token. Returns None if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except (jose_exceptions.JWTError, jose_exceptions.ExpiredSignatureError):
        return None
    except Exception:
        return None
