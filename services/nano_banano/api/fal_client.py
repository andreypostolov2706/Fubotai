"""
Nano Banano — fal.ai API Client
"""
import asyncio
import os
import time
from typing import Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class GenerationResult:
    """Результат генерации"""
    success: bool
    image_url: Optional[str] = None
    request_id: Optional[str] = None
    generation_time: Optional[float] = None
    error: Optional[str] = None


class FalClient:
    """Клиент для работы с fal.ai API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Устанавливаем API ключ через переменную окружения
        if api_key:
            os.environ['FAL_KEY'] = api_key
    
    async def generate_image(
        self,
        endpoint: str,
        prompt: str,
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "1:1",
        output_format: str = "png",
        resolution: Optional[str] = None,
        num_images: int = 1,
    ) -> GenerationResult:
        """
        Генерация изображения (Text-to-Image).
        
        Args:
            endpoint: fal.ai endpoint (например, "fal-ai/nano-banana-pro")
            prompt: Текстовый промпт
            negative_prompt: Негативный промпт (опционально)
            aspect_ratio: Соотношение сторон (1:1, 16:9, etc.)
            output_format: Формат вывода (png, jpeg, webp)
            resolution: Разрешение для Pro версии (1K, 2K, 4K)
            num_images: Количество изображений
            
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
                "num_images": num_images,
                "aspect_ratio": aspect_ratio,
                "output_format": output_format,
            }
            
            # Добавляем негативный промпт если есть
            if negative_prompt:
                input_params["negative_prompt"] = negative_prompt
            
            # Добавляем разрешение для Pro версии
            if resolution and "pro" in endpoint:
                input_params["resolution"] = resolution
            
            logger.info(f"Nano Banano: Запуск генерации, endpoint={endpoint}")
            logger.debug(f"Nano Banano: Параметры: {input_params}")
            
            # Выполняем запрос в отдельном потоке (fal_client синхронный)
            def run_generation():
                return fal_client.run(
                    endpoint,
                    arguments=input_params,
                )
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_generation)
            
            generation_time = time.time() - start_time
            
            # Извлекаем URL изображения
            images = result.get("images", [])
            if not images:
                return GenerationResult(
                    success=False,
                    error="fal.ai не вернул изображения"
                )
            
            image_url = images[0].get("url")
            request_id = result.get("request_id", "")
            
            logger.info(f"Nano Banano: Генерация завершена за {generation_time:.2f}с")
            
            return GenerationResult(
                success=True,
                image_url=image_url,
                request_id=request_id,
                generation_time=generation_time,
            )
            
        except Exception as e:
            logger.error(f"Nano Banano: Ошибка генерации: {e}")
            return GenerationResult(
                success=False,
                error=str(e)
            )
    
    async def edit_image(
        self,
        endpoint: str,
        prompt: str,
        image_urls: list[str],
        negative_prompt: Optional[str] = None,
        aspect_ratio: str = "auto",
        output_format: str = "png",
        resolution: Optional[str] = None,
        num_images: int = 1,
    ) -> GenerationResult:
        """
        Редактирование изображений (Image-to-Image).
        
        Args:
            endpoint: fal.ai endpoint (например, "fal-ai/nano-banana-pro/edit")
            prompt: Текстовый промпт для редактирования
            image_urls: Список URL входных изображений (1-4)
            negative_prompt: Негативный промпт (опционально)
            aspect_ratio: Соотношение сторон (auto, 1:1, 16:9, etc.)
            output_format: Формат вывода (png, jpeg, webp)
            resolution: Разрешение для Pro версии (1K, 2K, 4K)
            num_images: Количество изображений
            
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
        
        if not image_urls:
            return GenerationResult(
                success=False,
                error="Не указаны изображения для редактирования"
            )
        
        try:
            start_time = time.time()
            
            # Формируем параметры запроса
            input_params = {
                "prompt": prompt,
                "image_urls": image_urls,
                "num_images": num_images,
                "aspect_ratio": aspect_ratio,
                "output_format": output_format,
            }
            
            # Добавляем негативный промпт если есть
            if negative_prompt:
                input_params["negative_prompt"] = negative_prompt
            
            # Добавляем разрешение для Pro версии
            if resolution and "pro" in endpoint:
                input_params["resolution"] = resolution
            
            logger.info(f"Nano Banano: Запуск редактирования, endpoint={endpoint}")
            logger.debug(f"Nano Banano: Параметры: {input_params}")
            
            # Выполняем запрос в отдельном потоке
            def run_edit():
                return fal_client.run(
                    endpoint,
                    arguments=input_params,
                )
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_edit)
            
            generation_time = time.time() - start_time
            
            # Извлекаем URL изображения
            images = result.get("images", [])
            if not images:
                return GenerationResult(
                    success=False,
                    error="fal.ai не вернул изображения"
                )
            
            image_url = images[0].get("url")
            request_id = result.get("request_id", "")
            
            logger.info(f"Nano Banano: Редактирование завершено за {generation_time:.2f}с")
            
            return GenerationResult(
                success=True,
                image_url=image_url,
                request_id=request_id,
                generation_time=generation_time,
            )
            
        except Exception as e:
            logger.error(f"Nano Banano: Ошибка редактирования: {e}")
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
            
            url = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: fal_client.upload(image_data, "image/jpeg")
            )
            logger.info(f"Nano Banano: Изображение загружено: {url[:50]}...")
            return url
        except Exception as e:
            logger.error(f"Nano Banano: Ошибка загрузки изображения: {e}")
            return None


# Backward-compatible alias used by handlers
NanoBananoClient = FalClient
