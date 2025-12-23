"""
Sora 2 fal.ai API Client
"""
import os
import fal_client
from loguru import logger
from typing import Optional
import asyncio

from .config import FAL_TEXT_TO_VIDEO, FAL_IMAGE_TO_VIDEO


class SoraAPI:
    """Клиент для работы с Sora 2 через fal.ai"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        fal_client.api_key = api_key
        os.environ["FAL_KEY"] = api_key
    
    async def text_to_video(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        duration: int = 4,
    ) -> dict:
        """
        Генерация видео из текста
        
        Args:
            prompt: Описание видео
            aspect_ratio: Соотношение сторон (16:9, 9:16)
            duration: Длительность в секундах (4, 8, 12)
            
        Returns:
            dict с video_url, video_id, thumbnail_url
        """
        try:
            logger.info(f"Sora T2V: Starting generation, prompt={prompt[:50]}...")
            
            # Запускаем в отдельном потоке, т.к. fal_client синхронный
            result = await asyncio.to_thread(
                fal_client.run,
                FAL_TEXT_TO_VIDEO,
                arguments={
                    "prompt": prompt,
                    "resolution": "720p",
                    "aspect_ratio": aspect_ratio,
                    "duration": duration,
                }
            )
            
            logger.info(f"Sora T2V: Generation completed")
            
            return {
                "success": True,
                "video_url": result.get("video", {}).get("url"),
                "video_id": result.get("video_id"),
                "thumbnail_url": result.get("thumbnail", {}).get("url"),
            }
            
        except Exception as e:
            logger.error(f"Sora T2V error: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def image_to_video(
        self,
        image_url: str,
        prompt: str,
        aspect_ratio: str = "16:9",
        duration: int = 4,
    ) -> dict:
        """
        Анимация изображения
        
        Args:
            image_url: URL изображения
            prompt: Описание анимации
            aspect_ratio: Соотношение сторон
            duration: Длительность в секундах
            
        Returns:
            dict с video_url, video_id, thumbnail_url
        """
        try:
            logger.info(f"Sora I2V: Starting generation, prompt={prompt[:50]}...")
            
            result = await asyncio.to_thread(
                fal_client.run,
                FAL_IMAGE_TO_VIDEO,
                arguments={
                    "image_url": image_url,
                    "prompt": prompt,
                }
            )
            
            logger.info(f"Sora I2V: Generation completed")
            
            return {
                "success": True,
                "video_url": result.get("video", {}).get("url"),
                "video_id": result.get("video_id"),
                "thumbnail_url": result.get("thumbnail", {}).get("url"),
            }
            
        except Exception as e:
            logger.error(f"Sora I2V error: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def upload_image(self, image_data: bytes) -> Optional[str]:
        """Загрузить изображение на fal.ai storage"""
        try:
            url = await asyncio.to_thread(
                fal_client.upload,
                image_data,
                "image/jpeg"
            )
            return url
        except Exception as e:
            logger.error(f"Sora upload error: {e}")
            return None
