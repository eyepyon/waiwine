"""
Database configuration and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from backend.config.settings import get_config

config = get_config()

# Database engine configuration
if config.DATABASE_URL.startswith('sqlite'):
    # SQLite configuration with connection pooling
    engine = create_engine(
        config.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=config.DEBUG
    )
else:
    # PostgreSQL or other database configuration
    engine = create_engine(
        config.DATABASE_URL,
        echo=config.DEBUG
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)

def drop_database():
    """Drop all database tables (for testing)."""
    Base.metadata.drop_all(bind=engine)