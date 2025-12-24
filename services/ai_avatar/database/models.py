"""
AI Avatar — Database Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class AvatarGeneration(Base):
    """История генераций AI Avatar"""
    __tablename__ = "ai_avatar_generations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Входные данные
    image_url = Column(String(500), nullable=False)
    audio_url = Column(String(500), nullable=False)
    prompt = Column(Text, nullable=True)
    quality = Column(String(10), default="480p")
    
    # Результат
    video_url = Column(String(500), nullable=True)
    video_duration = Column(Float, nullable=True)
    
    # Стоимость
    cost_usd = Column(Float, nullable=False)
    cost_gton = Column(Float, nullable=False)
    
    # Статус
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Метаданные
    request_id = Column(String(100), nullable=True)
    generation_time = Column(Float, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<AvatarGeneration(id={self.id}, user_id={self.user_id}, status={self.status})>"


def init_db():
    """Инициализация базы данных"""
    from core.database.connection import engine
    Base.metadata.create_all(bind=engine)
