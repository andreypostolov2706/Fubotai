"""
Veo Service — Generate Handler (Text-to-Video)
"""
from typing import TYPE_CHECKING
from datetime import datetime
from decimal import Decimal, ROUND_UP

from loguru import logger

from ..config import PRICES, DEFAULT_MARGIN, DEFAULT_USER_SETTINGS, DURATION_NAMES, ASPECT_RATIO_NAMES
from .. import messages as msg
from .. import keyboards as kb
from ..database import get_session, VideoGeneration
from ..api import FalClient
from core.platform.telegram.media_sender import send_video_robust

if TYPE_CHECKING:
    from ..service import VeoService


class GenerateHandler:
    """Обработчик генерации видео (Text-to-Video)"""
    
    def __init__(self, service: "VeoService"):
        self.service = service
        self.core = service.core
    
    async def start_generation(self, user_id: int) -> dict:
        """Начать процесс генерации"""
        await self.core.set_user_state(user_id, "waiting_prompt", {"mode": "text_to_video"})
        
        return {
            "text": msg.PROMPT_REQUEST,
            "keyboard": kb.cancel_keyboard(),
        }
    
    async def handle_prompt(self, user_id: int, prompt: str, state_data: dict) -> dict:
        """Обработать введённый промпт"""
        state_data["prompt"] = prompt
        await self.core.set_user_state(user_id, "waiting_negative", state_data)
        
        return {
            "text": msg.NEGATIVE_PROMPT_REQUEST,
            "keyboard": kb.skip_negative_keyboard(),
        }
    
    async def handle_negative(self, user_id: int, negative_prompt: str, state_data: dict) -> dict:
        """Обработать негативный промпт"""
        state_data["negative_prompt"] = negative_prompt
        return await self._show_confirmation(user_id, state_data)
    
    async def skip_negative(self, user_id: int, state_data: dict) -> dict:
        """Пропустить негативный промпт"""
        state_data["negative_prompt"] = None
        return await self._show_confirmation(user_id, state_data)
    
    async def _show_confirmation(self, user_id: int, state_data: dict) -> dict:
        """Показать экран подтверждения"""
        settings = await self._get_settings(user_id)
        
        # Применяем настройки к state_data
        state_data["duration"] = state_data.get("duration", settings["duration"])
        state_data["aspect_ratio"] = state_data.get("aspect_ratio", settings["aspect_ratio"])
        state_data["enhance_prompt"] = state_data.get("enhance_prompt", settings["enhance_prompt"])
        
        await self.core.set_user_state(user_id, "confirming", state_data)
        
        # Рассчитываем стоимость
        cost_gton = await self._calculate_cost(state_data["duration"])
        state_data["cost_gton"] = float(cost_gton)
        
        # Формируем текст
        negative_section = ""
        if state_data.get("negative_prompt"):
            negative_section = msg.NEGATIVE_SECTION.format(
                negative_prompt=state_data["negative_prompt"]
            )
        
        text = msg.CONFIRM_GENERATION.format(
            prompt=state_data["prompt"],
            negative_section=negative_section,
            duration=DURATION_NAMES.get(state_data["duration"], state_data["duration"]),
            aspect_ratio=ASPECT_RATIO_NAMES.get(state_data["aspect_ratio"], state_data["aspect_ratio"]),
            enhance="Да" if state_data["enhance_prompt"] else "Нет",
            cost=f"{cost_gton:.4f}",
        )
        
        return {
            "text": text,
            "keyboard": kb.confirm_generation_keyboard(),
        }
    
    async def execute_generation(self, user_id: int, state_data: dict, context) -> dict:
        """Выполнить генерацию видео"""
        # Проверяем баланс
        balance = await self.core.get_balance(user_id)
        cost_gton = await self._calculate_cost(state_data["duration"])
        
        if balance < cost_gton:
            return {
                "text": msg.INSUFFICIENT_BALANCE.format(
                    balance=f"{balance:.4f}",
                    required=f"{cost_gton:.4f}",
                ),
                "keyboard": kb.insufficient_balance_keyboard(),
            }
        
        # Списываем средства
        await self.core.deduct_balance(
            user_id,
            float(cost_gton),
            description=f"Veo: генерация видео {state_data['duration']}"
        )
        
        # Создаём запись в БД
        session = get_session()
        try:
            generation = VideoGeneration(
                user_id=user_id,
                mode="text_to_video",
                prompt=state_data["prompt"],
                negative_prompt=state_data.get("negative_prompt"),
                duration=state_data["duration"],
                aspect_ratio=state_data["aspect_ratio"],
                enhance_prompt=state_data.get("enhance_prompt", True),
                cost_usd=PRICES.get(state_data["duration"], 2.50),
                cost_gton=float(cost_gton),
                status="processing",
            )
            session.add(generation)
            session.commit()
            generation_id = generation.id
        finally:
            session.close()
        
        # Получаем API ключ из конфига сервиса
        service_config = await self.core.get_service_config()
        api_key = service_config.get("fal_api_key", "")
        
        if not api_key:
            # Возвращаем средства
            await self.core.add_balance(user_id, float(cost_gton), description="Veo: возврат (нет API ключа)")
            return {
                "text": "❌ API ключ не настроен. Обратитесь к администратору.",
                "keyboard": kb.back_to_main_keyboard(),
            }
        
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
        
        # Выполняем генерацию
        client = FalClient(api_key)
        result = await client.generate_video(
            prompt=state_data["prompt"],
            duration=state_data["duration"],
            aspect_ratio=state_data["aspect_ratio"],
            negative_prompt=state_data.get("negative_prompt"),
            enhance_prompt=state_data.get("enhance_prompt", True),
        )
        
        # Обновляем запись в БД
        session = get_session()
        try:
            generation = session.query(VideoGeneration).get(generation_id)
            
            if result.success:
                generation.status = "completed"
                generation.video_url = result.video_url
                generation.generation_time = result.generation_time
                generation.fal_request_id = result.request_id
                generation.completed_at = datetime.utcnow()
                
                # Очищаем состояние
                await self.core.clear_user_state(user_id)
                
                # Проверяем настройки галереи
                gallery_enabled = service_config.get("gallery_enabled", False)
                
                session.commit()
                
                text = msg.GENERATION_SUCCESS.format(
                    prompt=state_data["prompt"],
                    duration=DURATION_NAMES.get(state_data["duration"], state_data["duration"]),
                    generation_time=f"{result.generation_time:.1f} сек" if result.generation_time else "N/A",
                    cost=f"{cost_gton:.4f}",
                )
                
                # Отправляем видео напрямую через bot (callback устаревает за время генерации)
                if context and context.bot:
                    from core.platform.telegram.utils import build_keyboard
                    try:
                        keyboard = build_keyboard(kb.generation_result_keyboard(generation_id, gallery_enabled))
                        await send_video_robust(
                            context.bot,
                            chat_id=context.chat_id,
                            video=result.video_url,
                            caption=text,
                            reply_markup=keyboard,
                            parse_mode="HTML",
                        )
                    except Exception as e:
                        logger.error(f"Error sending video: {e}")
                
                return {"text": "", "keyboard": None, "sent": True}
            else:
                generation.status = "failed"
                generation.error_message = result.error
                session.commit()
                
                # Возвращаем средства
                await self.core.add_balance(user_id, float(cost_gton), description="Veo: возврат (ошибка)")
                await self.core.clear_user_state(user_id)
                
                return {
                    "text": msg.GENERATION_ERROR.format(error=result.error),
                    "keyboard": kb.back_to_main_keyboard(),
                }
        finally:
            session.close()
    
    async def _calculate_cost(self, duration: str) -> Decimal:
        """Рассчитать стоимость в GTON"""
        # Получаем конфиг сервиса
        service_config = await self.core.get_service_config()
        margin = service_config.get("margin_multiplier", DEFAULT_MARGIN)
        
        # Базовая цена в USD
        price_usd = PRICES.get(duration, 2.50)
        
        # Добавляем маржу
        price_with_margin = price_usd * (1 + margin)
        
        # Конвертируем в GTON
        gton_amount = await self.core.convert_to_gton(price_with_margin, "USD")
        
        # Округляем вверх до 4 знаков
        return Decimal(str(gton_amount)).quantize(Decimal("0.0001"), rounding=ROUND_UP)
    
    async def _get_settings(self, user_id: int) -> dict:
        """Получить настройки пользователя"""
        settings = await self.core.get_user_service_settings(user_id)
        if not settings:
            settings = {}
        
        for key, value in DEFAULT_USER_SETTINGS.items():
            if key not in settings:
                settings[key] = value
        
        return settings
