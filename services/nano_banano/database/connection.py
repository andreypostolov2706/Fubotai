"""
Nano Banano — Database Connection
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Путь к БД сервиса
SERVICE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(SERVICE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "nano_banano.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

_db_initialized = False


def init_db():
    """Initialize database and create tables"""
    from .models import Base
    Base.metadata.create_all(engine)
    return SessionLocal


def get_session():
    """Get database session"""
    global _db_initialized
    if not _db_initialized:
        init_db()
        _db_initialized = True
    return SessionLocal()
