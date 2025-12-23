"""
FLUX 2 Flex — База данных
"""
import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from . import config

Base = declarative_base()

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "flux2_flex.db")


class Generation(Base):
    """Модель генерации изображения"""
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    image_size = Column(String(50), default="square")
    output_format = Column(String(10), default="jpeg")
    num_inference_steps = Column(Integer, default=28)
    guidance_scale = Column(Float, default=3.5)
    
    image_url = Column(Text)
    seed = Column(Integer)
    
    cost_usd = Column(Float, default=0)
    cost_gton = Column(Float, default=0)
    
    status = Column(String(20), default="pending")  # pending, completed, failed
    error_message = Column(Text)
    
    generation_time = Column(Float)  # секунды
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


_engine = None
_SessionLocal = None


def init_db():
    """Инициализация базы данных"""
    global _engine, _SessionLocal
    
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    _engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
    Base.metadata.create_all(_engine)
    _SessionLocal = sessionmaker(bind=_engine)


def get_session():
    """Получить сессию БД"""
    global _SessionLocal
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()
