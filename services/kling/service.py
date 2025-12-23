"""
Kling Video v2.6 Service
Генерация видео с помощью Kling AI через fal.ai
"""
import math
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any

from loguru import logger

from core.plugins.base_service import (
    BaseService, ServiceInfo, MenuItem, Response,
    CallbackContext, MessageContext, MessageDTO
)
from core.plugins.core_api import CoreAPI
from core.platform.telegram.media_sender import send_video_robust

from .config import (
    SERVICE_ID,
    SERVICE_NAME,
    SERVICE_ICON,
    SERVICE_VERSION,
    SERVICE_DESCRIPTION,
    PROGRESS_FRAMES,
)
from .database import init_db, get_session, VideoGeneration
from .api import FalClient
from .handlers import GenerateHandler, EditHandler, HistoryHandler, SettingsHandler
from . import messages as msg
from . import keyboards as kb


class KlingService(BaseService):
    """Сервис генерации видео Kling Video v2.6"""
    
    def __init__(self, core_api: CoreAPI):
        super().__init__(core_api)
        self.generate_handler = GenerateHandler(self)
        self.edit_handler = EditHandler(self)
        self.history_handler = HistoryHandler(self)
        self.settings_handler = SettingsHandler(self)
    
    @property
    def info(self) -> ServiceInfo:
        return ServiceInfo(
            id=SERVICE_ID,
            name=SERVICE_NAME,
            description=SERVICE_DESCRIPTION,
            version=SERVICE_VERSION,
            author="FuBot Team",
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
            "voice_messages": False,
        }
    
    async def install(self) -> bool:
        """Установка сервиса"""
        try:
            init_db()
            logger.info("Kling: База данных инициализирована")
            return True
        except Exception as e:
            logger.error(f"Kling: Ошибка установки: {e}")
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
                order=25,  # После Veo (20)
            )
        ]
    
    def get_admin_menu_items(self) -> list[MenuItem]:
        """Пункты меню для админа"""
        return [
            MenuItem(
                text=f"{SERVICE_ICON} {SERVICE_NAME}",
                callback=f"service:{SERVICE_ID}:admin",
                order=25,
            )
        ]
    
    async def handle_callback(
        self,
        user_id: int,
        action: str,
        params: dict,
        context: CallbackContext,
    ) -> Response:
        """Обработка callback-запросов"""
        try:
            # Главное меню
            if action == "main":
                await self.core.clear_user_state(user_id)
                return await self._show_main_menu(user_id)
            
            # Отмена
            elif action == "cancel":
                await self.core.clear_user_state(user_id)
                return await self._show_main_menu(user_id)
            
            # Text-to-Video
            elif action == "generate":
                result = await self.generate_handler.start_generation(user_id)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Image-to-Video
            elif action == "edit":
                result = await self.edit_handler.start_edit(user_id)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Подтверждение генерации
            elif action == "confirm":
                mode = params.get("0", "generate")
                return await self._execute_generation(user_id, context, mode)
            
            # Изменение параметров
            elif action == "edit_params":
                mode = params.get("0", "generate")
                return Response(
                    text="⚙️ <b>Изменить параметры</b>\n\nВыберите параметр:",
                    keyboard=kb.edit_params_keyboard(mode)
                )
            
            elif action == "back_to_confirm":
                mode = params.get("0", "generate")
                state, state_data = await self.core.get_user_state(user_id)
                if state and state_data:
                    if mode == "edit":
                        result = await self.edit_handler.show_confirmation(user_id, state_data)
                    else:
                        result = await self.generate_handler.show_confirmation(user_id, state_data)
                    return Response(text=result["text"], keyboard=result["keyboard"])
                return Response(text=msg.MAIN_MENU, keyboard=kb.main_menu_keyboard())
            
            # Выбор параметра
            elif action == "set_param":
                param = params.get("0")
                mode = params.get("1", "generate")
                state, state_data = await self.core.get_user_state(user_id)
                state_data = state_data or {}
                
                if param == "duration":
                    return Response(
                        text=msg.SELECT_DURATION.format(current=msg.DURATION_NAMES.get(state_data.get("duration", "5"), "5 секунд")),
                        keyboard=kb.duration_keyboard(state_data.get("duration", "5"), mode)
                    )
                elif param == "aspect":
                    return Response(
                        text=msg.SELECT_ASPECT_RATIO.format(current=msg.ASPECT_RATIO_NAMES.get(state_data.get("aspect_ratio", "16:9"), "16:9")),
                        keyboard=kb.aspect_ratio_keyboard(state_data.get("aspect_ratio", "16:9"), mode)
                    )
                elif param == "audio":
                    return Response(
                        text=msg.SELECT_AUDIO.format(current=msg.AUDIO_NAMES.get(state_data.get("audio", "off"), "off")),
                        keyboard=kb.audio_keyboard(state_data.get("audio", "off"), mode)
                    )
            
            # Установка параметра при генерации
            elif action == "duration":
                value = params.get("0")
                mode = params.get("1", "generate")
                if mode == "edit":
                    result = await self.edit_handler.update_param(user_id, "duration", value)
                else:
                    result = await self.generate_handler.update_param(user_id, "duration", value)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            elif action == "aspect":
                value = params.get("0")
                mode = params.get("1", "generate")
                if mode == "edit":
                    result = await self.edit_handler.update_param(user_id, "aspect", value)
                else:
                    result = await self.generate_handler.update_param(user_id, "aspect", value)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            elif action == "audio":
                value = params.get("0")
                mode = params.get("1", "generate")
                if mode == "edit":
                    result = await self.edit_handler.update_param(user_id, "audio", value)
                else:
                    result = await self.generate_handler.update_param(user_id, "audio", value)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Настройки
            elif action == "settings":
                sub_action = params.get("0")
                
                if sub_action == "duration":
                    result = await self.settings_handler.show_duration_selection(user_id)
                elif sub_action == "aspect":
                    result = await self.settings_handler.show_aspect_selection(user_id)
                elif sub_action == "audio":
                    result = await self.settings_handler.show_audio_selection(user_id)
                else:
                    result = await self.settings_handler.show_settings(user_id)
                
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Установка настроек
            elif action == "set":
                setting = params.get("0")
                value = params.get("1")
                
                if setting == "duration":
                    result = await self.settings_handler.set_duration(user_id, value)
                elif setting == "aspect":
                    result = await self.settings_handler.set_aspect(user_id, value)
                elif setting == "audio":
                    result = await self.settings_handler.set_audio(user_id, value)
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
                else:
                    result = await self.history_handler.show_history(user_id)
                
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Повторная отправка результата (без генерации)
            elif action == "resend":
                gen_id = int(params.get("0", 0))
                return await self._resend_result(user_id, gen_id, context)
            
            # Удаление
            elif action == "delete":
                gen_id = int(params.get("0", 0))
                result = await self.history_handler.delete_generation(user_id, gen_id)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Публикация в галерею
            elif action == "publish":
                gen_id = int(params.get("0", 0))
                await self._publish_to_gallery(user_id, gen_id)
                return Response(text="✅ Опубликовано в галерею!", keyboard=kb.back_keyboard("main"))
            
            # По умолчанию
            return Response(text=msg.MAIN_MENU, keyboard=kb.main_menu_keyboard())
            
        except Exception as e:
            logger.error(f"Kling callback error: {e}")
            return Response(text=f"❌ Ошибка: {e}", keyboard=kb.main_menu_keyboard())
    
    async def handle_message(
        self,
        user_id: int,
        message: MessageDTO,
        context: MessageContext
    ) -> Response:
        """Обработка текстовых сообщений"""
        state, state_data = await self.core.get_user_state(user_id)
        
        if not state:
            return Response(text=msg.MAIN_MENU, keyboard=kb.main_menu_keyboard())
        
        try:
            # Ожидание промпта для Text-to-Video
            if state == "waiting_prompt":
                if not message.text:
                    return Response(text=msg.ERROR_NO_PROMPT, keyboard=kb.cancel_keyboard())
                result = await self.generate_handler.handle_prompt(user_id, message.text)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Ожидание изображения для Image-to-Video
            elif state == "waiting_image":
                if not message.photo_file_id:
                    return Response(text=msg.ERROR_NO_IMAGE, keyboard=kb.cancel_keyboard())
                
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
                            client = FalClient(api_key)
                            image_url = await client.upload_image(image_data)
                    except Exception as e:
                        logger.error(f"Error uploading image: {e}")
                
                if not image_url:
                    return Response(
                        text="❌ Не удалось загрузить изображение. Попробуйте ещё раз.",
                        keyboard=kb.cancel_keyboard(),
                    )
                
                result = await self.edit_handler.handle_image(user_id, image_url)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            # Ожидание промпта для Image-to-Video
            elif state == "waiting_edit_prompt":
                if not message.text:
                    return Response(text=msg.ERROR_NO_PROMPT, keyboard=kb.cancel_keyboard())
                result = await self.edit_handler.handle_prompt(user_id, message.text)
                return Response(text=result["text"], keyboard=result["keyboard"])
            
            return Response(text=msg.MAIN_MENU, keyboard=kb.main_menu_keyboard())
            
        except Exception as e:
            logger.error(f"Kling message error: {e}")
            return Response(text=f"❌ Ошибка: {e}", keyboard=kb.main_menu_keyboard())
    
    async def _execute_generation(
        self,
        user_id: int,
        context,
        mode: str = "generate"
    ) -> Response:
        """Выполнить генерацию видео"""
        state, state_data = await self.core.get_user_state(user_id)
        if not state or not state_data:
            return Response(text="❌ Данные генерации не найдены", keyboard=kb.main_menu_keyboard())
        
        # Рассчитываем стоимость
        duration = int(state_data["duration"])
        audio_enabled = state_data["audio"] == "on"
        
        cost_usd = FalClient.calculate_cost(duration, audio_enabled)
        
        config = await self.get_service_config()
        margin = config.get("margin_multiplier", 0.3)
        cost_usd_with_margin = cost_usd * (1 + margin)
        
        cost_gton = await self.usd_to_gton(cost_usd_with_margin)
        
        # Проверяем баланс
        balance = await self.core.get_balance(user_id)
        if balance < cost_gton:
            return Response(
                text=msg.ERROR_INSUFFICIENT_BALANCE.format(
                    required=f"{cost_gton:.4f}",
                    balance=f"{balance:.4f}"
                ),
                keyboard=kb.back_keyboard("main")
            )
        
        # Списываем средства
        await self.core.deduct_balance(user_id, cost_gton, f"Kling: {state_data['prompt'][:50]}")
        
        # Создаём запись в БД
        session = get_session()
        try:
            generation = VideoGeneration(
                user_id=user_id,
                mode=state_data.get("mode", "text_to_video"),
                prompt=state_data["prompt"],
                duration=duration,
                aspect_ratio=state_data.get("aspect_ratio", "16:9"),
                audio_enabled=audio_enabled,
                input_image_url=state_data.get("input_image_url"),
                cost_usd=cost_usd_with_margin,
                cost_gton=float(cost_gton),
                status="processing",
            )
            session.add(generation)
            session.commit()
            generation_id = generation.id
        finally:
            session.close()
        
        # Показываем "Генерирую..."
        if context and context.bot:
            try:
                await context.bot.edit_message_text(
                    chat_id=context.chat_id,
                    message_id=context.message_id,
                    text="🎬 <b>Генерирую видео...</b>\n\nЭто может занять 1-3 минуты.",
                    parse_mode="HTML"
                )
            except Exception:
                pass
        
        # Запускаем генерацию
        start_time = datetime.utcnow()
        
        try:
            api_key = config.get("fal_api_key", "")
            if not api_key:
                raise ValueError("API ключ fal.ai не настроен")
            
            client = FalClient(api_key)
            
            if state_data.get("mode") == "image_to_video":
                result = await client.image_to_video(
                    prompt=state_data["prompt"],
                    image_url=state_data["input_image_url"],
                    duration=duration,
                    aspect_ratio=state_data.get("aspect_ratio", "16:9"),
                    audio_enabled=audio_enabled,
                )
            else:
                result = await client.text_to_video(
                    prompt=state_data["prompt"],
                    duration=duration,
                    aspect_ratio=state_data.get("aspect_ratio", "16:9"),
                    audio_enabled=audio_enabled,
                )
            
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            if not result.get("success"):
                raise Exception(result.get("error", "Неизвестная ошибка"))
            
            video = result.get("video", {})
            video_url = video.get("url")
            
            if not video_url:
                raise Exception("Видео не получено")
            
            # Обновляем запись
            session = get_session()
            try:
                gen = session.query(VideoGeneration).filter(VideoGeneration.id == generation_id).first()
                if gen:
                    gen.video_url = video_url
                    gen.generation_time = generation_time
                    gen.status = "completed"
                    gen.completed_at = datetime.utcnow()
                    gen.fal_request_id = result.get("request_id")
                    session.commit()
            finally:
                session.close()
            
            await self.core.clear_user_state(user_id)
            
            audio_str = "🔊 Включено" if audio_enabled else "🔇 Выключено"
            
            text = msg.GENERATION_SUCCESS.format(
                prompt=state_data["prompt"][:200] + "..." if len(state_data["prompt"]) > 200 else state_data["prompt"],
                duration=duration,
                audio=audio_str,
                cost_gton=f"{cost_gton:.4f}",
                time=generation_time,
            )
            
            # Отправляем видео напрямую через bot (callback устаревает за время генерации)
            if context and context.bot:
                from core.platform.telegram.utils import build_keyboard
                try:
                    keyboard = build_keyboard(kb.result_keyboard(generation_id))
                    await send_video_robust(
                        context.bot,
                        chat_id=context.chat_id,
                        video=video_url,
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode="HTML",
                    )
                except Exception as e:
                    logger.error(f"Error sending video: {e}")
            
            return Response(text="", action="answer")
            
        except Exception as e:
            logger.error(f"Kling generation error: {e}")
            
            # Возвращаем средства
            await self.core.add_balance(user_id, cost_gton, f"Возврат: Kling ошибка")
            
            # Обновляем статус
            session = get_session()
            try:
                gen = session.query(VideoGeneration).filter(VideoGeneration.id == generation_id).first()
                if gen:
                    gen.status = "failed"
                    gen.error_message = str(e)
                    session.commit()
            finally:
                session.close()
            
            await self.core.clear_user_state(user_id)
            
            return Response(
                text=msg.GENERATION_ERROR.format(error=str(e)),
                keyboard=kb.main_menu_keyboard()
            )
    
    async def _publish_to_gallery(self, user_id: int, generation_id: int):
        """Публикация в галерею"""
        config = await self.get_service_config()
        gallery_channel = config.get("gallery_channel_id")
        
        if not gallery_channel or not config.get("gallery_enabled"):
            return
        
        session = get_session()
        try:
            gen = session.query(VideoGeneration).filter(
                VideoGeneration.id == generation_id,
                VideoGeneration.user_id == user_id
            ).first()
            
            if gen and gen.video_url and not gen.published_to_gallery:
                gen.published_to_gallery = True
                gen.published_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    async def _show_main_menu(self, user_id: int) -> Response:
        """Показать главное меню сервиса"""
        balance = await self.core.get_balance(user_id)
        
        # Ориентировочная стоимость (5 сек без аудио)
        config = await self.get_service_config()
        margin = config.get("margin_multiplier", 0.3)
        base_price = 0.35  # 5s no audio
        price_usd = base_price * (1 + margin)
        price_gton = await self.usd_to_gton(price_usd)
        
        text = msg.MAIN_MENU.format(
            balance=f"{balance:.4f}",
            price=f"{float(price_gton):.2f}"
        )
        
        return Response(
            text=text,
            keyboard=kb.main_menu_keyboard(),
        )
    
    async def get_service_config(self) -> dict:
        """Получить конфиг сервиса из БД"""
        from core.database import get_db
        from core.database.models import Service
        from sqlalchemy import select
        
        async with get_db() as session:
            result = await session.execute(
                select(Service).where(Service.id == SERVICE_ID)
            )
            service = result.scalar_one_or_none()
            
            if service and service.config:
                return service.config
        
        return {}
    
    async def usd_to_gton(self, usd: float) -> Decimal:
        """Конвертировать USD в GTON"""
        from core.payments.converter import currency_converter
        
        try:
            result = await currency_converter.convert_to_gton(Decimal(str(usd)), "USD")
            if result.success:
                return Decimal(str(math.ceil(float(result.gton_amount) * 10000) / 10000))
            return Decimal(str(usd))
        except Exception as e:
            logger.error(f"USD to GTON conversion error: {e}")
            return Decimal(str(usd))
    
    async def gton_to_fiat(self, gton: Decimal, currency: str = "RUB") -> float:
        """Конвертировать GTON в фиат"""
        from core.payments.converter import currency_converter
        
        try:
            fiat = await currency_converter.convert_from_gton(gton, currency)
            return float(fiat)
        except Exception as e:
            logger.error(f"GTON to fiat conversion error: {e}")
            return 0.0
    
    async def _resend_result(self, user_id: int, generation_id: int, context) -> Response:
        """Повторная отправка результата без генерации"""
        from .database import get_session, VideoGeneration
        from core.platform.telegram.media_sender import send_video_robust
        
        session = get_session()
        try:
            gen = session.query(VideoGeneration).filter(
                VideoGeneration.id == generation_id,
                VideoGeneration.user_id == user_id
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
                        keyboard=kb.result_keyboard(generation_id),
                        action="edit"
                    )
                except Exception as e:
                    logger.error(f"Kling resend error: {e}")
                    return Response(
                        text=f"❌ Ошибка отправки: {e}",
                        keyboard=kb.result_keyboard(generation_id)
                    )
            
            return Response(text="❌ Ошибка контекста", keyboard=kb.main_menu_keyboard())
            
        finally:
            session.close()
