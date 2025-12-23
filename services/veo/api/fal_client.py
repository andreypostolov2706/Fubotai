"""
Veo Service — fal.ai API Client
"""
import asyncio
import os
import time
from typing import Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class GenerationResult:
    """Результат генерации видео"""
    success: bool
    video_url: Optional[str] = None
    request_id: Optional[str] = None
    generation_time: Optional[float] = None
    error: Optional[str] = None


class FalClient:
    """Клиент для работы с fal.ai API (Veo 2)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        if api_key:
            os.environ['FAL_KEY'] = api_key
    
    async def generate_video(
        self,
        prompt: str,
        duration: str = "5s",
        aspect_ratio: str = "16:9",
        negative_prompt: Optional[str] = None,
        enhance_prompt: bool = True,
        seed: Optional[int] = None,
    ) -> GenerationResult:
        """
        Генерация видео по тексту (Text-to-Video).
        
        Args:
            prompt: Текстовое описание видео
            duration: Длительность (5s, 6s, 7s, 8s)
            aspect_ratio: Соотношение сторон (16:9, 9:16)
            negative_prompt: Негативный промпт
            enhance_prompt: Улучшение промпта
            seed: Сид для воспроизводимости
            
        Returns:
            GenerationResult
        """
        try:
            import fal_client
        except ImportError:
            return GenerationResult(
                success=False,
                error="fal-client не установлен. Выполните: pip install fal-client"
            )
        
        if not self.api_key:
            return GenerationResult(
                success=False,
                error="API ключ fal.ai не настроен"
            )
        
        try:
            start_time = time.time()
            
            # Формируем параметры запроса
            input_params = {
                "prompt": prompt,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "enhance_prompt": enhance_prompt,
            }
            
            if negative_prompt:
                input_params["negative_prompt"] = negative_prompt
            
            if seed is not None:
                input_params["seed"] = seed
            
            logger.info(f"Veo: Запуск генерации видео, duration={duration}")
            logger.debug(f"Veo: Параметры: {input_params}")
            
            # Выполняем запрос в отдельном потоке
            def run_generation():
                return fal_client.run(
                    "fal-ai/veo2",
                    arguments=input_params,
                )
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_generation)
            
            generation_time = time.time() - start_time
            
            # Извлекаем URL видео
            video = result.get("video", {})
            video_url = video.get("url")
            
            if not video_url:
                return GenerationResult(
                    success=False,
                    error="fal.ai не вернул видео"
                )
            
            request_id = result.get("request_id", "")
            
            logger.info(f"Veo: Генерация завершена за {generation_time:.2f}с")
            
            return GenerationResult(
                success=True,
                video_url=video_url,
                request_id=request_id,
                generation_time=generation_time,
            )
            
        except Exception as e:
            logger.error(f"Veo: Ошибка генерации: {e}")
            return GenerationResult(
                success=False,
                error=str(e)
            )
    
    async def image_to_video(
        self,
        prompt: str,
        image_url: str,
        duration: str = "5s",
        aspect_ratio: str = "auto",
    ) -> GenerationResult:
        """
        Генерация видео из изображения (Image-to-Video).
        
        Args:
            prompt: Описание как анимировать изображение
            image_url: URL входного изображения
            duration: Длительность (5s, 6s, 7s, 8s)
            aspect_ratio: Соотношение сторон (auto, auto_prefer_portrait, 16:9, 9:16)
            
        Returns:
            GenerationResult
        """
        try:
            import fal_client
        except ImportError:
            return GenerationResult(
                success=False,
                error="fal-client не установлен. Выполните: pip install fal-client"
            )
        
        if not self.api_key:
            return GenerationResult(
                success=False,
                error="API ключ fal.ai не настроен"
            )
        
        if not image_url:
            return GenerationResult(
                success=False,
                error="Не указано изображение"
            )
        
        try:
            start_time = time.time()
            
            # Формируем параметры запроса
            input_params = {
                "prompt": prompt,
                "image_url": image_url,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
            }
            
            logger.info(f"Veo: Запуск Image-to-Video, duration={duration}")
            logger.debug(f"Veo: Параметры: {input_params}")
            
            # Выполняем запрос в отдельном потоке
            def run_generation():
                return fal_client.run(
                    "fal-ai/veo2/image-to-video",
                    arguments=input_params,
                )
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_generation)
            
            generation_time = time.time() - start_time
            
            # Извлекаем URL видео
            video = result.get("video", {})
            video_url = video.get("url")
            
            if not video_url:
                return GenerationResult(
                    success=False,
                    error="fal.ai не вернул видео"
                )
            
            request_id = result.get("request_id", "")
            
            logger.info(f"Veo: Image-to-Video завершено за {generation_time:.2f}с")
            
            return GenerationResult(
                success=True,
                video_url=video_url,
                request_id=request_id,
                generation_time=generation_time,
            )
            
        except Exception as e:
            logger.error(f"Veo: Ошибка Image-to-Video: {e}")
            return GenerationResult(
                success=False,
                error=str(e)
            )
    
    async def upload_image(self, image_data: bytes) -> Optional[str]:
        """
        Загрузить изображение на fal.ai storage.
        
        Args:
            image_data: Байты изображения
            
        Returns:
            URL загруженного изображения или None
        """
        try:
            import fal_client
            
            loop = asyncio.get_event_loop()
            url = await loop.run_in_executor(
                None,
                lambda: fal_client.upload(image_data, "image/jpeg")
            )
            logger.info(f"Veo: Изображение загружено: {url[:50]}...")
            return url
        except Exception as e:
            logger.error(f"Veo: Ошибка загрузки изображения: {e}")
            return None
