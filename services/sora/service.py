"""
Sora 2 Service - OpenAI Video Generation
"""
from decimal import Decimal
from datetime import datetime
from loguru import logger
from sqlalchemy import select, desc

from core.plugins.base_service import BaseService, ServiceInfo, Response, MenuItem, UserServiceDTO, CallbackContext
from core.plugins.core_api import CoreAPI
from core.platform.telegram.media_sender import send_video_robust

from . import config
from . import messages as msg
from . import keyboards as kb
from .database import init_db, get_session, Generation
from .api import SoraAPI


class SoraService(BaseService):
    """Sora 2 Video Generation Service"""
    
    def __init__(self, core_api):
        super().__init__(core_api)
        self.core = core_api
        self._api: SoraAPI = None
    
    @property
    def info(self) -> ServiceInfo:
        return ServiceInfo(
            id=config.SERVICE_ID,
            name=config.SERVICE_NAME,
            version=config.SERVICE_VERSION,
            author=config.SERVICE_AUTHOR,
            description=config.SERVICE_DESCRIPTION,
            icon=config.SERVICE_ICON,
        )
    
    async def install(self) -> bool:
        """Install service"""
        try:
            await init_db()
            logger.info(f"Sora service installed")
            return True
        except Exception as e:
            logger.error(f"Sora install error: {e}")
            return False
    
    async def uninstall(self) -> bool:
        """Uninstall service"""
        return True
    
    def get_user_menu_items(self, user_id: int, user_data: UserServiceDTO) -> list[MenuItem]:
        """Get menu items for main menu"""
        return [
            MenuItem(
                text=f"{config.SERVICE_ICON} {config.SERVICE_NAME}",
                callback=f"service:{config.SERVICE_ID}:main",
                order=25,  # После Veo
            )
        ]
    
    def get_admin_menu_items(self, user_id: int) -> list[MenuItem]:
        """Get admin menu items"""
        return []
    
    async def _get_api(self) -> SoraAPI:
        """Get API client with current config"""
        service_config = await self.core.get_service_config()
        api_key = service_config.get("fal_api_key", "")
        if not api_key:
            raise ValueError("API key not configured")
        return SoraAPI(api_key)
    
    async def handle_callback(self, user_id: int, action: str, params: dict, context: CallbackContext) -> Response:
        """Handle callback queries"""
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
                await self.core.set_user_state(user_id, "waiting_prompt", {"mode": "text_to_video"})
                return Response(
                    text=msg.GENERATE_PROMPT,
                    keyboard=kb.cancel_keyboard(),
                )
            
            # Image-to-Video
            elif action == "image_to_video":
                await self.core.set_user_state(user_id, "waiting_image", {"mode": "image_to_video"})
                return Response(
                    text=msg.IMAGE_TO_VIDEO_PROMPT,
                    keyboard=kb.cancel_keyboard(),
                )
            
            # Подтверждение генерации
            elif action == "confirm":
                return await self._confirm_generation(user_id, context)
            
            # Изменение соотношения сторон
            elif action == "change_aspect":
                state, state_data = await self.core.get_user_state(user_id)
                current = state_data.get("aspect_ratio", "16:9")
                return Response(
                    text=msg.SELECT_ASPECT_RATIO,
                    keyboard=kb.aspect_ratio_keyboard(current),
                )
            
            elif action == "set_aspect":
                state, state_data = await self.core.get_user_state(user_id)
                value = params.get("0") or params.get("id") or "16:9"
                state_data["aspect_ratio"] = value
                await self.core.set_user_state(user_id, state, state_data)
                return await self._show_generation_settings(user_id, state_data)
            
            # Изменение длительности
            elif action == "change_duration":
                state, state_data = await self.core.get_user_state(user_id)
                current = state_data.get("duration", 4)
                return Response(
                    text=msg.SELECT_DURATION,
                    keyboard=kb.duration_keyboard(current),
                )
            
            elif action == "set_duration":
                state, state_data = await self.core.get_user_state(user_id)
                value = params.get("0") or params.get("id") or "4"
                state_data["duration"] = int(value)
                await self.core.set_user_state(user_id, state, state_data)
                return await self._show_generation_settings(user_id, state_data)
            
            elif action == "back_to_confirm":
                state, state_data = await self.core.get_user_state(user_id)
                return await self._show_generation_settings(user_id, state_data)
            
            # Настройки
            elif action == "settings":
                return await self._show_settings(user_id)
            
            elif action == "settings_aspect":
                settings = await self.core.get_user_service_settings(user_id)
                current = settings.get("aspect_ratio", "16:9")
                return Response(
                    text=msg.SELECT_ASPECT_RATIO,
                    keyboard=kb.settings_aspect_keyboard(current),
                )
            
            elif action == "save_aspect":
                value = params.get("0") or params.get("id") or "16:9"
                await self.core.update_user_service_settings(user_id, {"aspect_ratio": value})
                return await self._show_settings(user_id)
            
            elif action == "settings_duration":
                settings = await self.core.get_user_service_settings(user_id)
                current = settings.get("duration", 4)
                return Response(
                    text=msg.SELECT_DURATION,
                    keyboard=kb.settings_duration_keyboard(current),
                )
            
            elif action == "save_duration":
                value = params.get("0") or params.get("id") or "4"
                await self.core.update_user_service_settings(user_id, {"duration": int(value)})
                return await self._show_settings(user_id)
            
            # История
            elif action == "history":
                value = params.get("0") or params.get("id") or "0"
                page = int(value) if value else 0
                return await self._show_history(user_id, page)
            
            elif action == "view":
                value = params.get("0") or params.get("id") or "0"
                return await self._show_generation(user_id, int(value))
            
            elif action == "resend":
                value = params.get("0") or params.get("id") or "0"
                return await self._resend_result(user_id, int(value), context)
            
            # noop
            elif action == "noop":
                return Response(answer_callback=True)
            
            return Response(text="❌ Неизвестное действие", keyboard=kb.back_to_main_keyboard())
            
        except Exception as e:
            logger.error(f"Sora callback error: {e}")
            return Response(
                text=f"❌ Ошибка: {e}",
                keyboard=kb.back_to_main_keyboard(),
            )
    
    async def handle_message(self, user_id: int, message, context) -> Response:
        """Handle text/photo messages"""
        from core.plugins.base_service import MessageDTO, MessageContext
        
        # Поддержка старой и новой сигнатуры
        if isinstance(message, MessageDTO):
            text = message.text
            photo_file_id = message.photo_file_id
        else:
            text = message
            photo_file_id = None
        
        try:
            state, state_data = await self.core.get_user_state(user_id)
            
            if not state:
                return await self._show_main_menu(user_id)
            
            # Ожидание промпта (Text-to-Video)
            if state == "waiting_prompt":
                state_data["prompt"] = text
                settings = await self.core.get_user_service_settings(user_id)
                state_data["aspect_ratio"] = settings.get("aspect_ratio", "16:9")
                state_data["duration"] = settings.get("duration", 4)
                await self.core.set_user_state(user_id, "confirm_generation", state_data)
                return await self._show_generation_settings(user_id, state_data)
            
            # Ожидание изображения (Image-to-Video)
            elif state == "waiting_image":
                if not photo_file_id:
                    return Response(
                        text=msg.ERROR_INVALID_IMAGE,
                        keyboard=kb.cancel_keyboard(),
                    )
                
                # Загружаем изображение сразу через bot
                image_url = None
                if context and hasattr(context, 'bot') and context.bot:
                    try:
                        file = await context.bot.get_file(photo_file_id)
                        image_data = bytes(await file.download_as_bytearray())
                        api = await self._get_api()
                        image_url = await api.upload_image(image_data)
                    except Exception as e:
                        logger.error(f"Error uploading image: {e}")
                
                if not image_url:
                    return Response(
                        text="❌ Не удалось загрузить изображение. Попробуйте ещё раз.",
                        keyboard=kb.cancel_keyboard(),
                    )
                
                state_data["image_url"] = image_url
                await self.core.set_user_state(user_id, "waiting_image_prompt", state_data)
                return Response(
                    text=msg.IMAGE_TO_VIDEO_DESCRIBE,
                    keyboard=kb.cancel_keyboard(),
                )
            
            # Ожидание промпта для Image-to-Video
            elif state == "waiting_image_prompt":
                state_data["prompt"] = text
                settings = await self.core.get_user_service_settings(user_id)
                state_data["aspect_ratio"] = settings.get("aspect_ratio", "16:9")
                state_data["duration"] = settings.get("duration", 4)
                await self.core.set_user_state(user_id, "confirm_generation", state_data)
                return await self._show_generation_settings(user_id, state_data)
            
            # Неизвестное состояние
            await self.core.clear_user_state(user_id)
            return await self._show_main_menu(user_id)
            
        except Exception as e:
            logger.error(f"Sora message error: {e}")
            await self.core.clear_user_state(user_id)
            return Response(
                text=f"❌ Ошибка: {e}",
                keyboard=kb.back_to_main_keyboard(),
            )
    
    # ==================== ПРИВАТНЫЕ МЕТОДЫ ====================
    
    async def _show_main_menu(self, user_id: int) -> Response:
        """Показать главное меню сервиса"""
        balance = await self.core.get_balance(user_id)
        
        # Ориентировочная стоимость (4 сек)
        service_config = await self.core.get_service_config()
        margin = service_config.get("margin_multiplier", 0.3)
        base_price = 0.50  # 4s price
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
    
    async def _show_generation_settings(self, user_id: int, state_data: dict) -> Response:
        """Показать настройки генерации перед подтверждением"""
        prompt = state_data.get("prompt", "")
        aspect_ratio = state_data.get("aspect_ratio", "16:9")
        duration = state_data.get("duration", 4)
        
        cost = await self._calculate_cost(duration)
        
        text = msg.GENERATE_SETTINGS.format(
            prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt,
            aspect_ratio=aspect_ratio,
            duration=duration,
            cost=f"{cost:.4f}",
        )
        
        return Response(
            text=text,
            keyboard=kb.confirm_generation_keyboard(),
        )
    
    async def _confirm_generation(self, user_id: int, context=None) -> Response:
        """Подтвердить и запустить генерацию"""
        state, state_data = await self.core.get_user_state(user_id)
        
        prompt = state_data.get("prompt", "")
        aspect_ratio = state_data.get("aspect_ratio", "16:9")
        duration = state_data.get("duration", 4)
        mode = state_data.get("mode", "text_to_video")
        photo_file_id = state_data.get("photo_file_id")
        
        # Проверяем баланс
        cost = await self._calculate_cost(duration)
        balance = await self.core.get_balance(user_id)
        
        if balance < cost:
            return Response(
                text=msg.ERROR_NO_BALANCE.format(required=f"{cost:.4f}", balance=f"{balance:.4f}"),
                keyboard=kb.back_to_main_keyboard(),
            )
        
        # Проверяем API ключ
        try:
            api = await self._get_api()
        except ValueError:
            return Response(
                text=msg.ERROR_API_KEY,
                keyboard=kb.back_to_main_keyboard(),
            )
        
        # Показываем сообщение о генерации
        await self.core.clear_user_state(user_id)
        
        # Создаём запись в БД
        session = get_session()
        try:
            generation = Generation(
                user_id=user_id,
                generation_type=mode,
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                duration=duration,
                status="processing",
            )
            session.add(generation)
            await session.commit()
            await session.refresh(generation)
            generation_id = generation.id
        finally:
            await session.close()
        
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
        image_url = state_data.get("image_url")
        if mode == "image_to_video" and image_url:
            # Изображение уже загружено при получении
            result = await api.image_to_video(
                image_url=image_url,
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                duration=duration,
            )
        elif mode == "image_to_video":
            result = {"success": False, "error": "Image not uploaded"}
        else:
            result = await api.text_to_video(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                duration=duration,
            )
        
        # Обновляем запись
        session = get_session()
        try:
            gen = await session.get(Generation, generation_id)
            if result.get("success"):
                gen.video_url = result.get("video_url")
                gen.video_id = result.get("video_id")
                gen.thumbnail_url = result.get("thumbnail_url")
                gen.status = "completed"
                gen.completed_at = datetime.utcnow()
                
                # Рассчитываем стоимость
                service_config = await self.core.get_service_config()
                margin = service_config.get("margin_multiplier", 0.3)
                prices = service_config.get("prices", config.PRICES)
                base_price = prices.get(f"{duration}s", 0.50)
                cost_usd = base_price * (1 + margin)
                cost_gton = await self._usd_to_gton(cost_usd)
                
                gen.cost_usd = float(cost_usd)
                gen.cost_gton = float(cost_gton)
                
                # Списываем баланс
                await self.core.deduct_balance(user_id, Decimal(str(cost_gton)), f"Sora: {prompt[:50]}")
                
                await session.commit()
                
                # Отправляем видео напрямую через bot (callback устаревает за время генерации)
                text = msg.GENERATION_SUCCESS.format(
                    prompt=prompt[:100] + "..." if len(prompt) > 100 else prompt,
                    duration=duration,
                    cost=f"{cost_gton:.4f}",
                )
                
                if context and context.bot:
                    from core.platform.telegram.utils import build_keyboard
                    try:
                        keyboard = build_keyboard(kb.generation_result_keyboard(generation_id))
                        await send_video_robust(
                            context.bot,
                            chat_id=context.chat_id,
                            video=result.get("video_url"),
                            caption=text,
                            reply_markup=keyboard,
                            parse_mode="HTML",
                        )
                    except Exception as e:
                        logger.error(f"Error sending video: {e}")
                
                return Response(text="", action="answer")
            else:
                gen.status = "failed"
                gen.error_message = result.get("error", "Unknown error")
                await session.commit()
                
                return Response(
                    text=msg.GENERATION_ERROR.format(error=result.get("error", "Unknown error")),
                    keyboard=kb.back_to_main_keyboard(),
                )
        finally:
            await session.close()
    
    async def _show_settings(self, user_id: int) -> Response:
        """Показать настройки"""
        settings = await self.core.get_user_service_settings(user_id)
        aspect_ratio = settings.get("aspect_ratio", "16:9")
        duration = settings.get("duration", 4)
        
        text = msg.SETTINGS_MENU.format(
            aspect_ratio=aspect_ratio,
            duration=duration,
        )
        
        return Response(
            text=text,
            keyboard=kb.settings_keyboard(),
        )
    
    async def _show_history(self, user_id: int, page: int = 0) -> Response:
        """Показать историю генераций"""
        session = get_session()
        try:
            result = await session.execute(
                select(Generation)
                .where(Generation.user_id == user_id)
                .order_by(desc(Generation.created_at))
            )
            generations = result.scalars().all()
            
            if not generations:
                return Response(
                    text=msg.HISTORY_EMPTY,
                    keyboard=kb.back_to_main_keyboard(),
                )
            
            gen_list = [
                {"id": g.id, "prompt": g.prompt, "status": g.status}
                for g in generations
            ]
            
            return Response(
                text="📂 <b>История генераций</b>\n\nВыберите генерацию:",
                keyboard=kb.history_keyboard(gen_list, page),
            )
        finally:
            await session.close()
    
    async def _show_generation(self, user_id: int, generation_id: int) -> Response:
        """Показать конкретную генерацию"""
        session = get_session()
        try:
            gen = await session.get(Generation, generation_id)
            if not gen or gen.user_id != user_id:
                return Response(
                    text="❌ Генерация не найдена",
                    keyboard=kb.back_to_main_keyboard(),
                )
            
            text = msg.HISTORY_ITEM.format(
                id=gen.id,
                prompt=gen.prompt[:100] + "..." if len(gen.prompt) > 100 else gen.prompt,
                date=gen.created_at.strftime("%d.%m.%Y %H:%M"),
                duration=gen.duration,
                cost=f"{gen.cost_gton:.4f}",
            )
            
            if gen.video_url:
                return Response(
                    text=text,
                    keyboard=kb.generation_result_keyboard(gen.id),
                    video_url=gen.video_url,
                )
            else:
                return Response(
                    text=text,
                    keyboard=kb.back_to_main_keyboard(),
                )
        finally:
            await session.close()
    
    async def _retry_generation(self, user_id: int, generation_id: int) -> Response:
        """Повторить генерацию"""
        session = get_session()
        try:
            gen = await session.get(Generation, generation_id)
            if not gen or gen.user_id != user_id:
                return Response(
                    text="❌ Генерация не найдена",
                    keyboard=kb.back_to_main_keyboard(),
                )
            
            # Устанавливаем состояние с данными из предыдущей генерации
            state_data = {
                "mode": gen.generation_type,
                "prompt": gen.prompt,
                "aspect_ratio": gen.aspect_ratio,
                "duration": gen.duration,
            }
            await self.core.set_user_state(user_id, "confirm_generation", state_data)
            return await self._show_generation_settings(user_id, state_data)
        finally:
            await session.close()
    
    async def _calculate_cost(self, duration: int) -> Decimal:
        """Рассчитать стоимость генерации"""
        service_config = await self.core.get_service_config()
        margin = Decimal(str(service_config.get("margin_multiplier", 0.3)))
        prices = service_config.get("prices", config.PRICES)
        
        base_price = Decimal(str(prices.get(f"{duration}s", 0.50)))
        price_usd = base_price * (1 + margin)
        
        return await self._usd_to_gton(float(price_usd))
    
    async def _usd_to_gton(self, usd: float) -> Decimal:
        """Конвертировать USD в GTON"""
        from core.payments.converter import currency_converter
        result = await currency_converter.convert_to_gton(Decimal(str(usd)), "USD")
        if result.success:
            return result.gton_amount
        return Decimal("0")
    
    async def _resend_result(self, user_id: int, generation_id: int, context) -> Response:
        """Повторная отправка результата без генерации"""
        from .database import get_session, VideoGeneration
        from core.platform.telegram.media_sender import send_video_robust
        
        session = await get_session()
        try:
            gen = await session.get(VideoGeneration, generation_id)
            
            if not gen or gen.user_id != user_id:
                return Response(text="❌ Генерация не найдена", keyboard=kb.back_to_main_keyboard())
            
            if not gen.video_url and not gen.file_id:
                return Response(text="❌ Результат не сохранён", keyboard=kb.back_to_main_keyboard())
            
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
                    logger.error(f"Sora resend error: {e}")
                    return Response(
                        text=f"❌ Ошибка отправки: {e}",
                        keyboard=kb.generation_result_keyboard(generation_id)
                    )
            
            return Response(text="❌ Ошибка контекста", keyboard=kb.back_to_main_keyboard())
            
        finally:
            await session.close()
