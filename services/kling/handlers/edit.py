"""
Kling — Image-to-Video Handler
"""
from typing import TYPE_CHECKING

from ..config import DEFAULT_USER_SETTINGS, MAX_PROMPT_LENGTH
from .. import messages as msg
from .. import keyboards as kb

if TYPE_CHECKING:
    from ..service import KlingService


class EditHandler:
    """Обработчик генерации видео из изображения (Image-to-Video)"""
    
    def __init__(self, service: "KlingService"):
        self.service = service
        self.core = service.core
    
    async def start_edit(self, user_id: int) -> dict:
        """Начать процесс — запросить изображение"""
        await self.core.set_user_state(user_id, "waiting_image", {"mode": "image_to_video"})
        
        return {
            "text": msg.IMAGE_TO_VIDEO_START,
            "keyboard": kb.cancel_keyboard(),
        }
    
    async def handle_image(self, user_id: int, image_url: str) -> dict:
        """Обработать загруженное изображение"""
        state_data = {
            "mode": "image_to_video",
            "input_image_url": image_url,
        }
        
        await self.core.set_user_state(user_id, "waiting_edit_prompt", state_data)
        
        return {
            "text": msg.IMAGE_TO_VIDEO_PROMPT,
            "keyboard": kb.cancel_keyboard(),
        }
    
    async def handle_prompt(self, user_id: int, prompt: str) -> dict:
        """Обработать промпт для генерации"""
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
        
        state, state_data = await self.core.get_user_state(user_id)
        if not state:
            return await self.start_edit(user_id)
        
        settings = await self._get_settings(user_id)
        
        state_data.update({
            "prompt": prompt.strip(),
            "duration": settings["duration"],
            "aspect_ratio": settings["aspect_ratio"],
            "audio": settings["audio"],
        })
        
        await self.core.set_user_state(user_id, "confirm_edit", state_data)
        
        return await self.show_confirmation(user_id, state_data)
    
    async def show_confirmation(self, user_id: int, state_data: dict) -> dict:
        """Показать экран подтверждения"""
        from ..api import FalClient
        
        duration = int(state_data["duration"])
        audio_enabled = state_data["audio"] == "on"
        
        cost_usd = FalClient.calculate_cost(duration, audio_enabled)
        
        margin = await self._get_margin()
        cost_usd_with_margin = cost_usd * (1 + margin)
        
        cost_gton = await self.service.usd_to_gton(cost_usd_with_margin)
        cost_fiat = await self.service.gton_to_fiat(cost_gton)
        
        balance = await self.core.get_balance(user_id)
        
        text = msg.IMAGE_TO_VIDEO_CONFIRM.format(
            prompt=state_data["prompt"][:500] + "..." if len(state_data["prompt"]) > 500 else state_data["prompt"],
            duration=state_data["duration"],
            aspect_ratio=msg.ASPECT_RATIO_NAMES.get(state_data["aspect_ratio"], state_data["aspect_ratio"]),
            audio=msg.AUDIO_NAMES.get(state_data["audio"], state_data["audio"]),
            cost_gton=f"{cost_gton:.4f}",
            cost_fiat=f"{cost_fiat:.2f}" if cost_fiat else "—",
            balance=f"{balance:.4f}",
        )
        
        return {
            "text": text,
            "keyboard": kb.confirm_keyboard("edit"),
        }
    
    async def update_param(self, user_id: int, param: str, value: str) -> dict:
        """Обновить параметр генерации"""
        state, state_data = await self.core.get_user_state(user_id)
        if not state:
            return await self.start_edit(user_id)
        
        if param == "duration":
            state_data["duration"] = value
        elif param == "aspect":
            state_data["aspect_ratio"] = value
        elif param == "audio":
            state_data["audio"] = value
        
        await self.core.set_user_state(user_id, "confirm_edit", state_data)
        
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
