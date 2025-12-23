"""
GPT-Image — Text-to-Image Handler
"""
from typing import TYPE_CHECKING, Optional, Dict, Any

from ..config import DEFAULT_USER_SETTINGS, MAX_PROMPT_LENGTH
from .. import messages as msg
from .. import keyboards as kb

if TYPE_CHECKING:
    from ..service import GPTImageService


class GenerateHandler:
    """Обработчик генерации изображений по тексту"""
    
    def __init__(self, service: "GPTImageService"):
        self.service = service
        self.core = service.core
    
    async def start_generation(self, user_id: int) -> dict:
        """Начать процесс генерации — запросить промпт"""
        await self.core.set_user_state(user_id, "waiting_prompt", {"mode": "text_to_image"})
        
        return {
            "text": msg.TEXT_TO_IMAGE_START,
            "keyboard": kb.cancel_keyboard(),
        }
    
    async def handle_prompt(self, user_id: int, prompt: str) -> dict:
        """Обработать введённый промпт"""
        if not prompt or not prompt.strip():
            return {
                "text": msg.ERROR_NO_PROMPT,
                "keyboard": kb.cancel_keyboard(),
            }
        
        if len(prompt) > MAX_PROMPT_LENGTH:
            return {
                "text": msg.ERROR_PROMPT_TOO_LONG.format(max=MAX_PROMPT_LENGTH),
                "keyboard": kb.cancel_keyboard(),
            }
        
        settings = await self._get_settings(user_id)
        
        state_data = {
            "mode": "text_to_image",
            "prompt": prompt.strip(),
            "quality": settings["quality"],
            "image_size": settings["image_size"],
            "background": settings["background"],
            "output_format": settings["output_format"],
        }
        
        await self.core.set_user_state(user_id, "confirm_generation", state_data)
        
        return await self.show_confirmation(user_id, state_data)
    
    async def show_confirmation(self, user_id: int, state_data: dict) -> dict:
        """Показать экран подтверждения"""
        from ..api import FalClient
        
        cost_usd = FalClient.calculate_cost(
            state_data["quality"],
            state_data["image_size"]
        )
        
        margin = await self._get_margin()
        cost_usd_with_margin = cost_usd * (1 + margin)
        
        cost_gton = await self.service.usd_to_gton(cost_usd_with_margin)
        cost_fiat = await self.service.gton_to_fiat(cost_gton)
        
        balance = await self.core.get_balance(user_id)
        
        text = msg.TEXT_TO_IMAGE_CONFIRM.format(
            prompt=state_data["prompt"][:500] + "..." if len(state_data["prompt"]) > 500 else state_data["prompt"],
            quality=msg.QUALITY_NAMES.get(state_data["quality"], state_data["quality"]),
            size=msg.SIZE_NAMES.get(state_data["image_size"], state_data["image_size"]),
            background=msg.BACKGROUND_NAMES.get(state_data["background"], state_data["background"]),
            format=msg.FORMAT_NAMES.get(state_data["output_format"], state_data["output_format"]),
            cost_gton=f"{cost_gton:.4f}",
            cost_fiat=f"{cost_fiat:.2f}" if cost_fiat else "—",
            balance=f"{balance:.4f}",
        )
        
        return {
            "text": text,
            "keyboard": kb.confirm_keyboard("generate"),
        }
    
    async def update_param(self, user_id: int, param: str, value: str) -> dict:
        """Обновить параметр генерации"""
        state, state_data = await self.core.get_user_state(user_id)
        if not state:
            return await self.start_generation(user_id)
        
        if not state_data:
            state_data = {}
        
        if param == "quality":
            state_data["quality"] = value
        elif param == "size":
            state_data["image_size"] = value
        elif param == "background":
            state_data["background"] = value
        elif param == "format":
            state_data["output_format"] = value
        
        await self.core.set_user_state(user_id, "confirm_generation", state_data)
        
        return await self.show_confirmation(user_id, state_data)
    
    async def _get_settings(self, user_id: int) -> dict:
        """Получить настройки пользователя"""
        settings = await self.core.get_user_service_settings(user_id)
        
        result = DEFAULT_USER_SETTINGS.copy()
        if settings:
            result.update(settings)
        
        return result
    
    async def _get_margin(self) -> float:
        """Получить маржу из конфига сервиса"""
        config = await self.service.get_service_config()
        return config.get("margin_multiplier", 0.3)
