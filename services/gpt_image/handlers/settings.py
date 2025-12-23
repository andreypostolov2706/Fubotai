"""
GPT-Image — Settings Handler
"""
from typing import TYPE_CHECKING

from ..config import DEFAULT_USER_SETTINGS
from .. import messages as msg
from .. import keyboards as kb

if TYPE_CHECKING:
    from ..service import GPTImageService


class SettingsHandler:
    """Обработчик настроек пользователя"""
    
    def __init__(self, service: "GPTImageService"):
        self.service = service
        self.core = service.core
    
    async def show_settings(self, user_id: int) -> dict:
        """Показать меню настроек"""
        settings = await self._get_settings(user_id)
        
        text = msg.SETTINGS_MENU.format(
            quality=msg.QUALITY_NAMES.get(settings["quality"], settings["quality"]),
            size=msg.SIZE_NAMES.get(settings["image_size"], settings["image_size"]),
            background=msg.BACKGROUND_NAMES.get(settings["background"], settings["background"]),
            format=msg.FORMAT_NAMES.get(settings["output_format"], settings["output_format"]),
        )
        
        return {
            "text": text,
            "keyboard": kb.settings_keyboard(),
        }
    
    async def show_quality_selection(self, user_id: int) -> dict:
        """Показать выбор качества"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_QUALITY.format(
            current=msg.QUALITY_NAMES.get(settings["quality"], settings["quality"])
        )
        
        return {
            "text": text,
            "keyboard": kb.settings_quality_keyboard(settings["quality"]),
        }
    
    async def show_size_selection(self, user_id: int) -> dict:
        """Показать выбор размера"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_SIZE.format(
            current=msg.SIZE_NAMES.get(settings["image_size"], settings["image_size"])
        )
        
        return {
            "text": text,
            "keyboard": kb.settings_size_keyboard(settings["image_size"]),
        }
    
    async def show_background_selection(self, user_id: int) -> dict:
        """Показать выбор фона"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_BACKGROUND.format(
            current=msg.BACKGROUND_NAMES.get(settings["background"], settings["background"])
        )
        
        return {
            "text": text,
            "keyboard": kb.settings_background_keyboard(settings["background"]),
        }
    
    async def show_format_selection(self, user_id: int) -> dict:
        """Показать выбор формата"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_FORMAT.format(
            current=msg.FORMAT_NAMES.get(settings["output_format"], settings["output_format"])
        )
        
        return {
            "text": text,
            "keyboard": kb.settings_format_keyboard(settings["output_format"]),
        }
    
    async def set_quality(self, user_id: int, value: str) -> dict:
        """Установить качество"""
        await self._update_setting(user_id, "quality", value)
        return await self.show_settings(user_id)
    
    async def set_size(self, user_id: int, value: str) -> dict:
        """Установить размер"""
        await self._update_setting(user_id, "image_size", value)
        return await self.show_settings(user_id)
    
    async def set_background(self, user_id: int, value: str) -> dict:
        """Установить фон"""
        await self._update_setting(user_id, "background", value)
        return await self.show_settings(user_id)
    
    async def set_format(self, user_id: int, value: str) -> dict:
        """Установить формат"""
        await self._update_setting(user_id, "output_format", value)
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
