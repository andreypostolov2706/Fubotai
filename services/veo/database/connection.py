"""
Veo Service — Database Connection
"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

# Путь к БД сервиса
SERVICE_DIR = Path(__file__).parent.parent
DB_PATH = SERVICE_DIR / "data" / "veo.db"

# Создаём директорию если не существует
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Engine и Session
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)


def get_session():
    """Получить сессию БД"""
    return SessionLocal()


def init_db():
    """Инициализировать БД (создать таблицы)"""
    Base.metadata.create_all(engine)
