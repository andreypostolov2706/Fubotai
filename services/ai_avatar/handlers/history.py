"""
AI Avatar — History Handler
"""
from sqlalchemy import select, desc
from core.plugins.base_service import CallbackContext, Response
from ..database import AvatarGeneration
from core.database import get_db
from .. import messages as msg
from .. import keyboards as kb


class HistoryHandler:
    """Обработчик истории генераций"""
    
    def __init__(self, service):
        self.service = service
    
    async def show_history(self, ctx: CallbackContext, page: int = 0) -> Response:
        """Показать историю генераций"""
        user_id = ctx.user_id
        page_size = 5
        offset = page * page_size
        
        async with get_db() as session:
            # Получаем общее количество
            count_query = select(AvatarGeneration).where(
                AvatarGeneration.user_id == user_id,
                AvatarGeneration.status == "completed"
            )
            result = await session.execute(count_query)
            total_count = len(result.scalars().all())
            
            if total_count == 0:
                return Response(
                    text=msg.HISTORY_EMPTY,
                    keyboard=kb.back_to_main_keyboard(),
                )
            
            # Получаем генерации для текущей страницы
            query = select(AvatarGeneration).where(
                AvatarGeneration.user_id == user_id,
                AvatarGeneration.status == "completed"
            ).order_by(
                desc(AvatarGeneration.created_at)
            ).limit(page_size).offset(offset)
            
            result = await session.execute(query)
            generations = result.scalars().all()
            
            # Рассчитываем общую стоимость
            total_cost_query = select(AvatarGeneration).where(
                AvatarGeneration.user_id == user_id,
                AvatarGeneration.status == "completed"
            )
            result = await session.execute(total_cost_query)
            all_generations = result.scalars().all()
            total_cost_gton = sum(g.cost_gton for g in all_generations)
            
            # Формируем текст
            text = msg.HISTORY_LIST.format(
                total_count=total_count,
                total_cost_gton=round(total_cost_gton, 4)
            )
            
            # Добавляем элементы
            for gen in generations:
                text += "\n" + msg.HISTORY_ITEM.format(
                    id=gen.id,
                    created_at=gen.created_at.strftime("%d.%m.%Y %H:%M"),
                    duration=round(gen.video_duration or 0, 1),
                    quality=gen.quality,
                    cost_gton=round(gen.cost_gton, 4)
                )
            
            has_more = (offset + page_size) < total_count
            
            return Response(
                text=text,
                keyboard=kb.history_keyboard(page, has_more),
            )
    
    async def download_video(self, ctx: CallbackContext, generation_id: int) -> Response:
        """Скачать видео из истории"""
        user_id = ctx.user_id
        
        async with get_db() as session:
            query = select(AvatarGeneration).where(
                AvatarGeneration.id == generation_id,
                AvatarGeneration.user_id == user_id
            )
            result = await session.execute(query)
            generation = result.scalar_one_or_none()
            
            if not generation:
                return Response(text="❌ Генерация не найдена")
            
            if not generation.video_url:
                return Response(text="❌ Видео недоступно")
            
            # Отправляем видео
            await self.service.core_api.notifications.send_video(
                user_id=user_id,
                video_url=generation.video_url,
            )
            
            return Response(
                text="✅ Видео отправлено",
                keyboard=kb.history_item_keyboard(generation_id),
            )
    
    async def repeat_generation(self, ctx: CallbackContext, generation_id: int) -> Response:
        """Повторить генерацию с теми же параметрами"""
        user_id = ctx.user_id
        
        async with get_db() as session:
            query = select(AvatarGeneration).where(
                AvatarGeneration.id == generation_id,
                AvatarGeneration.user_id == user_id
            )
            result = await session.execute(query)
            generation = result.scalar_one_or_none()
            
            if not generation:
                return Response(text="❌ Генерация не найдена")
            
            # Восстанавливаем параметры в состояние
            await self.service.core_api.user_state.set(
                user_id,
                f"{self.service.info.id}:image_url",
                generation.image_url
            )
            await self.service.core_api.user_state.set(
                user_id,
                f"{self.service.info.id}:audio_url",
                generation.audio_url
            )
            
            # Показываем подтверждение
            from .generate import GenerateHandler
            generate_handler = GenerateHandler(self.service)
            return await generate_handler.show_confirmation(user_id)
