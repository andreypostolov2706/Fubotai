"""
AI Avatar — fal.ai API Client
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
    video_duration: Optional[float] = None
    request_id: Optional[str] = None
    generation_time: Optional[float] = None
    error: Optional[str] = None


class FalClient:
    """Клиент для работы с fal.ai Creatify Aurora API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        if api_key:
            os.environ['FAL_KEY'] = api_key
    
    async def generate_avatar_video(
        self,
        image_url: str,
        audio_url: str,
        prompt: Optional[str] = None,
        quality: str = "480p",
    ) -> GenerationResult:
        """
        Генерация говорящего аватара (Image + Audio to Video).
        
        Args:
            image_url: URL изображения персонажа
            audio_url: URL аудиофайла
            prompt: Промпт визуального стиля (опционально)
            quality: Качество видео (480p или 720p)
            
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
                "image_url": image_url,
                "audio_url": audio_url,
            }
            
            # Добавляем промпт если указан
            if prompt:
                input_params["prompt"] = prompt
            
            logger.info(f"AI Avatar: Запуск генерации видео (quality={quality})")
            logger.debug(f"AI Avatar: Параметры: {input_params}")
            
            # Запускаем генерацию через fal.ai
            def run_generation():
                return fal_client.subscribe(
                    "fal-ai/creatify/aurora",
                    arguments=input_params,
                    with_logs=True,
                )
            
            # Выполняем в отдельном потоке
            result = await asyncio.get_event_loop().run_in_executor(
                None, run_generation
            )
            
            generation_time = time.time() - start_time
            
            # Извлекаем URL видео из результата
            video_url = result.get("video", {}).get("url")
            
            if not video_url:
                logger.error(f"AI Avatar: Видео URL не найден в ответе: {result}")
                return GenerationResult(
                    success=False,
                    error="Не удалось получить URL видео из ответа API"
                )
            
            logger.info(f"AI Avatar: Видео успешно сгенерировано за {generation_time:.1f}с")
            
            return GenerationResult(
                success=True,
                video_url=video_url,
                request_id=result.get("request_id"),
                generation_time=generation_time,
            )
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"AI Avatar: Ошибка генерации: {error_msg}")
            
            # Обработка специфичных ошибок
            if "401" in error_msg or "authentication" in error_msg.lower():
                return GenerationResult(
                    success=False,
                    error="Ошибка аутентификации API. Проверьте API ключ."
                )
            elif "422" in error_msg:
                return GenerationResult(
                    success=False,
                    error="Неверные параметры запроса. Проверьте формат файлов."
                )
            elif "content_policy" in error_msg.lower():
                return GenerationResult(
                    success=False,
                    error="Контент не прошёл проверку модерации"
                )
            else:
                return GenerationResult(
                    success=False,
                    error=f"Ошибка API: {error_msg}"
                )
    
    async def estimate_video_duration(self, audio_url: str) -> Optional[float]:
        """
        Оценка длительности видео на основе аудио.
        
        Args:
            audio_url: URL аудиофайла
            
        Returns:
            Длительность в секундах или None при ошибке
        """
        try:
            import requests
            from io import BytesIO
            
            # Скачиваем аудио
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: requests.get(audio_url, timeout=10)
            )
            
            if response.status_code != 200:
                logger.error(f"AI Avatar: Не удалось скачать аудио: {response.status_code}")
                return None
            
            # Пытаемся определить длительность через mutagen
            try:
                from mutagen import File
                audio_file = File(BytesIO(response.content))
                if audio_file and hasattr(audio_file.info, 'length'):
                    duration = audio_file.info.length
                    logger.info(f"AI Avatar: Длительность аудио: {duration:.1f}с")
                    return duration
            except Exception as e:
                logger.warning(f"AI Avatar: Не удалось определить длительность аудио: {e}")
                return None
                
        except Exception as e:
            logger.error(f"AI Avatar: Ошибка при оценке длительности: {e}")
            return None
