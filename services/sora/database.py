"""
Sora 2 Service Database Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Generation(Base):
    """Модель генерации видео"""
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Тип генерации
    generation_type = Column(String(20), default="text_to_video")  # text_to_video, image_to_video
    
    # Входные данные
    prompt = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)  # для image_to_video
    
    # Параметры
    aspect_ratio = Column(String(10), default="16:9")
    duration = Column(Integer, default=4)
    
    # Результат
    video_url = Column(Text, nullable=True)
    video_id = Column(String(100), nullable=True)
    thumbnail_url = Column(Text, nullable=True)
    
    # Стоимость
    cost_usd = Column(Float, default=0.0)
    cost_gton = Column(Float, default=0.0)
    
    # Статус
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # fal.ai
    fal_request_id = Column(String(100), nullable=True)
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Публикация
    published_to_gallery = Column(Boolean, default=False)
    gallery_message_id = Column(Integer, nullable=True)


# Database setup
SERVICE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SERVICE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(DATA_DIR, 'sora.db')}"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize database"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def get_session() -> AsyncSession:
    """Get database session"""
    return async_session()
