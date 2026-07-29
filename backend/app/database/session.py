import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Determine database URL from settings or environment
DATABASE_URL = settings.DATABASE_URL or os.getenv("DATABASE_URL", "")

# Normalize bare postgresql:// to postgresql+psycopg:// for explicit DBAPI driver compatibility
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Fallback to sqlite in-memory for testing environment if DATABASE_URL is not set
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///:memory:"

# Create engine with connection pooling and pre-ping check
engine_kwargs = {}
if DATABASE_URL.startswith("postgresql"):
    engine_kwargs = {
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy database session
    and ensures proper closing after request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
