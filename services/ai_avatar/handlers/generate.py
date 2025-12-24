"""
AI Avatar — Generate Handler
"""
import asyncio
from datetime import datetime
from decimal import Decimal
from loguru import logger

from core.plugins.base_service import CallbackContext, MessageContext, Response
from ..config import (
    FAL_PRICES_USD, ESTIMATED_GENERATION_TIME, PROGRESS_FRAMES,
    MAX_VIDEO_DURATION, MAX_FILE_SIZE_MB, VISUAL_STYLE_PROMPTS
)
from .. import messages as msg
from .. import keyboards as kb


class GenerateHandler:
    """Обработчик генерации видео"""
    
    def __init__(self, service):
        self.service = service
    
    async def start_generation(self, ctx: CallbackContext) -> Response:
        """Начало процесса генерации"""
        user_id = ctx.user_id
        
        # Сбрасываем состояние
        await self.service.core_api.user_state.set(
            user_id,
            f"{self.service.info.id}:state",
            "awaiting_image"
        )
        
        return Response(
            text=msg.UPLOAD_IMAGE,
            keyboard=kb.cancel_keyboard(),
        )
    
    async def handle_image_upload(self, ctx: MessageContext) -> Response:
        """Обработка загрузки изображения"""
        user_id = ctx.user_id
        
        # Проверяем наличие фото
        if not ctx.message.photo:
            return Response(text=msg.ERROR_INVALID_IMAGE)
        
        # Получаем самое большое фото
        photo = ctx.message.photo[-1]
        
        # Проверяем размер
        if photo.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return Response(
                text=msg.ERROR_FILE_TOO_LARGE.format(
                    max_size_mb=MAX_FILE_SIZE_MB,
                    file_size_mb=round(photo.file_size / 1024 / 1024, 2)
                )
            )
        
        # Получаем URL фото
        file = await ctx.bot.get_file(photo.file_id)
        image_url = file.file_path
        
        # Сохраняем в состояние
        await self.service.core_api.user_state.set(
            user_id,
            f"{self.service.info.id}:image_url",
            image_url
        )
        
        # Переходим к выбору режима ввода
        await self.service.core_api.user_state.set(
            user_id,
            f"{self.service.info.id}:state",
            "choosing_mode"
        )
        
        return Response(
            text=msg.UPLOAD_AUDIO,
            keyboard=kb.input_mode_keyboard(),
        )
    
    async def handle_mode_choice(self, ctx: CallbackContext, mode: str) -> Response:
        """Обработка выбора режима (audio или text)"""
        user_id = ctx.user_id
        
        await self.service.core_api.user_state.set(
            user_id,
            f"{self.service.info.id}:input_mode",
            mode
        )
        
        if mode == "audio":
            await self.service.core_api.user_state.set(
                user_id,
                f"{self.service.info.id}:state",
                "awaiting_audio"
            )
            return Response(
                text=msg.UPLOAD_AUDIO,
                keyboard=kb.cancel_keyboard(),
            )
        else:  # text
            await self.service.core_api.user_state.set(
                user_id,
                f"{self.service.info.id}:state",
                "awaiting_text"
            )
            return Response(
                text=msg.ENTER_TEXT_FOR_TTS,
                keyboard=kb.cancel_keyboard(),
            )
    
    async def handle_audio_upload(self, ctx: MessageContext) -> Response:
        """Обработка загрузки аудио"""
        user_id = ctx.user_id
        
        # Проверяем наличие аудио или голосового сообщения
        audio = ctx.message.audio or ctx.message.voice
        
        if not audio:
            return Response(text=msg.ERROR_INVALID_AUDIO)
        
        # Проверяем размер
        if audio.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            return Response(
                text=msg.ERROR_FILE_TOO_LARGE.format(
                    max_size_mb=MAX_FILE_SIZE_MB,
                    file_size_mb=round(audio.file_size / 1024 / 1024, 2)
                )
            )
        
        # Проверяем длительность
        if hasattr(audio, 'duration') and audio.duration > MAX_VIDEO_DURATION:
            return Response(
                text=msg.ERROR_DURATION_TOO_LONG.format(
                    max_duration=MAX_VIDEO_DURATION,
                    duration=audio.duration
                )
            )
        
        # Получаем URL аудио
        file = await ctx.bot.get_file(audio.file_id)
        audio_url = file.file_path
        
        # Сохраняем в состояние
        await self.service.core_api.user_state.set(
            user_id,
            f"{self.service.info.id}:audio_url",
            audio_url
        )
        
        if hasattr(audio, 'duration'):
            await self.service.core_api.user_state.set(
                user_id,
                f"{self.service.info.id}:duration",
                audio.duration
            )
        
        # Переходим к подтверждению
        return await self.show_confirmation(user_id)
    
    async def handle_text_input(self, ctx: MessageContext) -> Response:
        """Обработка ввода текста для TTS"""
        user_id = ctx.user_id
        text = ctx.message.text
        
        if len(text) > 500:
            return Response(text="❌ Текст слишком длинный. Максимум 500 символов.")
        
        # Сохраняем текст
        await self.service.core_api.user_state.set(
            user_id,
            f"{self.service.info.id}:tts_text",
            text
        )
        
        # Оцениваем длительность (примерно 150 слов в минуту)
        words = len(text.split())
        estimated_duration = (words / 150) * 60
        
        await self.service.core_api.user_state.set(
            user_id,
            f"{self.service.info.id}:duration",
            estimated_duration
        )
        
        # Переходим к подтверждению
        return await self.show_confirmation(user_id)
    
    async def show_confirmation(self, user_id: int) -> Response:
        """Показ экрана подтверждения"""
        # Получаем настройки пользователя
        user_settings = await self.service.core_api.user_data.get_settings(
            user_id,
            self.service.info.id
        )
        quality = user_settings.get("quality", "480p")
        
        # Получаем длительность
        duration = await self.service.core_api.user_state.get(
            user_id,
            f"{self.service.info.id}:duration"
        ) or 10.0
        
        # Рассчитываем стоимость
        price_per_sec_usd = FAL_PRICES_USD[quality]
        margin = await self.service.get_config_value("margin_multiplier", 0.3)
        total_usd = float(price_per_sec_usd * Decimal(str(duration)) * (1 + Decimal(str(margin))))
        
        # Конвертируем в GTON
        total_gton = await self.service.core_api.balance.usd_to_gton(total_usd)
        
        # Получаем баланс
        balance_gton = await self.service.core_api.balance.get(user_id)
        
        # Проверяем баланс
        if balance_gton < total_gton:
            return Response(
                text=msg.INSUFFICIENT_BALANCE.format(
                    required_gton=round(total_gton, 4),
                    balance_gton=round(balance_gton, 4),
                    missing_gton=round(total_gton - balance_gton, 4)
                ),
                keyboard=kb.back_to_main_keyboard(),
            )
        
        # Сохраняем стоимость
        await self.service.core_api.user_state.set(
            user_id,
            f"{self.service.info.id}:cost_usd",
            total_usd
        )
        await self.service.core_api.user_state.set(
            user_id,
            f"{self.service.info.id}:cost_gton",
            total_gton
        )
        
        # Формируем текст подтверждения
        style = "Стандартный"
        
        text = msg.CONFIRMATION.format(
            quality=quality,
            duration=round(duration, 1),
            style=style,
            cost_gton=round(total_gton, 4),
            cost_usd=round(total_usd, 2),
            balance_gton=round(balance_gton, 4)
        )
        
        await self.service.core_api.user_state.set(
            user_id,
            f"{self.service.info.id}:state",
            "confirming"
        )
        
        return Response(
            text=text,
            keyboard=kb.confirmation_keyboard(),
        )
    
    async def confirm_generation(self, ctx: CallbackContext) -> Response:
        """Подтверждение и запуск генерации"""
        user_id = ctx.user_id
        
        # Получаем все данные из состояния
        image_url = await self.service.core_api.user_state.get(
            user_id,
            f"{self.service.info.id}:image_url"
        )
        audio_url = await self.service.core_api.user_state.get(
            user_id,
            f"{self.service.info.id}:audio_url"
        )
        tts_text = await self.service.core_api.user_state.get(
            user_id,
            f"{self.service.info.id}:tts_text"
        )
        cost_usd = await self.service.core_api.user_state.get(
            user_id,
            f"{self.service.info.id}:cost_usd"
        )
        cost_gton = await self.service.core_api.user_state.get(
            user_id,
            f"{self.service.info.id}:cost_gton"
        )
        
        user_settings = await self.service.core_api.user_data.get_settings(
            user_id,
            self.service.info.id
        )
        quality = user_settings.get("quality", "480p")
        
        # Списываем средства
        success = await self.service.core_api.balance.deduct(
            user_id,
            cost_gton,
            f"AI Avatar generation ({quality})"
        )
        
        if not success:
            return Response(text=msg.INSUFFICIENT_BALANCE)
        
        # Запускаем генерацию в фоне
        asyncio.create_task(
            self._generate_video(
                user_id=user_id,
                image_url=image_url,
                audio_url=audio_url,
                tts_text=tts_text,
                quality=quality,
                cost_usd=cost_usd,
                cost_gton=cost_gton,
            )
        )
        
        # Показываем прогресс
        estimated_time = ESTIMATED_GENERATION_TIME.get(quality, 30)
        
        return Response(
            text=msg.GENERATING.format(
                progress=PROGRESS_FRAMES[0],
                estimated_time=estimated_time
            ),
        )
    
    async def _generate_video(
        self,
        user_id: int,
        image_url: str,
        audio_url: str,
        tts_text: str,
        quality: str,
        cost_usd: float,
        cost_gton: float,
    ):
        """Фоновая генерация видео"""
        try:
            # Получаем API клиент
            fal_api_key = await self.service.get_config_value("fal_api_key")
            
            if not fal_api_key:
                await self._handle_generation_error(
                    user_id, "API ключ не настроен", cost_gton
                )
                return
            
            from ..api import FalClient
            client = FalClient(fal_api_key)
            
            # Если используется TTS, сначала генерируем аудио
            if tts_text and not audio_url:
                # TODO: Интеграция TTS API
                logger.warning("TTS не реализован, используйте загрузку аудио")
                await self._handle_generation_error(
                    user_id, "TTS пока не поддерживается", cost_gton
                )
                return
            
            # Генерируем видео
            prompt = VISUAL_STYLE_PROMPTS["default"]
            result = await client.generate_avatar_video(
                image_url=image_url,
                audio_url=audio_url,
                prompt=prompt,
                quality=quality,
            )
            
            if not result.success:
                await self._handle_generation_error(
                    user_id, result.error, cost_gton
                )
                return
            
            # Сохраняем в БД
            from ..database import AvatarGeneration
            from core.database import get_db
            
            async with get_db() as session:
                generation = AvatarGeneration(
                    user_id=user_id,
                    image_url=image_url,
                    audio_url=audio_url,
                    quality=quality,
                    video_url=result.video_url,
                    video_duration=result.video_duration,
                    cost_usd=cost_usd,
                    cost_gton=cost_gton,
                    status="completed",
                    request_id=result.request_id,
                    generation_time=result.generation_time,
                    completed_at=datetime.utcnow(),
                )
                session.add(generation)
                await session.commit()
                generation_id = generation.id
            
            # Отправляем результат
            await self.service.core_api.notifications.send(
                user_id=user_id,
                text=msg.GENERATION_COMPLETE.format(
                    generation_time=round(result.generation_time, 1),
                    cost_gton=round(cost_gton, 4)
                ),
                keyboard=kb.result_keyboard(generation_id),
            )
            
            # Отправляем видео
            await self.service.core_api.notifications.send_video(
                user_id=user_id,
                video_url=result.video_url,
            )
            
            logger.info(f"AI Avatar: Видео успешно сгенерировано для user_id={user_id}")
            
        except Exception as e:
            logger.error(f"AI Avatar: Ошибка генерации для user_id={user_id}: {e}")
            await self._handle_generation_error(user_id, str(e), cost_gton)
    
    async def _handle_generation_error(self, user_id: int, error: str, cost_gton: float):
        """Обработка ошибки генерации"""
        # Возвращаем средства
        await self.service.core_api.balance.add(
            user_id,
            cost_gton,
            "AI Avatar generation failed - refund"
        )
        
        # Отправляем уведомление
        await self.service.core_api.notifications.send(
            user_id=user_id,
            text=msg.GENERATION_FAILED.format(error_message=error),
            keyboard=kb.back_to_main_keyboard(),
        )
