"""
FLUX 2 Flex Service - Text to Image Generation
"""
from decimal import Decimal
from datetime import datetime
from loguru import logger

from core.plugins.base_service import BaseService, ServiceInfo, MenuItem, Response, CallbackContext, MessageContext, MessageDTO, UserServiceDTO
from core.plugins.core_api import CoreAPI
from core.platform.telegram.media_sender import send_photo_robust

from . import config
from . import messages as msg
from . import keyboards as kb
from .database import init_db, get_session, Generation
from .api import Flux2FlexAPI


class Flux2FlexService(BaseService):
    """FLUX 2 Flex Image Generation Service"""
    
    def __init__(self, core_api):
        super().__init__(core_api)
        self.core = core_api
        self._api: Flux2FlexAPI = None
    
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
            init_db()
            logger.info(f"FLUX 2 Flex service installed")
            return True
        except Exception as e:
            logger.error(f"FLUX 2 Flex install error: {e}")
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
                order=15,  # После Nano Banano, перед Veo
            )
        ]
    
    def get_admin_menu_items(self, user_id: int) -> list[MenuItem]:
        """Get admin menu items"""
        return []
    
    async def _get_api(self) -> Flux2FlexAPI:
        """Get API client with current config"""
        service_config = await self.core.get_service_config()
        api_key = service_config.get("fal_api_key", "")
        if not api_key:
            raise ValueError("API key not configured")
        return Flux2FlexAPI(api_key)
    
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
            
            # Генерация
            elif action == "generate":
                await self.core.set_user_state(user_id, "waiting_prompt", {})
                return Response(
                    text=msg.GENERATE_PROMPT,
                    keyboard=kb.cancel_keyboard(),
                )
            
            # Подтверждение генерации
            elif action == "confirm":
                return await self._confirm_generation(user_id, context)
            
            # Изменение размера
            elif action == "change_size":
                state, state_data = await self.core.get_user_state(user_id)
                current = state_data.get("image_size", "square")
                return Response(
                    text=msg.SELECT_SIZE.format(current=config.IMAGE_SIZES.get(current, current)),
                    keyboard=kb.size_keyboard(current),
                )
            
            elif action == "set_size":
                state, state_data = await self.core.get_user_state(user_id)
                value = params.get("0") or params.get("id") or "square"
                state_data["image_size"] = value
                await self.core.set_user_state(user_id, state, state_data)
                return await self._show_generation_settings(user_id, state_data)
            
            # Изменение формата
            elif action == "change_format":
                state, state_data = await self.core.get_user_state(user_id)
                current = state_data.get("output_format", "jpeg")
                return Response(
                    text=msg.SELECT_FORMAT.format(current=config.OUTPUT_FORMATS.get(current, current)),
                    keyboard=kb.format_keyboard(current),
                )
            
            elif action == "set_format":
                state, state_data = await self.core.get_user_state(user_id)
                value = params.get("0") or params.get("id") or "jpeg"
                state_data["output_format"] = value
                await self.core.set_user_state(user_id, state, state_data)
                return await self._show_generation_settings(user_id, state_data)
            
            elif action == "back_to_confirm":
                state, state_data = await self.core.get_user_state(user_id)
                return await self._show_generation_settings(user_id, state_data)
            
            # Настройки
            elif action == "settings":
                return await self._show_settings(user_id)
            
            elif action == "settings_size":
                settings = await self.core.get_user_service_settings(user_id)
                current = settings.get("image_size", "square")
                return Response(
                    text=msg.SELECT_SIZE.format(current=config.IMAGE_SIZES.get(current, current)),
                    keyboard=kb.settings_size_keyboard(current),
                )
            
            elif action == "save_size":
                value = params.get("0") or params.get("id") or "square"
                await self.core.update_user_service_settings(user_id, {"image_size": value})
                return await self._show_settings(user_id)
            
            elif action == "settings_format":
                settings = await self.core.get_user_service_settings(user_id)
                current = settings.get("output_format", "jpeg")
                return Response(
                    text=msg.SELECT_FORMAT.format(current=config.OUTPUT_FORMATS.get(current, current)),
                    keyboard=kb.settings_format_keyboard(current),
                )
            
            elif action == "save_format":
                value = params.get("0") or params.get("id") or "jpeg"
                await self.core.update_user_service_settings(user_id, {"output_format": value})
                return await self._show_settings(user_id)
            
            elif action == "settings_steps":
                settings = await self.core.get_user_service_settings(user_id)
                current = settings.get("num_inference_steps", 28)
                return Response(
                    text=msg.SELECT_STEPS.format(current=current),
                    keyboard=kb.settings_steps_keyboard(current),
                )
            
            elif action == "save_steps":
                value = params.get("0") or params.get("id") or "28"
                await self.core.update_user_service_settings(user_id, {"num_inference_steps": int(value)})
                return await self._show_settings(user_id)
            
            # История
            elif action == "history":
                value = params.get("0") or params.get("id") or "0"
                page = int(value) if value else 0
                return await self._show_history(user_id, page)
            
            elif action == "view":
                value = params.get("0") or params.get("id") or "0"
                return await self._show_generation(user_id, int(value))
            
            # noop
            elif action == "noop":
                return Response(text="", action="answer")
            
            return Response(text="❌ Неизвестное действие", keyboard=kb.back_to_main_keyboard())
            
        except Exception as e:
            logger.error(f"FLUX 2 Flex callback error: {e}")
            return Response(
                text=f"❌ Ошибка: {str(e)}",
                keyboard=kb.back_to_main_keyboard(),
            )
    
    async def handle_message(self, user_id: int, message, context) -> Response:
        """Handle text messages"""
        try:
            state, state_data = await self.core.get_user_state(user_id)
            
            if state == "waiting_prompt":
                prompt = message.text.strip() if hasattr(message, 'text') and message.text else ""
                
                if not prompt:
                    return Response(
                        text="❌ Отправьте текстовое описание изображения.",
                        keyboard=kb.cancel_keyboard(),
                    )
                
                if len(prompt) > config.MAX_PROMPT_LENGTH:
                    return Response(
                        text=f"❌ Промпт слишком длинный. Максимум {config.MAX_PROMPT_LENGTH} символов.",
                        keyboard=kb.cancel_keyboard(),
                    )
                
                # Получаем настройки пользователя
                settings = await self.core.get_user_service_settings(user_id)
                
                state_data = {
                    "prompt": prompt,
                    "image_size": settings.get("image_size", "square"),
                    "output_format": settings.get("output_format", "jpeg"),
                    "num_inference_steps": settings.get("num_inference_steps", 28),
                    "guidance_scale": settings.get("guidance_scale", 3.5),
                }
                
                await self.core.set_user_state(user_id, "confirm_generation", state_data)
                return await self._show_generation_settings(user_id, state_data)
            
            return Response(text="")
            
        except Exception as e:
            logger.error(f"FLUX 2 Flex message error: {e}")
            return Response(text=f"❌ Ошибка: {str(e)}")
    
    async def _show_main_menu(self, user_id: int) -> Response:
        """Show main menu"""
        balance = await self.core.get_balance(user_id)
        balance_rub = await self._gton_to_rub(balance)
        
        # Получаем минимальную цену
        service_config = await self.core.get_service_config()
        margin = service_config.get("margin_multiplier", 0.3)
        prices = service_config.get("prices", config.PRICES)
        min_price_usd = min(prices.values())
        min_price_with_margin = min_price_usd * (1 + margin)
        min_price_rub = await self._usd_to_rub(Decimal(str(min_price_with_margin)))
        
        return Response(
            text=msg.MAIN_MENU.format(
                price=f"{min_price_rub:.2f}",
                balance=f"{balance_rub:.2f}",
            ),
            keyboard=kb.main_menu_keyboard(),
        )
    
    async def _show_generation_settings(self, user_id: int, state_data: dict) -> Response:
        """Show generation confirmation screen"""
        prompt = state_data.get("prompt", "")
        image_size = state_data.get("image_size", "square")
        output_format = state_data.get("output_format", "jpeg")
        num_steps = state_data.get("num_inference_steps", 28)
        
        # Рассчитываем стоимость
        cost_rub = await self._calculate_cost_rub(image_size)
        
        return Response(
            text=msg.CONFIRM_GENERATION.format(
                prompt=prompt[:500] + "..." if len(prompt) > 500 else prompt,
                size=config.IMAGE_SIZES.get(image_size, image_size),
                format=config.OUTPUT_FORMATS.get(output_format, output_format),
                steps=num_steps,
                cost=f"{cost_rub:.2f}",
            ),
            keyboard=kb.confirm_keyboard(),
        )
    
    async def _confirm_generation(self, user_id: int, context: CallbackContext) -> Response:
        """Execute generation"""
        state, state_data = await self.core.get_user_state(user_id)
        
        if not state_data or "prompt" not in state_data:
            return await self._show_main_menu(user_id)
        
        prompt = state_data.get("prompt")
        image_size = state_data.get("image_size", "square")
        output_format = state_data.get("output_format", "jpeg")
        num_steps = state_data.get("num_inference_steps", 28)
        guidance_scale = state_data.get("guidance_scale", 3.5)
        
        # Проверяем баланс
        balance = await self.core.get_balance(user_id)
        cost_gton = await self._calculate_cost_gton(image_size)
        
        if balance < cost_gton:
            balance_rub = await self._gton_to_rub(balance)
            cost_rub = await self._gton_to_rub(cost_gton)
            return Response(
                text=msg.INSUFFICIENT_BALANCE.format(
                    required=f"{cost_rub:.2f}",
                    balance=f"{balance_rub:.2f}",
                ),
                keyboard=kb.back_to_main_keyboard(),
            )
        
        # Проверяем API ключ
        try:
            api = await self._get_api()
        except ValueError:
            return Response(
                text=msg.API_KEY_NOT_CONFIGURED,
                keyboard=kb.back_to_main_keyboard(),
            )
        
        # Создаём запись в БД
        session = get_session()
        generation = Generation(
            user_id=user_id,
            prompt=prompt,
            image_size=image_size,
            output_format=output_format,
            num_inference_steps=num_steps,
            guidance_scale=guidance_scale,
            cost_usd=float(await self._calculate_cost_usd(image_size)),
            cost_gton=float(cost_gton),
            status="pending",
        )
        session.add(generation)
        session.commit()
        generation_id = generation.id
        session.close()
        
        # Списываем баланс
        await self.core.deduct_balance(user_id, cost_gton, f"FLUX 2 Flex generation #{generation_id}")
        
        # Показываем "Генерирую..."
        if context.bot:
            try:
                await context.bot.edit_message_text(
                    chat_id=context.chat_id,
                    message_id=context.message_id,
                    text="✨ <b>Генерирую изображение...</b>\n\nЭто может занять 10-30 секунд.",
                    parse_mode="HTML"
                )
            except Exception:
                pass
        
        # Очищаем состояние
        await self.core.clear_user_state(user_id)
        
        # Запускаем генерацию
        result = await api.generate(
            prompt=prompt,
            image_size=image_size,
            output_format=output_format,
            num_inference_steps=num_steps,
            guidance_scale=guidance_scale,
        )
        
        # Обновляем запись
        session = get_session()
        gen = session.query(Generation).filter(Generation.id == generation_id).first()
        
        if result.success:
            gen.status = "completed"
            gen.image_url = result.image_url
            gen.seed = result.seed
            gen.generation_time = result.generation_time
            gen.completed_at = datetime.utcnow()
            session.commit()
            session.close()
            
            cost_rub = await self._gton_to_rub(cost_gton)
            
            text = msg.GENERATION_SUCCESS.format(
                prompt=prompt[:300] + "..." if len(prompt) > 300 else prompt,
                size=config.IMAGE_SIZES.get(image_size, image_size),
                time=f"{result.generation_time:.1f}" if result.generation_time else "?",
                cost=f"{cost_rub:.2f}",
            )
            
            # Отправляем фото напрямую через bot (callback устаревает за время генерации)
            if context and context.bot:
                from core.platform.telegram.utils import build_keyboard
                try:
                    keyboard = build_keyboard(kb.back_to_main_keyboard())
                    await send_photo_robust(
                        context.bot,
                        chat_id=context.chat_id,
                        photo=result.image_url,
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode="HTML",
                    )
                except Exception as e:
                    logger.error(f"Error sending photo: {e}")
            
            return Response(text="", action="answer")
        else:
            gen.status = "failed"
            gen.error_message = result.error
            session.commit()
            session.close()
            
            # Возвращаем баланс
            await self.core.add_balance(user_id, cost_gton, f"Refund FLUX 2 Flex #{generation_id}")
            
            return Response(
                text=msg.GENERATION_ERROR.format(error=result.error),
                keyboard=kb.back_to_main_keyboard(),
            )
    
    async def _show_settings(self, user_id: int) -> Response:
        """Show settings menu"""
        settings = await self.core.get_user_service_settings(user_id)
        
        image_size = settings.get("image_size", "square")
        output_format = settings.get("output_format", "jpeg")
        num_steps = settings.get("num_inference_steps", 28)
        expansion = settings.get("enable_prompt_expansion", True)
        
        return Response(
            text=msg.SETTINGS_MENU.format(
                size=config.IMAGE_SIZES.get(image_size, image_size),
                format=config.OUTPUT_FORMATS.get(output_format, output_format),
                steps=num_steps,
                expansion="✅ Вкл" if expansion else "❌ Выкл",
            ),
            keyboard=kb.settings_keyboard(),
        )
    
    async def _show_history(self, user_id: int, page: int = 0) -> Response:
        """Show generation history"""
        session = get_session()
        
        per_page = 5
        total = session.query(Generation).filter(
            Generation.user_id == user_id,
            Generation.status == "completed"
        ).count()
        
        if total == 0:
            session.close()
            return Response(
                text=msg.HISTORY_EMPTY,
                keyboard=kb.back_to_main_keyboard(),
            )
        
        total_pages = (total + per_page - 1) // per_page
        page = max(0, min(page, total_pages - 1))
        
        generations = session.query(Generation).filter(
            Generation.user_id == user_id,
            Generation.status == "completed"
        ).order_by(desc(Generation.created_at)).offset(page * per_page).limit(per_page).all()
        
        session.close()
        
        text = msg.HISTORY_HEADER.format(page=page + 1, total=total_pages) + "\n\n"
        
        for gen in generations:
            cost_rub = await self._gton_to_rub(Decimal(str(gen.cost_gton)))
            text += f"• #{gen.id}: {gen.prompt[:50]}... — {cost_rub:.2f} ₽\n"
        
        return Response(
            text=text,
            keyboard=kb.history_keyboard(page, total_pages),
        )
    
    async def _show_generation(self, user_id: int, generation_id: int) -> Response:
        """Show single generation"""
        session = get_session()
        gen = session.query(Generation).filter(
            Generation.id == generation_id,
            Generation.user_id == user_id
        ).first()
        session.close()
        
        if not gen:
            return Response(
                text="❌ Генерация не найдена",
                keyboard=kb.back_to_main_keyboard(),
            )
        
        cost_rub = await self._gton_to_rub(Decimal(str(gen.cost_gton)))
        
        return Response(
            text=msg.HISTORY_ITEM.format(
                id=gen.id,
                prompt=gen.prompt,
                size=config.IMAGE_SIZES.get(gen.image_size, gen.image_size),
                date=gen.created_at.strftime("%d.%m.%Y %H:%M"),
                cost=f"{cost_rub:.2f}",
            ),
            keyboard=kb.back_to_main_keyboard(),
            media_type="photo" if gen.image_url else None,
            media_url=gen.image_url,
        )
    
    async def _calculate_cost_usd(self, image_size: str) -> Decimal:
        """Calculate cost in USD"""
        service_config = await self.core.get_service_config()
        prices = service_config.get("prices", config.PRICES)
        margin = service_config.get("margin_multiplier", 0.3)
        
        base_price = prices.get(image_size, 0.06)
        return Decimal(str(base_price)) * (1 + Decimal(str(margin)))
    
    async def _calculate_cost_gton(self, image_size: str) -> Decimal:
        """Calculate cost in GTON"""
        cost_usd = await self._calculate_cost_usd(image_size)
        return await self._usd_to_gton(cost_usd)
    
    async def _calculate_cost_rub(self, image_size: str) -> Decimal:
        """Calculate cost in RUB"""
        cost_usd = await self._calculate_cost_usd(image_size)
        return await self._usd_to_rub(cost_usd)
    
    async def _usd_to_gton(self, usd: Decimal) -> Decimal:
        """Convert USD to GTON"""
        from core.payments.converter import currency_converter
        result = await currency_converter.convert_to_gton(usd, "USD")
        return result.gton_amount if result.success else Decimal("0")
    
    async def _usd_to_rub(self, usd: Decimal) -> Decimal:
        """Convert USD to RUB"""
        from core.database import get_db
        from core.database.models import ExchangeRate
        from sqlalchemy import select
        
        async with get_db() as session:
            result = await session.execute(
                select(ExchangeRate).where(
                    ExchangeRate.base_currency == "USD",
                    ExchangeRate.quote_currency == "RUB"
                )
            )
            rate = result.scalar_one_or_none()
            if rate:
                return usd * Decimal(str(rate.rate))
        return usd * Decimal("100")  # fallback
    
    async def _gton_to_rub(self, gton: Decimal) -> Decimal:
        """Convert GTON to RUB"""
        from core.database import get_db
        from core.database.models import Setting
        from sqlalchemy import select
        
        async with get_db() as session:
            result = await session.execute(
                select(Setting).where(Setting.key == "gton_rub_rate")
            )
            setting = result.scalar_one_or_none()
            if setting:
                return gton * Decimal(str(setting.value))
        return gton * Decimal("100")  # fallback
