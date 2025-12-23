"""
FLUX 2 Flex — API клиент fal.ai
"""
import os
import time
import asyncio
from dataclasses import dataclass
from typing import Optional
from loguru import logger


@dataclass
class GenerationResult:
    """Результат генерации"""
    success: bool
    image_url: Optional[str] = None
    seed: Optional[int] = None
    generation_time: Optional[float] = None
    error: Optional[str] = None


class Flux2FlexAPI:
    """API клиент для FLUX 2 Flex через fal.ai"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        os.environ["FAL_KEY"] = api_key
    
    async def generate(
        self,
        prompt: str,
        image_size: str = "square",
        output_format: str = "jpeg",
        num_inference_steps: int = 28,
        guidance_scale: float = 3.5,
        enable_prompt_expansion: bool = True,
        seed: Optional[int] = None,
    ) -> GenerationResult:
        """
        Генерация изображения.
        
        Args:
            prompt: Текстовый промпт
            image_size: Размер изображения
            output_format: Формат вывода (jpeg, png)
            num_inference_steps: Количество шагов
            guidance_scale: Guidance scale
            enable_prompt_expansion: Расширение промпта
            seed: Seed для воспроизводимости
        
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
            
            input_params = {
                "prompt": prompt,
                "image_size": image_size,
                "output_format": output_format,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
                "enable_prompt_expansion": enable_prompt_expansion,
                "enable_safety_checker": True,
            }
            
            if seed is not None:
                input_params["seed"] = seed
            
            logger.info(f"FLUX 2 Flex: Запуск генерации, size={image_size}")
            logger.debug(f"FLUX 2 Flex: Параметры: {input_params}")
            
            def run_generation():
                return fal_client.run(
                    "fal-ai/flux-2-flex",
                    arguments=input_params,
                )
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, run_generation)
            
            generation_time = time.time() - start_time
            
            if result and "images" in result and len(result["images"]) > 0:
                image_data = result["images"][0]
                return GenerationResult(
                    success=True,
                    image_url=image_data.get("url"),
                    seed=result.get("seed"),
                    generation_time=generation_time,
                )
            else:
                return GenerationResult(
                    success=False,
                    error="Не удалось получить изображение из ответа API"
                )
                
        except Exception as e:
            logger.error(f"FLUX 2 Flex API error: {e}")
            return GenerationResult(
                success=False,
                error=str(e)
            )
