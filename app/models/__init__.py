"""Database connection and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker
from .database import Base


def _is_production_environment() -> bool:
    """Return True when running in production-like environments."""
    environment = os.getenv("ENVIRONMENT", "").strip().lower()
    app_env = os.getenv("APP_ENV", "").strip().lower()
    python_env = os.getenv("PYTHON_ENV", "").strip().lower()
    render = os.getenv("RENDER", "").strip().lower() == "true"
    return render or environment in {"production", "prod"} or app_env in {"production", "prod"} or python_env in {"production", "prod"}


def _normalize_database_url(raw_url: str) -> str:
    """Normalize database URL schemes for SQLAlchemy compatibility."""
    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw_url


_raw_database_url = os.getenv("DATABASE_URL", "").strip()
if _raw_database_url:
    DATABASE_URL = _normalize_database_url(_raw_database_url)
elif _is_production_environment():
    raise RuntimeError(
        "DATABASE_URL is required in production. Refusing to start with SQLite fallback."
    )
else:
    DATABASE_URL = "sqlite:///./timetide.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_database_diagnostics() -> dict:
    """Return safe, human-readable database diagnostics for startup logs."""
    url = make_url(DATABASE_URL)
    dialect = (url.drivername or "unknown").split("+")[0]

    if dialect == "sqlite":
        return {
            "dialect": "SQLite",
            "host": None,
            "database": url.database,
        }

    return {
        "dialect": "PostgreSQL" if dialect.startswith("postgres") else dialect,
        "host": url.host,
        "database": url.database,
    }

# Dependency to get DB session
def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
