"""
Veo Service — Settings Handler
"""
from typing import TYPE_CHECKING

from ..config import DEFAULT_USER_SETTINGS, DURATIONS, ASPECT_RATIOS_TEXT, DURATION_NAMES, ASPECT_RATIO_NAMES
from .. import messages as msg
from .. import keyboards as kb

if TYPE_CHECKING:
    from ..service import VeoService


class SettingsHandler:
    """Обработчик настроек пользователя"""
    
    def __init__(self, service: "VeoService"):
        self.service = service
        self.core = service.core
    
    async def show_settings(self, user_id: int) -> dict:
        """Показать меню настроек"""
        settings = await self._get_settings(user_id)
        
        text = msg.SETTINGS_MENU.format(
            duration=DURATION_NAMES.get(settings["duration"], settings["duration"]),
            aspect_ratio=ASPECT_RATIO_NAMES.get(settings["aspect_ratio"], settings["aspect_ratio"]),
            enhance="Да" if settings["enhance_prompt"] else "Нет",
        )
        
        return {
            "text": text,
            "keyboard": kb.settings_keyboard(),
        }
    
    async def show_duration_selection(self, user_id: int) -> dict:
        """Показать выбор длительности"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_DURATION.format(
            current=DURATION_NAMES.get(settings["duration"], settings["duration"])
        )
        
        return {
            "text": text,
            "keyboard": kb.duration_keyboard(settings["duration"]),
        }
    
    async def show_aspect_ratio_selection(self, user_id: int, mode: str = "text_to_video") -> dict:
        """Показать выбор соотношения сторон"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_ASPECT_RATIO.format(
            current=ASPECT_RATIO_NAMES.get(settings["aspect_ratio"], settings["aspect_ratio"])
        )
        
        return {
            "text": text,
            "keyboard": kb.aspect_ratio_keyboard(settings["aspect_ratio"], mode),
        }
    
    async def show_enhance_selection(self, user_id: int) -> dict:
        """Показать выбор улучшения промпта"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_ENHANCE.format(
            current="Включено" if settings["enhance_prompt"] else "Выключено"
        )
        
        return {
            "text": text,
            "keyboard": kb.enhance_keyboard(settings["enhance_prompt"]),
        }
    
    async def set_duration(self, user_id: int, duration: str) -> dict:
        """Установить длительность"""
        if duration not in DURATIONS:
            duration = "5s"
        
        await self.core.set_user_service_settings(user_id, {"duration": duration})
        return await self.show_settings(user_id)
    
    async def set_aspect_ratio(self, user_id: int, ratio: str) -> dict:
        """Установить соотношение сторон"""
        # Конвертируем из callback формата (16-9 → 16:9)
        ratio = ratio.replace("-", ":")
        
        if ratio not in ASPECT_RATIOS_TEXT and ratio not in ["auto", "auto_prefer_portrait"]:
            ratio = "16:9"
        
        await self.core.set_user_service_settings(user_id, {"aspect_ratio": ratio})
        return await self.show_settings(user_id)
    
    async def set_enhance(self, user_id: int, enhance: str) -> dict:
        """Установить улучшение промпта"""
        enhance_bool = enhance.lower() == "true"
        
        await self.core.set_user_service_settings(user_id, {"enhance_prompt": enhance_bool})
        return await self.show_settings(user_id)
    
    async def _get_settings(self, user_id: int) -> dict:
        """Получить настройки пользователя с дефолтами"""
        settings = await self.core.get_user_service_settings(user_id)
        if not settings:
            settings = {}
        
        for key, value in DEFAULT_USER_SETTINGS.items():
            if key not in settings:
                settings[key] = value
        
        return settings
