"""
Kling Video v2.6 — FAL.ai API Client
"""
import os
import asyncio
from typing import Optional, Dict, Any
from loguru import logger

import fal_client

from ..config import (
    FAL_TEXT_TO_VIDEO,
    FAL_IMAGE_TO_VIDEO,
    PRICE_PER_SECOND_NO_AUDIO,
    PRICE_PER_SECOND_WITH_AUDIO,
)


class FalClient:
    """Клиент для работы с fal.ai Kling Video API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        os.environ["FAL_KEY"] = api_key
    
    async def text_to_video(
        self,
        prompt: str,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        audio_enabled: bool = False,
    ) -> Dict[str, Any]:
        """
        Генерация видео по текстовому промпту (Text-to-Video)
        
        Args:
            prompt: Текстовое описание
            duration: Длительность (5 или 10 секунд)
            aspect_ratio: Соотношение сторон (16:9, 9:16, 1:1)
            audio_enabled: Включить генерацию аудио
        
        Returns:
            Dict с результатом генерации
        """
        try:
            arguments = {
                "prompt": prompt,
                "duration": str(duration),
                "aspect_ratio": aspect_ratio,
            }
            
            if audio_enabled:
                arguments["with_audio"] = True
            
            logger.info(f"Kling: Запуск Text-to-Video, prompt={prompt[:50]}...")
            
            result = await asyncio.to_thread(
                fal_client.run,
                FAL_TEXT_TO_VIDEO,
                arguments=arguments
            )
            
            logger.info(f"Kling: Text-to-Video завершено успешно")
            
            return {
                "success": True,
                "video": result.get("video", {}),
                "request_id": result.get("request_id"),
            }
            
        except Exception as e:
            logger.error(f"Kling: Ошибка Text-to-Video: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def image_to_video(
        self,
        prompt: str,
        image_url: str,
        duration: int = 5,
        aspect_ratio: str = "16:9",
        audio_enabled: bool = False,
    ) -> Dict[str, Any]:
        """
        Генерация видео из изображения (Image-to-Video)
        
        Args:
            prompt: Текстовое описание движения
            image_url: URL исходного изображения
            duration: Длительность (5 или 10 секунд)
            aspect_ratio: Соотношение сторон
            audio_enabled: Включить генерацию аудио
        
        Returns:
            Dict с результатом генерации
        """
        try:
            arguments = {
                "prompt": prompt,
                "image_url": image_url,
                "duration": str(duration),
                "aspect_ratio": aspect_ratio,
            }
            
            if audio_enabled:
                arguments["with_audio"] = True
            
            logger.info(f"Kling: Запуск Image-to-Video, prompt={prompt[:50]}...")
            
            result = await asyncio.to_thread(
                fal_client.run,
                FAL_IMAGE_TO_VIDEO,
                arguments=arguments
            )
            
            logger.info(f"Kling: Image-to-Video завершено успешно")
            
            return {
                "success": True,
                "video": result.get("video", {}),
                "request_id": result.get("request_id"),
            }
            
        except Exception as e:
            logger.error(f"Kling: Ошибка Image-to-Video: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def upload_image(self, image_data: bytes) -> Optional[str]:
        """
        Загрузить изображение на fal.ai storage.
        
        Args:
            image_data: Байты изображения
            
        Returns:
            URL загруженного изображения или None
        """
        try:
            url = await asyncio.to_thread(
                fal_client.upload,
                image_data,
                "image/jpeg"
            )
            logger.info(f"Kling: Изображение загружено: {url[:50]}...")
            return url
        except Exception as e:
            logger.error(f"Kling: Ошибка загрузки изображения: {e}")
            return None
    
    @staticmethod
    def calculate_cost(duration: int, audio_enabled: bool = False) -> float:
        """
        Рассчитать стоимость генерации в USD
        
        Args:
            duration: Длительность в секундах
            audio_enabled: Включено ли аудио
        
        Returns:
            Стоимость в USD
        """
        price_per_second = PRICE_PER_SECOND_WITH_AUDIO if audio_enabled else PRICE_PER_SECOND_NO_AUDIO
        return price_per_second * duration
