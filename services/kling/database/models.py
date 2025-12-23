"""
Kling Database Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class VideoGeneration(Base):
    """Модель для хранения истории генераций видео"""
    __tablename__ = "video_generations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    mode = Column(String(20), nullable=False)  # "text_to_video" или "image_to_video"
    
    prompt = Column(Text, nullable=False)
    
    duration = Column(Integer, nullable=False)  # 5 или 10 секунд
    aspect_ratio = Column(String(10), nullable=False)  # 16:9, 9:16, 1:1
    audio_enabled = Column(Boolean, default=False)
    
    input_image_url = Column(Text, nullable=True)
    
    video_url = Column(Text, nullable=True)
    file_id = Column(String(200), nullable=True)
    
    cost_usd = Column(Float, nullable=True)
    cost_gton = Column(Float, nullable=True)
    
    generation_time = Column(Float, nullable=True)
    fal_request_id = Column(String(100), nullable=True)
    
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    published_to_gallery = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)
    gallery_message_id = Column(Integer, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<VideoGeneration(id={self.id}, user_id={self.user_id}, mode={self.mode}, status={self.status})>"
