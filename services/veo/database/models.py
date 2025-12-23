"""
Veo Service — Database Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class VideoGeneration(Base):
    """Модель генерации видео"""
    __tablename__ = "video_generations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Режим генерации
    mode = Column(String(20), nullable=False)  # "text_to_video" или "image_to_video"
    
    # Параметры генерации
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    duration = Column(String(10), nullable=False)  # "5s", "6s", "7s", "8s"
    aspect_ratio = Column(String(30), nullable=False)
    enhance_prompt = Column(Boolean, default=True)
    seed = Column(Integer, nullable=True)
    
    # Входное изображение (для image_to_video)
    input_image_url = Column(Text, nullable=True)
    
    # Результат
    video_url = Column(Text, nullable=True)
    file_id = Column(String(200), nullable=True)  # Telegram file_id
    
    # Стоимость
    cost_usd = Column(Float, nullable=True)
    cost_gton = Column(Float, nullable=True)
    
    # Метаданные
    generation_time = Column(Float, nullable=True)  # Время генерации в секундах
    fal_request_id = Column(String(100), nullable=True)
    
    # Статус
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Публикация в галерею
    published_to_gallery = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)
    gallery_message_id = Column(Integer, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<VideoGeneration(id={self.id}, user_id={self.user_id}, mode={self.mode}, status={self.status})>"
