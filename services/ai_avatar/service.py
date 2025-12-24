"""
AI Avatar — Главный класс сервиса
"""
from __future__ import annotations

from typing import Optional
from loguru import logger

from core.plugins.base_service import (
    BaseService, ServiceInfo, MenuItem, Response,
    UserServiceDTO, CallbackContext, MessageContext
)
from core.plugins.core_api import CoreAPI

from .config import (
    SERVICE_ID, SERVICE_NAME, SERVICE_ICON, SERVICE_VERSION,
    SERVICE_AUTHOR, SERVICE_DESCRIPTION, DEFAULT_SERVICE_CONFIG,
    DEFAULT_USER_SETTINGS
)
from .handlers import GenerateHandler, SettingsHandler, HistoryHandler
from . import messages as msg
from . import keyboards as kb


class AIAvatarService(BaseService):
    """
    AI Avatar — Сервис создания говорящих видео.
    
    Использует fal.ai Creatify Aurora API для превращения
    фото в говорящее видео с синхронизацией губ.
    """
    
    def __init__(self, core_api: CoreAPI):
        super().__init__(core_api)
        
        # Инициализируем handlers
        self.generate_handler = GenerateHandler(self)
        self.settings_handler = SettingsHandler(self)
        self.history_handler = HistoryHandler(self)
    
    # ==================== ИНФОРМАЦИЯ ====================
    
    @property
    def info(self) -> ServiceInfo:
        return ServiceInfo(
            id=SERVICE_ID,
            name=SERVICE_NAME,
            description=SERVICE_DESCRIPTION,
            version=SERVICE_VERSION,
            author=SERVICE_AUTHOR,
            icon=SERVICE_ICON,
        )
    
    @property
    def permissions(self) -> list[str]:
        return [
            "balance:read",
            "balance:deduct",
            "balance:add",
            "notifications:send",
            "analytics:track",
        ]
    
    @property
    def features(self) -> dict:
        return {
            "subscriptions": False,
            "broadcasts": False,
            "partner_menu": False,
            "voice_messages": True,  # Поддержка голосовых сообщений
        }
    
    # ==================== УСТАНОВКА ====================
    
    async def install(self) -> bool:
        """Установка сервиса - создание таблиц БД"""
        try:
            from .database import init_db
            init_db()
            logger.info(f"AI Avatar: База данных инициализирована")
            return True
        except Exception as e:
            logger.error(f"AI Avatar: Ошибка установки: {e}")
            return False
    
    async def uninstall(self) -> bool:
        """Удаление сервиса"""
        try:
            logger.info(f"AI Avatar: Сервис удалён")
            return True
        except Exception as e:
            logger.error(f"AI Avatar: Ошибка удаления: {e}")
            return False
    
    # ==================== МЕНЮ ====================
    
    def get_user_menu_items(self, user_id: int, user_data: UserServiceDTO) -> list[MenuItem]:
        """Кнопка в главном меню бота"""
        return [
            MenuItem(
                text=f"{SERVICE_ICON} {SERVICE_NAME}",
                callback=f"service:{SERVICE_ID}:main",
                order=20,
            )
        ]
    
    def get_admin_menu_items(self) -> list[MenuItem]:
        """Кнопка в админ-панели"""
        return [
            MenuItem(
                text=f"{SERVICE_ICON} {SERVICE_NAME}",
                callback=f"service:{SERVICE_ID}:admin",
                order=50,
            )
        ]
    
    # ==================== ОБРАБОТКА CALLBACK ====================
    
    async def handle_callback(
        self,
        user_id: int,
        action: str,
        params: dict,
        context: CallbackContext
    ) -> Response:
        """
        Обработка callback от пользователя.
        
        Формат: service:ai_avatar:{action}:{params}
        """
        logger.info(f"AI Avatar: handle_callback called - action={action}, params={params}, user_id={user_id}")
        
        try:
            # Главное меню
            if action == "main":
                logger.info(f"AI Avatar: Showing main menu for user {user_id}")
                return await self._show_main_menu(user_id)
            
            # Генерация
            elif action == "generate":
                return await self.generate_handler.start_generation(context)
            
            # Выбор режима (audio/text)
            elif action == "mode":
                mode = params.get("0") or params.get("id")
                return await self.generate_handler.handle_mode_choice(context, mode)
            
            # Пропустить промпт
            elif action == "skip_prompt":
                return await self.generate_handler.show_confirmation(user_id)
            
            # Подтверждение генерации
            elif action == "confirm":
                return await self.generate_handler.confirm_generation(context)
            
            # Настройки
            elif action == "settings":
                sub_action = params.get("0") or params.get("id")
                
                if sub_action == "quality":
                    return await self.settings_handler.show_quality_settings(context)
                else:
                    return await self.settings_handler.show_settings(context)
            
            # Установка качества
            elif action == "set_quality":
                quality = params.get("0") or params.get("id")
                return await self.settings_handler.set_quality(context, quality)
            
            # История
            elif action == "history":
                page = int(params.get("0", 0))
                return await self.history_handler.show_history(context, page)
            
            # Скачать из истории
            elif action == "download":
                generation_id = int(params.get("0") or params.get("id"))
                return await self.history_handler.download_video(context, generation_id)
            
            # Повторить генерацию
            elif action == "repeat":
                generation_id = int(params.get("0") or params.get("id"))
                return await self.history_handler.repeat_generation(context, generation_id)
            
            # Файл не пришёл
            elif action == "file_issue":
                generation_id = int(params.get("0") or params.get("id"))
                return Response(
                    text=msg.FILE_NOT_RECEIVED.format(generation_id=generation_id),
                    keyboard=kb.back_to_main_keyboard(),
                )
            
            # Отмена
            elif action == "cancel":
                await self.core_api.user_state.clear(user_id, f"{SERVICE_ID}:*")
                return await self._show_main_menu(user_id)
            
            # Неизвестное действие
            else:
                logger.warning(f"AI Avatar: Неизвестное действие: {action}")
                return await self._show_main_menu(user_id)
                
        except Exception as e:
            logger.error(f"AI Avatar: Ошибка обработки callback: {e}")
            return Response(
                text=msg.ERROR_UNKNOWN.format(error_message=str(e)),
                keyboard=kb.back_to_main_keyboard(),
            )
    
    # ==================== ОБРАБОТКА СООБЩЕНИЙ ====================
    
    async def handle_message(
        self,
        user_id: int,
        context: MessageContext
    ) -> Optional[Response]:
        """
        Обработка текстовых сообщений и медиа от пользователя.
        """
        # Получаем текущее состояние
        state = await self.core_api.user_state.get(
            user_id,
            f"{SERVICE_ID}:state"
        )
        
        if not state:
            return None
        
        try:
            # Ожидание изображения
            if state == "awaiting_image":
                return await self.generate_handler.handle_image_upload(context)
            
            # Ожидание аудио
            elif state == "awaiting_audio":
                return await self.generate_handler.handle_audio_upload(context)
            
            # Ожидание текста для TTS
            elif state == "awaiting_text":
                return await self.generate_handler.handle_text_input(context)
            
            # Ожидание промпта
            elif state == "awaiting_prompt":
                # TODO: Обработка кастомного промпта
                return await self.generate_handler.show_confirmation(user_id)
            
            return None
            
        except Exception as e:
            logger.error(f"AI Avatar: Ошибка обработки сообщения: {e}")
            return Response(
                text=msg.ERROR_UNKNOWN.format(error_message=str(e)),
                keyboard=kb.back_to_main_keyboard(),
            )
    
    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================
    
    async def _show_main_menu(self, user_id: int) -> Response:
        """Показать главное меню сервиса"""
        # Очищаем состояние
        await self.core.user_state.clear(user_id, f"{SERVICE_ID}:*")
        
        return Response(
            text=msg.MAIN_MENU,
            keyboard=kb.main_menu_keyboard(),
        )
    
    async def get_config_value(self, key: str, default=None):
        """Получить значение из конфигурации сервиса"""
        config = await self.core.service_config.get(SERVICE_ID)
        return config.get(key, default)
    
    # ==================== КОНФИГУРАЦИЯ ====================
    
    async def get_default_config(self) -> dict:
        """Конфигурация по умолчанию"""
        return DEFAULT_SERVICE_CONFIG
    
    async def get_default_user_settings(self) -> dict:
        """Настройки пользователя по умолчанию"""
        return DEFAULT_USER_SETTINGS
