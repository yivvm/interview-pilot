"""Database setup: SQLAlchemy engine, session factory, and helpers."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# check_same_thread=False is required for SQLite under FastAPI,
# which may touch the connection from different threads.
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

# Factory that produces individual DB sessions (one per request).
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class all ORM models inherit from.
Base = declarative_base()

def init_db() -> None:
    """Create any tables that don't exist yet (no migrations for MVP)."""
    from app import models  # noqa: F401 (import so models register on Base)
    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI dependency: hand out a DB session, always close it."""
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
