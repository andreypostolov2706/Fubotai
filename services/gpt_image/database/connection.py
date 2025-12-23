"""
GPT-Image Database Connection
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base

SERVICE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(SERVICE_DIR, "data", "gpt_image.db")

engine = None
SessionLocal = None


def init_db():
    """Инициализация базы данных"""
    global engine, SessionLocal
    
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    SessionLocal = sessionmaker(bind=engine)
    
    Base.metadata.create_all(engine)


def get_session() -> Session:
    """Получить сессию БД"""
    if SessionLocal is None:
        init_db()
    return SessionLocal()
