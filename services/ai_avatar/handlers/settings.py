"""
AI Avatar — Settings Handler
"""
from core.plugins.base_service import CallbackContext, Response
from .. import messages as msg
from .. import keyboards as kb


class SettingsHandler:
    """Обработчик настроек"""
    
    def __init__(self, service):
        self.service = service
    
    async def show_settings(self, ctx: CallbackContext) -> Response:
        """Показать меню настроек"""
        user_id = ctx.user_id
        
        # Получаем текущие настройки
        user_settings = await self.service.core_api.user_data.get_settings(
            user_id,
            self.service.info.id
        )
        
        quality = user_settings.get("quality", "480p")
        use_tts = user_settings.get("use_tts", False)
        
        text = msg.SETTINGS_MENU.format(
            quality=quality,
            use_tts="Включено" if use_tts else "Выключено"
        )
        
        return Response(
            text=text,
            keyboard=kb.settings_menu_keyboard(),
        )
    
    async def show_quality_settings(self, ctx: CallbackContext) -> Response:
        """Показать настройки качества"""
        user_id = ctx.user_id
        
        user_settings = await self.service.core_api.user_data.get_settings(
            user_id,
            self.service.info.id
        )
        
        current_quality = user_settings.get("quality", "480p")
        
        text = msg.QUALITY_SETTINGS.format(current_quality=current_quality)
        
        return Response(
            text=text,
            keyboard=kb.quality_settings_keyboard(current_quality),
        )
    
    async def set_quality(self, ctx: CallbackContext, quality: str) -> Response:
        """Установить качество видео"""
        user_id = ctx.user_id
        
        # Сохраняем настройку
        await self.service.core_api.user_data.set_setting(
            user_id,
            self.service.info.id,
            "quality",
            quality
        )
        
        # Возвращаемся к меню настроек
        return await self.show_settings(ctx)
