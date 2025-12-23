"""
Nano Banano — Settings Handler
"""
from typing import TYPE_CHECKING

from ..config import DEFAULT_USER_SETTINGS, ASPECT_RATIOS, OUTPUT_FORMATS, RESOLUTIONS
from .. import messages as msg
from .. import keyboards as kb

if TYPE_CHECKING:
    from ..service import NanoBananoService


class SettingsHandler:
    """Обработчик настроек пользователя"""
    
    def __init__(self, service: "NanoBananoService"):
        self.service = service
        self.core = service.core
    
    async def show_settings(self, user_id: int) -> dict:
        """Показать меню настроек"""
        settings = await self._get_settings(user_id)
        
        text = msg.SETTINGS_MENU.format(
            model_name=msg.MODEL_NAMES.get(settings["model"], settings["model"]),
            aspect_ratio=settings["aspect_ratio"],
            output_format=settings["output_format"].upper(),
            resolution=settings["resolution"],
        )
        
        return {
            "text": text,
            "keyboard": kb.settings_keyboard(),
        }
    
    async def show_model_selection(self, user_id: int) -> dict:
        """Показать выбор модели"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_MODEL.format(current=msg.MODEL_NAMES.get(settings["model"], settings["model"]))
        
        return {
            "text": text,
            "keyboard": kb.model_selection_keyboard(settings["model"]),
        }
    
    async def show_aspect_ratio_selection(self, user_id: int) -> dict:
        """Показать выбор размера"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_ASPECT_RATIO.format(current=settings["aspect_ratio"])
        
        return {
            "text": text,
            "keyboard": kb.aspect_ratio_keyboard(settings["aspect_ratio"]),
        }
    
    async def show_format_selection(self, user_id: int) -> dict:
        """Показать выбор формата"""
        settings = await self._get_settings(user_id)
        
        text = msg.SELECT_FORMAT.format(current=settings["output_format"].upper())
        
        return {
            "text": text,
            "keyboard": kb.format_keyboard(settings["output_format"]),
        }
    
    async def show_resolution_selection(self, user_id: int) -> dict:
        """Показать выбор разрешения"""
        settings = await self._get_settings(user_id)
        is_pro = settings["model"] == "nano_banana_pro"
        
        text = msg.SELECT_RESOLUTION.format(current=settings["resolution"])
        
        return {
            "text": text,
            "keyboard": kb.resolution_keyboard(settings["resolution"], is_pro),
        }
    
    async def set_model(self, user_id: int, model: str) -> dict:
        """Установить модель"""
        if model not in ["nano_banana", "nano_banana_pro"]:
            model = "nano_banana"
        
        await self.core.set_user_service_settings(user_id, {"model": model})
        return await self.show_settings(user_id)
    
    async def set_aspect_ratio(self, user_id: int, ratio: str) -> dict:
        """Установить размер"""
        # Конвертируем обратно из callback формата (16-9 → 16:9)
        ratio = ratio.replace("-", ":")
        
        if ratio not in ASPECT_RATIOS:
            ratio = "1:1"
        
        await self.core.set_user_service_settings(user_id, {"aspect_ratio": ratio})
        return await self.show_settings(user_id)
    
    async def set_format(self, user_id: int, fmt: str) -> dict:
        """Установить формат"""
        if fmt not in OUTPUT_FORMATS:
            fmt = "png"
        
        await self.core.set_user_service_settings(user_id, {"output_format": fmt})
        return await self.show_settings(user_id)
    
    async def set_resolution(self, user_id: int, resolution: str) -> dict:
        """Установить разрешение"""
        if resolution not in RESOLUTIONS:
            resolution = "1K"
        
        await self.core.set_user_service_settings(user_id, {"resolution": resolution})
        return await self.show_settings(user_id)
    
    async def _get_settings(self, user_id: int) -> dict:
        """Получить настройки пользователя с дефолтами"""
        settings = await self.core.get_user_service_settings(user_id)
        if not settings:
            settings = {}
        
        # Применяем дефолты
        for key, value in DEFAULT_USER_SETTINGS.items():
            if key not in settings:
                settings[key] = value
        
        return settings
