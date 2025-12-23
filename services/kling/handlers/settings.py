"""
Kling — Settings Handler
"""
from typing import TYPE_CHECKING

from ..config import DEFAULT_USER_SETTINGS
from .. import messages as msg
from .. import keyboards as kb

if TYPE_CHECKING:
    from ..service import KlingService


class SettingsHandler:
    """Обработчик настроек пользователя"""
    
    def __init__(self, service: "KlingService"):
        self.service = service
        self.core = service.core
    
    async def show_settings(self, user_id: int) -> dict:
        """Показать меню настроек"""
        settings = await self._get_settings(user_id)
        
        text = msg.SETTINGS_MENU.format(
            duration=msg.DURATION_NAMES.get(settings["duration"], settings["duration"]),
            aspect_ratio=msg.ASPECT_RATIO_NAMES.get(settings["aspect_ratio"], settings["aspect_ratio"]),
            audio=msg.AUDIO_NAMES.get(settings["audio"], settings["audio"]),
        )
        
        return {
            "text": text,
            "keyboard": kb.settings_keyboard(),
        }
    
    async def show_duration_selection(self, user_id: int) -> dict:
        """Показать выбор длительности"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_DURATION.format(
            current=msg.DURATION_NAMES.get(settings["duration"], settings["duration"])
        )
        
        return {
            "text": text,
            "keyboard": kb.settings_duration_keyboard(settings["duration"]),
        }
    
    async def show_aspect_selection(self, user_id: int) -> dict:
        """Показать выбор соотношения сторон"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_ASPECT_RATIO.format(
            current=msg.ASPECT_RATIO_NAMES.get(settings["aspect_ratio"], settings["aspect_ratio"])
        )
        
        return {
            "text": text,
            "keyboard": kb.settings_aspect_keyboard(settings["aspect_ratio"]),
        }
    
    async def show_audio_selection(self, user_id: int) -> dict:
        """Показать выбор аудио"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_AUDIO.format(
            current=msg.AUDIO_NAMES.get(settings["audio"], settings["audio"])
        )
        
        return {
            "text": text,
            "keyboard": kb.settings_audio_keyboard(settings["audio"]),
        }
    
    async def set_duration(self, user_id: int, value: str) -> dict:
        """Установить длительность"""
        await self._update_setting(user_id, "duration", value)
        return await self.show_settings(user_id)
    
    async def set_aspect(self, user_id: int, value: str) -> dict:
        """Установить соотношение сторон"""
        await self._update_setting(user_id, "aspect_ratio", value)
        return await self.show_settings(user_id)
    
    async def set_audio(self, user_id: int, value: str) -> dict:
        """Установить аудио"""
        await self._update_setting(user_id, "audio", value)
        return await self.show_settings(user_id)
    
    async def _get_settings(self, user_id: int) -> dict:
        """Получить настройки пользователя"""
        settings = await self.core.get_user_service_settings(user_id)
        
        result = DEFAULT_USER_SETTINGS.copy()
        if settings:
            result.update(settings)
        
        return result
    
    async def _update_setting(self, user_id: int, key: str, value: str):
        """Обновить настройку"""
        settings = await self._get_settings(user_id)
        settings[key] = value
        await self.core.set_user_service_settings(user_id, settings)
