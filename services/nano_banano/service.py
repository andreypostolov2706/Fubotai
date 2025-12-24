"""
Nano Banano — Главный класс сервиса
"""
from __future__ import annotations

from typing import Optional
from datetime import datetime
from loguru import logger

from core.plugins.base_service import (
    BaseService, ServiceInfo, MenuItem, Response,
    UserServiceDTO, CallbackContext, MessageContext, MessageDTO
)
from core.plugins.core_api import CoreAPI

from .config import (
    SERVICE_ID, SERVICE_NAME, SERVICE_ICON, SERVICE_VERSION,
    SERVICE_AUTHOR, SERVICE_DESCRIPTION, DEFAULT_SERVICE_CONFIG,
    DEFAULT_USER_SETTINGS, PROGRESS_FRAMES, ESTIMATED_GENERATION_TIME
)
from .handlers import GenerateHandler, EditHandler, HistoryHandler, SettingsHandler
from . import messages as msg
from . import keyboards as kb


class NanoBananoService(BaseService):
    """
    Nano Banano — Сервис генерации и редактирования изображений.
    
    Использует fal.ai API (Google Gemini) для генерации изображений
    по текстовому описанию и редактирования существующих фото.
    """
    
    def __init__(self, core_api: CoreAPI):
        super().__init__(core_api)
        
        # Инициализируем handlers
        self.generate_handler = GenerateHandler(self)
        self.edit_handler = EditHandler(self)
        self.history_handler = HistoryHandler(self)
        self.settings_handler = SettingsHandler(self)
    
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
            "balance:add",  # Для возврата при ошибке
            "notifications:send",
            "analytics:track",
        ]
    
    @property
    def features(self) -> dict:
        return {
            "subscriptions": False,
            "broadcasts": False,
            "partner_menu": False,
            "voice_messages": False,
        }
    
    # ==================== УСТАНОВКА ====================
    
    async def install(self) -> bool:
        """Установка сервиса - создание таблиц БД"""
        try:
            from .database import init_db
            init_db()
            logger.info(f"Nano Banano: База данных инициализирована")
            return True
        except Exception as e:
            logger.error(f"Nano Banano: Ошибка установки: {e}")
            return False
    
    async def uninstall(self) -> bool:
        """Удаление сервиса"""
        try:
            # Можно добавить удаление таблиц если нужно
            logger.info(f"Nano Banano: Сервис удалён")
            return True
        except Exception as e:
            logger.error(f"Nano Banano: Ошибка удаления: {e}")
            return False
    
    # ==================== МЕНЮ ====================
    
    def get_user_menu_items(self, user_id: int, user_data: UserServiceDTO) -> list[MenuItem]:
        """Кнопка в главном меню бота"""
        return [
            MenuItem(
                text=f"{SERVICE_ICON} {SERVICE_NAME}",
                callback=f"service:{SERVICE_ID}:main",
                order=10,  # Первый в меню
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
        
        Формат: service:nano_banano:{action}:{params}
        """
        logger.debug(f"Nano Banano: callback action={action}, params={params}")
        
        try:
            # Главное меню
            if action == "main":
                return await self._show_main_menu(user_id)
            
            # Генерация (Text-to-Image)
            elif action == "generate":
                result = await self.generate_handler.start_generation(user_id)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Редактирование (Image-to-Image)
            elif action == "edit":
                result = await self.edit_handler.start_edit(user_id)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Пропустить негативный промпт
            elif action == "skip_negative":
                state, state_data = await self.core.get_user_state(user_id)
                if state_data:
                    if state_data.get("mode") == "edit":
                        result = await self.edit_handler.skip_negative(user_id, state_data)
                    else:
                        result = await self.generate_handler.skip_negative(user_id, state_data)
                    return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Добавить ещё фото
            elif action == "add_more_images":
                # Просто остаёмся в состоянии ожидания фото
                return Response(
                    text="📷 Отправьте ещё фотографию.",
                    keyboard=kb.cancel_keyboard(),
                )
            
            # Фото получены - готово
            elif action == "images_done":
                state, state_data = await self.core.get_user_state(user_id)
                if state_data:
                    result = await self.edit_handler.images_done(user_id, state_data)
                    return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Подтверждение генерации
            elif action == "confirm":
                sub_action = params.get("0") or params.get("id")
                state, state_data = await self.core.get_user_state(user_id)
                
                if sub_action == "create" and state_data:
                    if state_data.get("mode") == "edit":
                        result = await self.edit_handler.execute_edit(user_id, state_data, context)
                    else:
                        result = await self.generate_handler.execute_generation(user_id, state_data, context)
                    
                    # Если уже отправлено напрямую - возвращаем answer
                    if result.get("sent"):
                        return Response(
                            text="",
                            action="answer",
                        )
                    
                    # Если есть фото - возвращаем специальный Response
                    if result.get("photo_url"):
                        return Response(
                            text=result["text"],
                            keyboard=result["keyboard"],
                            media_type="photo",
                            media_url=result["photo_url"],
                            action="send",
                        )
                    return Response(text=result["text"], keyboard=result["keyboard"])
                
                elif sub_action == "edit":
                    return Response(
                        text=msg.EDIT_PARAMS_MENU,
                        keyboard=kb.edit_params_keyboard(),
                    )
            
            # Изменение параметров
            elif action == "edit_param":
                param = params.get("0") or params.get("id")
                state, state_data = await self.core.get_user_state(user_id)
                
                if param == "prompt":
                    await self.core.set_user_state(user_id, "editing_prompt", state_data)
                    return Response(
                        text=msg.PROMPT_REQUEST,
                        keyboard=kb.cancel_keyboard(),
                    )
                elif param == "negative":
                    await self.core.set_user_state(user_id, "editing_negative", state_data)
                    return Response(
                        text=msg.NEGATIVE_PROMPT_REQUEST,
                        keyboard=kb.skip_negative_keyboard(),
                    )
                elif param == "model":
                    result = await self.settings_handler.show_model_selection(user_id)
                    return Response(text=result["text"], keyboard=result["keyboard"])
                elif param == "ratio":
                    result = await self.settings_handler.show_aspect_ratio_selection(user_id)
                    return Response(text=result["text"], keyboard=result["keyboard"])
                elif param == "format":
                    result = await self.settings_handler.show_format_selection(user_id)
                    return Response(text=result["text"], keyboard=result["keyboard"])
                elif param == "resolution":
                    result = await self.settings_handler.show_resolution_selection(user_id)
                    return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Вернуться к подтверждению
            elif action == "back_to_confirm":
                state, state_data = await self.core.get_user_state(user_id)
                if state_data:
                    if state_data.get("mode") == "edit":
                        result = await self.edit_handler._show_confirmation(user_id, state_data)
                    else:
                        result = await self.generate_handler._show_confirmation(user_id, state_data)
                    return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Настройки
            elif action == "settings":
                sub_action = params.get("0") or params.get("id")
                
                if sub_action == "model":
                    result = await self.settings_handler.show_model_selection(user_id)
                elif sub_action == "ratio":
                    result = await self.settings_handler.show_aspect_ratio_selection(user_id)
                elif sub_action == "format":
                    result = await self.settings_handler.show_format_selection(user_id)
                elif sub_action == "resolution":
                    result = await self.settings_handler.show_resolution_selection(user_id)
                else:
                    # Проверяем контекст - если в процессе генерации, показываем edit_params
                    state, state_data = await self.core.get_user_state(user_id)
                    if state and state == "confirming" and state_data:
                        return Response(
                            text=msg.EDIT_PARAMS_MENU,
                            keyboard=kb.edit_params_keyboard()
                        )
                    result = await self.settings_handler.show_settings(user_id)
                
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Установка настроек
            elif action == "set":
                setting = params.get("0")
                value = params.get("1")
                
                if setting == "model":
                    result = await self.settings_handler.set_model(user_id, value)
                elif setting == "ratio":
                    result = await self.settings_handler.set_aspect_ratio(user_id, value)
                elif setting == "format":
                    result = await self.settings_handler.set_format(user_id, value)
                elif setting == "resolution":
                    result = await self.settings_handler.set_resolution(user_id, value)
                else:
                    result = await self.settings_handler.show_settings(user_id)
                
                # Проверяем, есть ли активное состояние генерации
                state, state_data = await self.core.get_user_state(user_id)
                if state and state == "confirming" and state_data:
                    # Возвращаемся к подтверждению генерации
                    if state_data.get("mode") == "edit":
                        result = await self.edit_handler._show_confirmation(user_id, state_data)
                    else:
                        result = await self.generate_handler._show_confirmation(user_id, state_data)
                
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # История
            elif action == "history":
                sub_action = params.get("0")
                
                if sub_action == "page":
                    page = int(params.get("1", 1))
                    result = await self.history_handler.show_history(user_id, page)
                elif sub_action == "view":
                    gen_id = int(params.get("1", 0))
                    result = await self.history_handler.view_generation(user_id, gen_id)
                    
                    if result.get("photo_url") or result.get("file_id"):
                        return Response(
                            text=result["text"],
                            keyboard=result["keyboard"],
                            media_type="photo",
                            media_url=result.get("photo_url"),
                            media_file_id=result.get("file_id"),
                            action="send",
                        )
                else:
                    result = await self.history_handler.show_history(user_id)
                
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Повторная отправка результата (без генерации)
            elif action == "resend":
                gen_id = int(params.get("0") or params.get("id", 0))
                return await self._resend_result(user_id, gen_id, context)
            
            # Удалить генерацию
            elif action == "delete":
                gen_id = int(params.get("0") or params.get("id", 0))
                result = await self.history_handler.delete_generation(user_id, gen_id)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Галерея
            elif action == "gallery":
                sub_action = params.get("0")
                gen_id = int(params.get("1") or params.get("id", 0))
                
                if sub_action == "confirm":
                    config = await self.core.get_service_config()
                    if not config.get("gallery_enabled") or not config.get("gallery_channel_id"):
                        return Response(
                            text=msg.GALLERY_DISABLED,
                            keyboard=kb.back_to_main_keyboard(),
                        )
                    return Response(
                        text=msg.GALLERY_CONFIRM,
                        keyboard=kb.gallery_confirm_keyboard(gen_id),
                    )
                
                elif sub_action == "publish":
                    result = await self._publish_to_gallery(user_id, gen_id)
                    return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Отмена
            elif action == "cancel":
                await self.core.clear_user_state(user_id)
                return await self._show_main_menu(user_id)
            
            # Неизвестное действие
            return Response(text="❌ Неизвестное действие", keyboard=kb.back_to_main_keyboard())
            
        except Exception as e:
            logger.error(f"Nano Banano: Ошибка обработки callback: {e}")
            return Response(
                text=f"❌ Произошла ошибка: {e}",
                keyboard=kb.back_to_main_keyboard(),
            )
    
    # ==================== ОБРАБОТКА СООБЩЕНИЙ ====================
    
    async def handle_message(
        self,
        user_id: int,
        message: MessageDTO,
        context: MessageContext
    ) -> Response:
        """Обработка текстовых сообщений и фото"""
        state, state_data = await self.core.get_user_state(user_id)
        
        if not state:
            return Response(
                text="Используйте кнопки меню для взаимодействия.",
                keyboard=kb.main_menu_keyboard(),
            )
        
        try:
            # Ожидание промпта для генерации
            if state == "waiting_prompt":
                if not message.text:
                    return Response(
                        text="❌ Пожалуйста, введите текстовое описание.",
                        keyboard=kb.cancel_keyboard(),
                    )
                result = await self.generate_handler.handle_prompt(user_id, message.text, state_data)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Ожидание негативного промпта
            elif state == "waiting_negative":
                if not message.text:
                    return Response(
                        text="❌ Пожалуйста, введите текст или нажмите 'Пропустить'.",
                        keyboard=kb.skip_negative_keyboard(),
                    )
                
                if state_data.get("mode") == "edit":
                    result = await self.edit_handler.handle_negative(user_id, message.text, state_data)
                else:
                    result = await self.generate_handler.handle_negative(user_id, message.text, state_data)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Ожидание фото для редактирования
            elif state == "waiting_images":
                if not message.photo_file_id:
                    return Response(
                        text="❌ Пожалуйста, отправьте фотографию.",
                        keyboard=kb.cancel_keyboard(),
                    )
                
                # Скачиваем и загружаем изображение сразу
                from .api import FalClient
                
                config = await self.core.get_service_config()
                api_key = config.get("fal_api_key", "")
                
                if not api_key:
                    return Response(
                        text="❌ API ключ не настроен.",
                        keyboard=kb.back_to_main_keyboard(),
                    )
                
                # Скачиваем из Telegram напрямую через bot
                image_data = None
                
                if not context.bot:
                    logger.error("Bot not available in context")
                else:
                    try:
                        logger.info(f"Downloading file: {message.photo_file_id}")
                        file = await context.bot.get_file(message.photo_file_id)
                        logger.info(f"File path: {file.file_path}")
                        
                        # Используем встроенный метод download_as_bytearray
                        image_data = bytes(await file.download_as_bytearray())
                        logger.info(f"Downloaded {len(image_data)} bytes")
                    except Exception as e:
                        logger.error(f"Error downloading image: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                
                if not image_data:
                    return Response(
                        text="❌ Не удалось загрузить изображение. Попробуйте отправить другое фото.",
                        keyboard=kb.cancel_keyboard(),
                    )
                
                # Загружаем на fal.ai
                client = FalClient(api_key)
                uploaded_url = await client.upload_image(image_data)
                if not uploaded_url:
                    return Response(
                        text="❌ Не удалось загрузить изображение на сервер. Попробуйте ещё раз.",
                        keyboard=kb.cancel_keyboard(),
                    )
                
                # Сохраняем URL загруженного изображения
                result = await self.edit_handler.handle_image(user_id, uploaded_url, state_data)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Ожидание промпта для редактирования
            elif state == "waiting_edit_prompt":
                if not message.text:
                    return Response(
                        text="❌ Пожалуйста, опишите что нужно сделать с фото.",
                        keyboard=kb.cancel_keyboard(),
                    )
                result = await self.edit_handler.handle_edit_prompt(user_id, message.text, state_data)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Редактирование промпта
            elif state == "editing_prompt":
                if not message.text:
                    return Response(
                        text="❌ Пожалуйста, введите новый промпт.",
                        keyboard=kb.cancel_keyboard(),
                    )
                state_data["prompt"] = message.text
                if state_data.get("mode") == "edit":
                    result = await self.edit_handler._show_confirmation(user_id, state_data)
                else:
                    result = await self.generate_handler._show_confirmation(user_id, state_data)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Редактирование негативного промпта
            elif state == "editing_negative":
                state_data["negative_prompt"] = message.text if message.text else None
                if state_data.get("mode") == "edit":
                    result = await self.edit_handler._show_confirmation(user_id, state_data)
                else:
                    result = await self.generate_handler._show_confirmation(user_id, state_data)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Неизвестное состояние
            await self.core.clear_user_state(user_id)
            return await self._show_main_menu(user_id)
            
        except Exception as e:
            logger.error(f"Nano Banano: Ошибка обработки сообщения: {e}")
            await self.core.clear_user_state(user_id)
            return Response(
                text=f"❌ Произошла ошибка: {e}",
                keyboard=kb.back_to_main_keyboard(),
            )
    
    # ==================== ПРИВАТНЫЕ МЕТОДЫ ====================
    
    async def _show_main_menu(self, user_id: int) -> Response:
        """Показать главное меню сервиса"""
        balance = await self.core.get_balance(user_id)
        
        # Ориентировочная стоимость (минимальная цена nano_banana)
        config = await self.core.get_service_config()
        margin = config.get("margin_multiplier", 0.3)
        base_price = 0.04  # nano_banana base price
        price_usd = base_price * (1 + margin)
        price_gton = await self._usd_to_gton(price_usd)
        
        text = msg.MAIN_MENU.format(
            balance=f"{balance:.4f}",
            price=f"{price_gton:.4f}"
        )
        
        return Response(
            text=text,
            keyboard=kb.main_menu_keyboard(),
        )
    
    async def _publish_to_gallery(self, user_id: int, generation_id: int) -> dict:
        """Опубликовать генерацию в галерею"""
        from .database import get_session, Generation
        
        config = await self.core.get_service_config()
        channel_id = config.get("gallery_channel_id", "")
        
        if not channel_id:
            return {
                "text": msg.GALLERY_DISABLED,
                "keyboard": kb.back_to_main_keyboard(),
            }
        
        with get_session() as session:
            gen = session.query(Generation).filter(
                Generation.id == generation_id,
                Generation.user_id == user_id
            ).first()
            
            if not gen:
                return {
                    "text": "❌ Генерация не найдена",
                    "keyboard": kb.back_to_main_keyboard(),
                }
            
            if gen.published_to_gallery:
                return {
                    "text": "⚠️ Это изображение уже опубликовано в галерее",
                    "keyboard": kb.back_to_main_keyboard(),
                }
            
            # Получаем username автора
            user = await self.core.get_user_by_id(user_id)
            author = f"@{user.telegram_username}" if user and user.telegram_username else "Аноним"
            
            # Формируем текст поста
            post_text = msg.GALLERY_POST.format(
                prompt=gen.prompt,
                model_name=msg.MODEL_NAMES.get(gen.model, gen.model),
                author=author,
            )
            
            # Помечаем как опубликованное
            gen.published_to_gallery = True
            gen.published_at = datetime.utcnow()
            session.commit()
            
            # TODO: Отправить в канал через бот
            # Это требует доступа к боту, который не доступен из сервиса напрямую
            # Нужно добавить метод в CoreAPI или использовать события
            
            return {
                "text": msg.GALLERY_SUCCESS,
                "keyboard": kb.back_to_main_keyboard(),
                "gallery_post": {
                    "channel_id": channel_id,
                    "text": post_text,
                    "photo_url": gen.image_url,
                    "file_id": gen.file_id,
                },
            }
    
    async def _resend_result(self, user_id: int, generation_id: int, context) -> Response:
        """Повторная отправка результата без генерации"""
        from .database import get_session, Generation
        from core.platform.telegram.media_sender import send_photo_robust
        
        session = get_session()
        try:
            gen = session.query(Generation).filter(
                Generation.id == generation_id,
                Generation.user_id == user_id
            ).first()
            
            if not gen:
                return Response(text="❌ Генерация не найдена", keyboard=kb.main_menu_keyboard())
            
            if not gen.image_url and not gen.file_id:
                return Response(text="❌ Результат не сохранён", keyboard=kb.main_menu_keyboard())
            
            # Отправляем результат повторно
            if context and context.bot:
                try:
                    photo = gen.file_id if gen.file_id else gen.image_url
                    await send_photo_robust(
                        context.bot,
                        chat_id=context.chat_id,
                        photo=photo,
                        caption="✅ Файл отправлен повторно",
                        reply_markup=None,
                    )
                    
                    return Response(
                        text="✅ Готово!",
                        keyboard=kb.generation_result_keyboard(generation_id),
                        action="edit"
                    )
                except Exception as e:
                    logger.error(f"Nano Banano resend error: {e}")
                    return Response(
                        text=f"❌ Ошибка отправки: {e}",
                        keyboard=kb.generation_result_keyboard(generation_id)
                    )
            
            return Response(text="❌ Ошибка контекста", keyboard=kb.main_menu_keyboard())
            
        finally:
            session.close()
    
    async def _usd_to_gton(self, usd: float) -> float:
        """Конвертировать USD в GTON"""
        from decimal import Decimal
        import math
        from core.payments.converter import currency_converter
        
        try:
            gton = await currency_converter.convert_to_gton(Decimal(str(usd)), "USD")
            return float(Decimal(str(math.ceil(float(gton) * 10000) / 10000)))
        except Exception:
            return usd
