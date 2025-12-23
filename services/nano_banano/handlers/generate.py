"""
Nano Banano — Text-to-Image Handler
"""
import asyncio
import io
import time
from decimal import Decimal, ROUND_UP
from datetime import datetime
from typing import TYPE_CHECKING

import aiohttp
from loguru import logger
from telegram import InputFile

from ..config import (
    FAL_ENDPOINTS, FAL_PRICES_USD, ESTIMATED_GENERATION_TIME,
    PROGRESS_FRAMES, DEFAULT_USER_SETTINGS
)
from .. import messages as msg
from .. import keyboards as kb
from ..api.fal_client import NanoBananoClient
from ..database import get_session, Generation
from core.platform.telegram.media_sender import send_photo_robust

if TYPE_CHECKING:
    from ..service import NanoBananoService


class GenerateHandler:
    """Обработчик генерации изображений (Text-to-Image)"""
    
    def __init__(self, service: "NanoBananoService"):
        self.service = service
        self.core = service.core
    
    async def start_generation(self, user_id: int) -> dict:
        """Начать процесс генерации - запросить промпт"""
        # Устанавливаем состояние
        await self.core.set_user_state(user_id, "waiting_prompt", {"mode": "generate"})
        
        return {
            "text": msg.PROMPT_REQUEST,
            "keyboard": kb.cancel_keyboard(),
        }
    
    async def handle_prompt(self, user_id: int, prompt: str, state_data: dict) -> dict:
        """Обработка введённого промпта"""
        # Сохраняем промпт и переходим к негативному промпту
        state_data["prompt"] = prompt
        await self.core.set_user_state(user_id, "waiting_negative", state_data)
        
        return {
            "text": msg.NEGATIVE_PROMPT_REQUEST,
            "keyboard": kb.skip_negative_keyboard(),
        }
    
    async def handle_negative(self, user_id: int, negative: str, state_data: dict) -> dict:
        """Обработка негативного промпта"""
        state_data["negative_prompt"] = negative
        return await self._show_confirmation(user_id, state_data)
    
    async def skip_negative(self, user_id: int, state_data: dict) -> dict:
        """Пропустить негативный промпт"""
        state_data["negative_prompt"] = None
        return await self._show_confirmation(user_id, state_data)
    
    async def _show_confirmation(self, user_id: int, state_data: dict) -> dict:
        """Показать экран подтверждения"""
        # Получаем настройки пользователя
        settings = await self.core.get_user_service_settings(user_id)
        if not settings:
            settings = DEFAULT_USER_SETTINGS.copy()
        
        model = settings.get("model", "nano_banana")
        aspect_ratio = settings.get("aspect_ratio", "1:1")
        resolution = settings.get("resolution", "1K")
        
        # Рассчитываем стоимость
        cost = await self._calculate_cost(model, resolution)
        balance = await self.core.get_balance(user_id)
        
        # Сохраняем в state
        state_data["model"] = model
        state_data["aspect_ratio"] = aspect_ratio
        state_data["resolution"] = resolution
        state_data["output_format"] = settings.get("output_format", "png")
        state_data["cost"] = str(cost)
        
        await self.core.set_user_state(user_id, "confirming", state_data)
        
        # Формируем текст
        negative_section = ""
        if state_data.get("negative_prompt"):
            negative_section = msg.NEGATIVE_SECTION.format(
                negative=state_data["negative_prompt"]
            )
        
        resolution_section = ""
        if model == "nano_banana_pro":
            resolution_section = msg.RESOLUTION_SECTION.format(resolution=resolution)
        
        text = msg.CONFIRM_GENERATION.format(
            prompt=state_data["prompt"],
            negative_section=negative_section,
            model_name=msg.MODEL_NAMES.get(model, model),
            aspect_ratio=aspect_ratio,
            resolution_section=resolution_section,
            cost=f"{cost:.4f}",
            balance=f"{balance:.4f}",
        )
        
        return {
            "text": text,
            "keyboard": kb.confirm_generation_keyboard(),
        }
    
    async def execute_generation(self, user_id: int, state_data: dict, context) -> dict:
        """Выполнить генерацию"""
        prompt = state_data["prompt"]
        negative_prompt = state_data.get("negative_prompt")
        model = state_data["model"]
        aspect_ratio = state_data["aspect_ratio"]
        resolution = state_data.get("resolution", "1K")
        output_format = state_data.get("output_format", "png")
        cost = Decimal(state_data["cost"])
        
        # Проверяем баланс
        balance = await self.core.get_balance(user_id)
        if balance < cost:
            return {
                "text": msg.INSUFFICIENT_BALANCE.format(
                    cost=f"{cost:.4f}",
                    balance=f"{balance:.4f}"
                ),
                "keyboard": kb.insufficient_balance_keyboard(),
            }
        
        # Проверяем API ключ
        config = await self.core.get_service_config()
        api_key = config.get("fal_api_key", "")
        if not api_key:
            return {
                "text": msg.API_NOT_CONFIGURED,
                "keyboard": kb.back_to_main_keyboard(),
            }
        
        # Списываем GTON
        deduct_result = await self.core.deduct_balance(
            user_id=user_id,
            amount=cost,
            reason=f"Генерация изображения Nano Banano ({model})",
            action="generate_image"
        )
        
        if not deduct_result.success:
            return {
                "text": msg.INSUFFICIENT_BALANCE.format(
                    cost=f"{cost:.4f}",
                    balance=f"{balance:.4f}"
                ),
                "keyboard": kb.insufficient_balance_keyboard(),
            }
        
        # Создаём запись в БД
        with get_session() as session:
            generation = Generation(
                user_id=user_id,
                mode="generate",
                prompt=prompt,
                negative_prompt=negative_prompt,
                model=model,
                aspect_ratio=aspect_ratio,
                resolution=resolution if model == "nano_banana_pro" else None,
                output_format=output_format,
                cost_gton=cost,
                status="pending",
            )
            session.add(generation)
            session.commit()
            generation_id = generation.id
        
        # Очищаем состояние
        await self.core.clear_user_state(user_id)
        
        # Запускаем генерацию с анимацией прогресса
        estimated_time = ESTIMATED_GENERATION_TIME.get(
            f"{model}_{resolution.lower()}" if model == "nano_banana_pro" else model,
            15
        )
        
        # Возвращаем начальное сообщение о генерации
        # Анимация будет обновляться в отдельной задаче
        return await self._run_generation_with_progress(
            user_id=user_id,
            generation_id=generation_id,
            prompt=prompt,
            negative_prompt=negative_prompt,
            model=model,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            output_format=output_format,
            cost=cost,
            estimated_time=estimated_time,
            context=context,
        )
    
    async def _run_generation_with_progress(
        self,
        user_id: int,
        generation_id: int,
        prompt: str,
        negative_prompt: str,
        model: str,
        aspect_ratio: str,
        resolution: str,
        output_format: str,
        cost: Decimal,
        estimated_time: int,
        context,
    ) -> dict:
        """Запустить генерацию с анимированным прогрессом"""
        from ..api import FalClient
        
        config = await self.core.get_service_config()
        api_key = config.get("fal_api_key", "")
        
        # Определяем endpoint
        endpoint = FAL_ENDPOINTS[model]["generate"]
        
        # Создаём клиент
        client = FalClient(api_key)
        
        # Показываем "Генерирую..."
        if context and context.bot:
            try:
                await context.bot.edit_message_text(
                    chat_id=context.chat_id,
                    message_id=context.message_id,
                    text="🍌 <b>Генерирую изображение...</b>\n\nЭто может занять 10-30 секунд.",
                    parse_mode="HTML"
                )
            except Exception:
                pass
        
        start_time = time.time()
        
        # Запускаем генерацию
        result = await client.generate_image(
            endpoint=endpoint,
            prompt=prompt,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio,
            output_format=output_format,
            resolution=resolution if model == "nano_banana_pro" else None,
        )
        
        generation_time = time.time() - start_time
        
        # Обновляем запись в БД
        with get_session() as session:
            gen = session.query(Generation).filter(Generation.id == generation_id).first()
            if gen:
                if result.success:
                    gen.status = "completed"
                    gen.image_url = result.image_url
                    gen.fal_request_id = result.request_id
                    gen.generation_time = generation_time
                    gen.completed_at = datetime.utcnow()
                else:
                    gen.status = "failed"
                    gen.error_message = result.error
                session.commit()
        
        if result.success:
            # Трекаем событие
            await self.core.track_event(
                "image_generated",
                user_id=user_id,
                value=int(cost * 10000),
                properties={"model": model, "mode": "generate"}
            )
            
            # Проверяем включена ли галерея
            gallery_enabled = config.get("gallery_enabled", False) and config.get("gallery_channel_id", "")
            
            # Отправляем фото напрямую через bot (callback уже устарел)
            if context and context.bot:
                from core.platform.telegram.utils import build_keyboard
                try:
                    keyboard = build_keyboard(kb.generation_result_keyboard(generation_id, gallery_enabled))
                    await send_photo_robust(
                        context.bot,
                        chat_id=context.chat_id,
                        photo=result.image_url,
                        caption=msg.GENERATION_SUCCESS.format(
                            cost=f"{cost:.4f}",
                            time=generation_time,
                        ),
                        reply_markup=keyboard,
                        parse_mode="HTML",
                    )
                except Exception as e:
                    logger.error(f"Error sending photo: {e}")
            
            # Возвращаем пустой результат (фото уже отправлено)
            return {
                "text": "",
                "keyboard": None,
                "sent": True,
            }
        else:
            # Возвращаем GTON
            await self.core.add_balance(
                user_id=user_id,
                amount=cost,
                source="refund",
                reason="Возврат за неудачную генерацию Nano Banano"
            )
            
            # Обновляем статус
            with get_session() as session:
                gen = session.query(Generation).filter(Generation.id == generation_id).first()
                if gen:
                    gen.status = "refunded"
                    session.commit()
            
            return {
                "text": msg.GENERATION_ERROR.format(error=result.error),
                "keyboard": kb.back_to_main_keyboard(),
            }
    
    async def _calculate_cost(self, model: str, resolution: str = "1K") -> Decimal:
        """Рассчитать стоимость генерации"""
        config = await self.core.get_service_config()
        margin = Decimal(str(config.get("margin_multiplier", 0.3)))
        prices = config.get("prices", {})
        
        # Определяем базовую цену в USD
        if model == "nano_banana":
            base_usd = Decimal(str(prices.get("nano_banana", 0.04)))
        else:  # nano_banana_pro
            price_key = f"nano_banana_pro_{resolution.lower()}"
            base_usd = Decimal(str(prices.get(price_key, 0.15)))
        
        # Применяем маржу
        total_usd = base_usd * (1 + margin)
        
        # Конвертируем USD → GTON
        gton_cost = await self.core.convert_to_gton(total_usd, "USD")
        
        if gton_cost is None:
            # Fallback если конвертация не удалась
            gton_cost = total_usd / Decimal("10")  # Примерный курс
        
        # Округляем до 4 знаков
        gton_cost = gton_cost.quantize(Decimal("0.0001"), rounding=ROUND_UP)
        
        return gton_cost
    
    async def repeat_generation(self, user_id: int, generation_id: int) -> dict:
        """Повторить генерацию с теми же параметрами"""
        with get_session() as session:
            gen = session.query(Generation).filter(Generation.id == generation_id).first()
            if not gen:
                return {
                    "text": "❌ Генерация не найдена",
                    "keyboard": kb.back_to_main_keyboard(),
                }
            
            # Восстанавливаем параметры
            state_data = {
                "mode": gen.mode,
                "prompt": gen.prompt,
                "negative_prompt": gen.negative_prompt,
                "model": gen.model,
                "aspect_ratio": gen.aspect_ratio,
                "resolution": gen.resolution or "1K",
                "output_format": gen.output_format,
            }
        
        return await self._show_confirmation(user_id, state_data)
