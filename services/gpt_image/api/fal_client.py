"""
GPT-Image 1.5 — FAL.ai API Client
"""
import os
import asyncio
from typing import Optional, Dict, Any
from loguru import logger

import fal_client

from ..config import FAL_ENDPOINT, FAL_EDIT_ENDPOINT, PRICES


class FalClient:
    """Клиент для работы с fal.ai GPT-Image 1.5 API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        os.environ["FAL_KEY"] = api_key
    
    async def generate_image(
        self,
        prompt: str,
        quality: str = "high",
        image_size: str = "1024x1024",
        background: str = "auto",
        output_format: str = "png",
        num_images: int = 1,
    ) -> Dict[str, Any]:
        """
        Генерация изображения по текстовому промпту (Text-to-Image)
        
        Args:
            prompt: Текстовое описание
            quality: Качество (low, medium, high)
            image_size: Размер (1024x1024, 1536x1024, 1024x1536)
            background: Фон (auto, transparent, opaque)
            output_format: Формат (png, jpeg, webp)
            num_images: Количество изображений (1-4)
        
        Returns:
            Dict с результатом генерации
        """
        try:
            arguments = {
                "prompt": prompt,
                "quality": quality,
                "image_size": image_size,
                "background": background,
                "output_format": output_format,
                "num_images": num_images,
            }
            
            logger.info(f"GPT-Image: Запуск генерации, prompt={prompt[:50]}...")
            
            result = await asyncio.to_thread(
                fal_client.run,
                FAL_ENDPOINT,
                arguments=arguments
            )
            
            logger.info(f"GPT-Image: Генерация завершена успешно")
            
            return {
                "success": True,
                "images": result.get("images", []),
                "usage": result.get("usage", {}),
            }
            
        except Exception as e:
            logger.error(f"GPT-Image: Ошибка генерации: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    async def edit_image(
        self,
        prompt: str,
        image_url: str,
        quality: str = "high",
        image_size: str = "auto",
        background: str = "auto",
        output_format: str = "png",
        num_images: int = 1,
        mask_image_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Редактирование изображения (Image-to-Image)
        
        Args:
            prompt: Текстовое описание изменений
            image_url: URL исходного изображения
            quality: Качество (low, medium, high)
            image_size: Размер (auto, 1024x1024, 1536x1024, 1024x1536)
            background: Фон (auto, transparent, opaque)
            output_format: Формат (png, jpeg, webp)
            num_images: Количество изображений
            mask_image_url: URL маски для inpainting (опционально)
        
        Returns:
            Dict с результатом генерации
        """
        try:
            arguments = {
                "prompt": prompt,
                "image_urls": [image_url],
                "quality": quality,
                "image_size": image_size,
                "background": background,
                "output_format": output_format,
                "num_images": num_images,
            }
            
            if mask_image_url:
                arguments["mask_image_url"] = mask_image_url
            
            logger.info(f"GPT-Image: Запуск редактирования, prompt={prompt[:50]}...")
            
            result = await asyncio.to_thread(
                fal_client.run,
                FAL_ENDPOINT,
                arguments=arguments
            )
            
            logger.info(f"GPT-Image: Редактирование завершено успешно")
            
            return {
                "success": True,
                "images": result.get("images", []),
                "usage": result.get("usage", {}),
            }
            
        except Exception as e:
            logger.error(f"GPT-Image: Ошибка редактирования: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    @staticmethod
    def calculate_cost(quality: str, image_size: str, num_images: int = 1) -> float:
        """
        Рассчитать стоимость генерации в USD
        
        Args:
            quality: Качество (low, medium, high)
            image_size: Размер изображения
            num_images: Количество изображений
        
        Returns:
            Стоимость в USD
        """
        quality_prices = PRICES.get(quality, PRICES["high"])
        price_per_image = quality_prices.get(image_size, quality_prices["1024x1024"])
        return price_per_image * num_images
