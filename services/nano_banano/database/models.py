"""
Nano Banano — Database Models
"""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, String, DateTime, 
    Boolean, Text, Float, Numeric, JSON
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Generation(Base):
    """История генераций изображений"""
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    
    # Тип генерации
    mode = Column(String(20))  # "generate" | "edit"
    
    # Параметры генерации
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text)
    model = Column(String(50))  # nano_banana | nano_banana_pro
    aspect_ratio = Column(String(10))  # 1:1, 16:9, etc.
    resolution = Column(String(5))  # 1K, 2K, 4K
    output_format = Column(String(10))  # png, jpeg, webp
    
    # Входные изображения (для edit режима)
    input_images = Column(JSON)  # ["url1", "url2", ...]
    
    # Результат
    image_url = Column(String(500))
    file_id = Column(String(100))  # Telegram file_id для повторной отправки
    
    # Стоимость
    cost_usd = Column(Numeric(10, 4))  # Себестоимость fal.ai
    cost_gton = Column(Numeric(18, 6))  # Списано с пользователя
    
    # Метаданные генерации
    generation_time = Column(Float)  # Время генерации в секундах
    fal_request_id = Column(String(100))
    
    # Статус
    status = Column(String(20), default="pending")  # pending, completed, failed, refunded
    error_message = Column(Text)
    
    # Публикация в галерею
    published_to_gallery = Column(Boolean, default=False)
    published_at = Column(DateTime)
    gallery_message_id = Column(BigInteger)  # ID сообщения в канале
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Generation(id={self.id}, user_id={self.user_id}, status={self.status})>"
