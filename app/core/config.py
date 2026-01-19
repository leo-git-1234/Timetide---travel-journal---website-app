import os
from datetime import timedelta


SECRET_KEY = os.getenv("TIMETIDE_SECRET_KEY", "change-this-in-production")
ALGORITHM = os.getenv("TIMETIDE_JWT_ALGO", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("TIMETIDE_ACCESS_TOKEN_MINUTES", "60"))

def access_token_expires_delta() -> timedelta:
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
