"""
GPT-Image Database Models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ImageGeneration(Base):
    """Модель для хранения истории генераций"""
    __tablename__ = "image_generations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    mode = Column(String(20), nullable=False)  # "text_to_image" или "image_to_image"
    
    prompt = Column(Text, nullable=False)
    
    quality = Column(String(20), nullable=False)  # low, medium, high
    image_size = Column(String(20), nullable=False)  # 1024x1024, 1536x1024, 1024x1536
    background = Column(String(20), nullable=False)  # auto, transparent, opaque
    output_format = Column(String(10), nullable=False)  # png, jpeg, webp
    num_images = Column(Integer, default=1)
    
    input_image_url = Column(Text, nullable=True)
    
    image_url = Column(Text, nullable=True)
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
        return f"<ImageGeneration(id={self.id}, user_id={self.user_id}, mode={self.mode}, status={self.status})>"
