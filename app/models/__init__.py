"""Database connection and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .database import Base
import os

# Get database URL from environment or use SQLite for local dev
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./timetide.db"
)

# Create engine
# For PostgreSQL in production, use: postgresql://user:password@localhost/timetide
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
