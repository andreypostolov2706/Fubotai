"""
Veo Service — Главный класс сервиса
"""
from typing import Optional
from loguru import logger

from core.plugins.base_service import (
    BaseService,
    ServiceInfo,
    MenuItem,
    Response,
    MessageDTO,
    CallbackContext,
    MessageContext,
)

from .config import SERVICE_ID, SERVICE_NAME, SERVICE_ICON, DURATION_NAMES, ASPECT_RATIO_NAMES
from . import messages as msg
from . import keyboards as kb
from .handlers import GenerateHandler, ImageToVideoHandler, HistoryHandler, SettingsHandler
from .database import init_db, get_session, VideoGeneration


class VeoService(BaseService):
    """Сервис генерации видео Veo"""
    
    def __init__(self, core_api):
        super().__init__(core_api)
        self.core = core_api
        
        # Инициализируем обработчики
        self.generate_handler = GenerateHandler(self)
        self.image_to_video_handler = ImageToVideoHandler(self)
        self.history_handler = HistoryHandler(self)
        self.settings_handler = SettingsHandler(self)
    
    @property
    def info(self) -> ServiceInfo:
        return ServiceInfo(
            id=SERVICE_ID,
            name="Veo",
            description="Генерация видео с помощью Google Veo 2",
            version="1.0.0",
            author="FuBot Team",
            icon="🎬",
        )
    
    @property
    def features(self) -> dict:
        return {
            "subscriptions": False,
            "broadcasts": False,
            "partner_menu": False,
            "voice_messages": False,
        }
    
    @property
    def permissions(self) -> list:
        return [
            "balance:read",
            "balance:deduct",
            "balance:add",
            "notifications:send",
            "analytics:track",
        ]
    
    async def install(self) -> bool:
        """Установка сервиса"""
        try:
            init_db()
            logger.info("Veo: База данных инициализирована")
            return True
        except Exception as e:
            logger.error(f"Veo: Ошибка установки: {e}")
            return False
    
    async def uninstall(self) -> bool:
        """Удаление сервиса"""
        return True
    
    def get_user_menu_items(self, user_id: int, user_data=None) -> list[MenuItem]:
        """Пункты меню для пользователя"""
        return [
            MenuItem(
                text=f"{SERVICE_ICON} {SERVICE_NAME}",
                callback=f"service:{SERVICE_ID}:main",
                order=20,  # Второй после Nano Banano
            )
        ]
    
    def get_admin_menu_items(self) -> list[MenuItem]:
        """Пункты меню для админа"""
        return [
            MenuItem(
                text=f"{SERVICE_ICON} {SERVICE_NAME}",
                callback=f"service:{SERVICE_ID}:admin",
                order=20,
            )
        ]
    
    async def handle_callback(
        self,
        user_id: int,
        action: str,
        params: dict,
        context: CallbackContext,
    ) -> Response:
        """
        Обработка callback-запросов.
        Формат: service:veo:{action}:{params}
        """
        logger.debug(f"Veo: callback action={action}, params={params}")
        
        try:
            # Главное меню
            if action == "main":
                return await self._show_main_menu(user_id)
            
            # Генерация (Text-to-Video)
            elif action == "generate":
                result = await self.generate_handler.start_generation(user_id)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Image-to-Video
            elif action == "image_to_video":
                result = await self.image_to_video_handler.start(user_id)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Пропустить негативный промпт
            elif action == "skip_negative":
                state, state_data = await self.core.get_user_state(user_id)
                if state_data and state_data.get("mode") == "text_to_video":
                    result = await self.generate_handler.skip_negative(user_id, state_data)
                    return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Подтверждение генерации
            elif action == "confirm":
                sub_action = params.get("0") or params.get("id")
                state, state_data = await self.core.get_user_state(user_id)
                
                if sub_action == "create" and state_data:
                    if state_data.get("mode") == "image_to_video":
                        result = await self.image_to_video_handler.execute_generation(user_id, state_data, context)
                    else:
                        result = await self.generate_handler.execute_generation(user_id, state_data, context)
                    
                    # Если уже отправлено напрямую
                    if result.get("sent"):
                        return Response(text="", action="answer")
                    
                    if result.get("video_url"):
                        return Response(
                            text=result["text"],
                            keyboard=result["keyboard"],
                            media_type="video",
                            media_url=result["video_url"],
                            action="send",
                        )
                    return Response(text=result["text"], keyboard=result["keyboard"])
                
                elif sub_action == "edit":
                    mode = state_data.get("mode", "text_to_video") if state_data else "text_to_video"
                    return Response(
                        text=msg.EDIT_PARAMS_MENU,
                        keyboard=kb.edit_params_keyboard(mode),
                    )
            
            # Изменение параметров
            elif action == "edit_param":
                param = params.get("0") or params.get("id")
                state, state_data = await self.core.get_user_state(user_id)
                mode = state_data.get("mode", "text_to_video") if state_data else "text_to_video"
                
                if param == "prompt":
                    await self.core.set_user_state(user_id, "editing_prompt", state_data)
                    return Response(
                        text=msg.PROMPT_REQUEST if mode == "text_to_video" else msg.IMAGE_PROMPT_REQUEST,
                        keyboard=kb.cancel_keyboard(),
                    )
                elif param == "negative":
                    await self.core.set_user_state(user_id, "editing_negative", state_data)
                    return Response(
                        text=msg.NEGATIVE_PROMPT_REQUEST,
                        keyboard=kb.skip_negative_keyboard(),
                    )
                elif param == "duration":
                    result = await self.settings_handler.show_duration_selection(user_id)
                    return Response(text=result["text"], keyboard=result["keyboard"])
                elif param == "ratio":
                    result = await self.settings_handler.show_aspect_ratio_selection(user_id, mode)
                    return Response(text=result["text"], keyboard=result["keyboard"])
                elif param == "enhance":
                    result = await self.settings_handler.show_enhance_selection(user_id)
                    return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Вернуться к подтверждению
            elif action == "back_to_confirm":
                state, state_data = await self.core.get_user_state(user_id)
                if state_data:
                    if state_data.get("mode") == "image_to_video":
                        result = await self.image_to_video_handler._show_confirmation(user_id, state_data)
                    else:
                        result = await self.generate_handler._show_confirmation(user_id, state_data)
                    return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Настройки
            elif action == "settings":
                sub_action = params.get("0") or params.get("id")
                
                if sub_action == "duration":
                    result = await self.settings_handler.show_duration_selection(user_id)
                elif sub_action == "ratio":
                    result = await self.settings_handler.show_aspect_ratio_selection(user_id)
                elif sub_action == "enhance":
                    result = await self.settings_handler.show_enhance_selection(user_id)
                else:
                    result = await self.settings_handler.show_settings(user_id)
                
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Установка настроек
            elif action == "set":
                setting = params.get("0")
                value = params.get("1")
                
                if setting == "duration":
                    result = await self.settings_handler.set_duration(user_id, value)
                elif setting == "ratio":
                    result = await self.settings_handler.set_aspect_ratio(user_id, value)
                elif setting == "enhance":
                    result = await self.settings_handler.set_enhance(user_id, value)
                else:
                    result = await self.settings_handler.show_settings(user_id)
                
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
                    
                    if result.get("video_url") or result.get("file_id"):
                        return Response(
                            text=result["text"],
                            keyboard=result["keyboard"],
                            media_type="video",
                            media_url=result.get("video_url"),
                            media_file_id=result.get("file_id"),
                            action="send",
                        )
                elif sub_action == "delete":
                    gen_id = int(params.get("1", 0))
                    result = await self.history_handler.delete_generation(user_id, gen_id)
                else:
                    result = await self.history_handler.show_history(user_id)
                
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Повторная отправка результата (без генерации)
            elif action == "resend":
                gen_id = int(params.get("0") or params.get("id") or 0)
                return await self._resend_result(user_id, gen_id, context)
            
            # Публикация в галерею
            elif action == "publish":
                gen_id = int(params.get("0") or params.get("id") or 0)
                return await self._publish_to_gallery(user_id, gen_id, context)
            
            # Отмена
            elif action == "cancel":
                await self.core.clear_user_state(user_id)
                return await self._show_main_menu(user_id)
            
            # noop (для пагинации)
            elif action == "noop":
                return Response(text="", action="answer")
            
            # Неизвестное действие
            return Response(
                text="❌ Неизвестное действие",
                keyboard=kb.back_to_main_keyboard(),
            )
            
        except Exception as e:
            logger.error(f"Veo: Ошибка обработки callback: {e}")
            await self.core.clear_user_state(user_id)
            return Response(
                text=f"❌ Произошла ошибка: {e}",
                keyboard=kb.back_to_main_keyboard(),
            )
    
    async def handle_message(
        self,
        user_id: int,
        message: MessageDTO,
        context: MessageContext,
    ) -> Response:
        """Обработка текстовых сообщений"""
        try:
            state, state_data = await self.core.get_user_state(user_id)
            
            if not state:
                return await self._show_main_menu(user_id)
            
            # Ожидание промпта (Text-to-Video)
            if state == "waiting_prompt":
                if not message.text:
                    return Response(
                        text="❌ Пожалуйста, введите текстовое описание видео.",
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
                result = await self.generate_handler.handle_negative(user_id, message.text, state_data)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Ожидание изображения (Image-to-Video)
            elif state == "waiting_image":
                if not message.photo_file_id:
                    return Response(
                        text="❌ Пожалуйста, отправьте фотографию.",
                        keyboard=kb.cancel_keyboard(),
                    )
                
                # Загружаем изображение сразу через bot
                image_url = None
                if context and context.bot:
                    try:
                        file = await context.bot.get_file(message.photo_file_id)
                        image_data = bytes(await file.download_as_bytearray())
                        
                        # Загружаем на fal.ai
                        config = await self.core.get_service_config()
                        api_key = config.get("fal_api_key", "")
                        if api_key:
                            from .api import FalClient
                            client = FalClient(api_key)
                            image_url = await client.upload_image(image_data)
                    except Exception as e:
                        logger.error(f"Error uploading image: {e}")
                
                if not image_url:
                    return Response(
                        text="❌ Не удалось загрузить изображение. Попробуйте ещё раз.",
                        keyboard=kb.cancel_keyboard(),
                    )
                
                result = await self.image_to_video_handler.handle_image(user_id, image_url, state_data)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Ожидание промпта для Image-to-Video
            elif state == "waiting_image_prompt":
                if not message.text:
                    return Response(
                        text="❌ Пожалуйста, опишите как анимировать изображение.",
                        keyboard=kb.cancel_keyboard(),
                    )
                result = await self.image_to_video_handler.handle_prompt(user_id, message.text, state_data)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Редактирование промпта
            elif state == "editing_prompt":
                if not message.text:
                    return Response(
                        text="❌ Пожалуйста, введите новый промпт.",
                        keyboard=kb.cancel_keyboard(),
                    )
                state_data["prompt"] = message.text
                if state_data.get("mode") == "image_to_video":
                    result = await self.image_to_video_handler._show_confirmation(user_id, state_data)
                else:
                    result = await self.generate_handler._show_confirmation(user_id, state_data)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Редактирование негативного промпта
            elif state == "editing_negative":
                state_data["negative_prompt"] = message.text if message.text else None
                result = await self.generate_handler._show_confirmation(user_id, state_data)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Неизвестное состояние
            await self.core.clear_user_state(user_id)
            return await self._show_main_menu(user_id)
            
        except Exception as e:
            logger.error(f"Veo: Ошибка обработки сообщения: {e}")
            await self.core.clear_user_state(user_id)
            return Response(
                text=f"❌ Произошла ошибка: {e}",
                keyboard=kb.back_to_main_keyboard(),
            )
    
    # ==================== ПРИВАТНЫЕ МЕТОДЫ ====================
    
    async def _show_main_menu(self, user_id: int) -> Response:
        """Показать главное меню сервиса"""
        balance = await self.core.get_balance(user_id)
        
        # Ориентировочная стоимость (5 сек видео)
        config = await self.core.get_service_config()
        margin = config.get("margin_multiplier", 0.3)
        base_price = 2.50  # 5s video base price
        price_usd = base_price * (1 + margin)
        price_gton = await self._usd_to_gton(price_usd)
        
        text = msg.MAIN_MENU.format(
            balance=f"{balance:.4f}",
            price=f"{price_gton:.2f}"
        )
        
        return Response(
            text=text,
            keyboard=kb.main_menu_keyboard(),
        )
    
    async def _repeat_generation(self, user_id: int, generation_id: int) -> Response:
        """Повторить генерацию с теми же параметрами"""
        session = get_session()
        try:
            generation = session.query(VideoGeneration).filter(
                VideoGeneration.id == generation_id,
                VideoGeneration.user_id == user_id,
            ).first()
            
            if not generation:
                return Response(
                    text="❌ Генерация не найдена.",
                    keyboard=kb.back_to_main_keyboard(),
                )
            
            # Восстанавливаем параметры
            state_data = {
                "mode": generation.mode,
                "prompt": generation.prompt,
                "negative_prompt": generation.negative_prompt,
                "duration": generation.duration,
                "aspect_ratio": generation.aspect_ratio,
                "enhance_prompt": generation.enhance_prompt,
            }
            
            if generation.mode == "image_to_video" and generation.input_image_url:
                state_data["image_url"] = generation.input_image_url
                result = await self.image_to_video_handler._show_confirmation(user_id, state_data)
            else:
                result = await self.generate_handler._show_confirmation(user_id, state_data)
            
            return Response(text=result["text"], keyboard=result["keyboard"])
        finally:
            session.close()
    
    async def _publish_to_gallery(self, user_id: int, generation_id: int, context: CallbackContext) -> Response:
        """Опубликовать видео в галерею"""
        service_config = await self.core.get_service_config()
        gallery_channel_id = service_config.get("gallery_channel_id")
        
        if not gallery_channel_id:
            return Response(
                text="❌ Галерея не настроена.",
                action="answer",
                show_alert=True,
            )
        
        session = get_session()
        try:
            generation = session.query(VideoGeneration).filter(
                VideoGeneration.id == generation_id,
                VideoGeneration.user_id == user_id,
            ).first()
            
            if not generation or not generation.video_url:
                return Response(
                    text="❌ Видео не найдено.",
                    action="answer",
                    show_alert=True,
                )
            
            if generation.published_to_gallery:
                return Response(
                    text="ℹ️ Видео уже опубликовано.",
                    action="answer",
                    show_alert=True,
                )
            
            # Получаем username пользователя
            user = await self.core.get_user(user_id)
            username = user.telegram_username if user else "anonymous"
            
            # Формируем caption
            caption = msg.GALLERY_CAPTION.format(
                prompt=generation.prompt[:500],
                username=username,
            )
            
            # Отмечаем как опубликованное
            generation.published_to_gallery = True
            generation.published_at = datetime.utcnow()
            session.commit()
            
            return Response(
                text="✅ Видео опубликовано в галерею!",
                action="answer",
            )
        finally:
            session.close()
    
    async def _resend_result(self, user_id: int, generation_id: int, context) -> Response:
        """Повторная отправка результата без генерации"""
        from .database import get_session, Generation
        from core.platform.telegram.media_sender import send_video_robust
        
        session = get_session()
        try:
            gen = session.query(Generation).filter(
                Generation.id == generation_id,
                Generation.user_id == user_id
            ).first()
            
            if not gen:
                return Response(text="❌ Генерация не найдена", keyboard=kb.main_menu_keyboard())
            
            if not gen.video_url and not gen.file_id:
                return Response(text="❌ Результат не сохранён", keyboard=kb.main_menu_keyboard())
            
            if context and context.bot:
                try:
                    await send_video_robust(
                        context.bot,
                        chat_id=context.chat_id,
                        video_url=gen.video_url,
                        file_id=gen.file_id,
                        caption="✅ Файл отправлен повторно",
                        reply_markup=None,
                    )
                    
                    return Response(
                        text="✅ Готово!",
                        keyboard=kb.generation_result_keyboard(generation_id),
                        action="edit"
                    )
                except Exception as e:
                    logger.error(f"Veo resend error: {e}")
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


from datetime import datetime
