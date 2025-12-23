"""
Kling — History Handler
"""
from typing import TYPE_CHECKING

from ..config import SERVICE_ID
from .. import messages as msg
from .. import keyboards as kb
from ..database import get_session, VideoGeneration

if TYPE_CHECKING:
    from ..service import KlingService


class HistoryHandler:
    """Обработчик истории генераций"""
    
    ITEMS_PER_PAGE = 5
    
    def __init__(self, service: "KlingService"):
        self.service = service
        self.core = service.core
    
    async def show_history(self, user_id: int, page: int = 1) -> dict:
        """Показать историю генераций"""
        session = get_session()
        try:
            total = session.query(VideoGeneration).filter(
                VideoGeneration.user_id == user_id,
                VideoGeneration.status == "completed"
            ).count()
            
            if total == 0:
                return {
                    "text": msg.HISTORY_EMPTY,
                    "keyboard": kb.back_keyboard("main"),
                }
            
            total_pages = (total + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
            page = max(1, min(page, total_pages))
            
            offset = (page - 1) * self.ITEMS_PER_PAGE
            
            generations = session.query(VideoGeneration).filter(
                VideoGeneration.user_id == user_id,
                VideoGeneration.status == "completed"
            ).order_by(VideoGeneration.created_at.desc()).offset(offset).limit(self.ITEMS_PER_PAGE).all()
            
            text = msg.HISTORY_TITLE.format(
                total=total,
                page=page,
                pages=total_pages
            )
            
            for gen in generations:
                date_str = gen.created_at.strftime("%d.%m.%Y %H:%M")
                prompt_short = gen.prompt[:50] + "..." if len(gen.prompt) > 50 else gen.prompt
                audio_str = "🔊" if gen.audio_enabled else "🔇"
                
                text += "\n\n" + msg.HISTORY_ITEM.format(
                    id=gen.id,
                    date=date_str,
                    prompt=prompt_short,
                    duration=gen.duration,
                    audio=audio_str,
                )
            
            return {
                "text": text,
                "keyboard": kb.history_keyboard(page, total_pages),
            }
        finally:
            session.close()
    
    async def view_generation(self, user_id: int, generation_id: int) -> dict:
        """Просмотр конкретной генерации"""
        session = get_session()
        try:
            generation = session.query(VideoGeneration).filter(
                VideoGeneration.id == generation_id,
                VideoGeneration.user_id == user_id
            ).first()
            
            if not generation:
                return {
                    "text": "❌ Генерация не найдена",
                    "keyboard": kb.back_keyboard("history"),
                }
            
            date_str = generation.created_at.strftime("%d.%m.%Y %H:%M")
            audio_str = "🔊 Включено" if generation.audio_enabled else "🔇 Выключено"
            
            text = f"🎬 <b>Генерация #{generation.id}</b>\n\n"
            text += f"<b>Промпт:</b>\n<i>{generation.prompt}</i>\n\n"
            text += f"<b>Параметры:</b>\n"
            text += f"• Длительность: {generation.duration} сек\n"
            text += f"• Соотношение: {generation.aspect_ratio}\n"
            text += f"• Аудио: {audio_str}\n\n"
            text += f"<b>Стоимость:</b> {generation.cost_gton:.4f} GTON\n"
            text += f"<b>Дата:</b> {date_str}"
            
            return {
                "text": text,
                "keyboard": kb.history_item_keyboard(generation_id),
                "video_url": generation.video_url,
                "file_id": generation.file_id,
            }
        finally:
            session.close()
    
    async def delete_generation(self, user_id: int, generation_id: int) -> dict:
        """Удалить генерацию из истории"""
        session = get_session()
        try:
            generation = session.query(VideoGeneration).filter(
                VideoGeneration.id == generation_id,
                VideoGeneration.user_id == user_id
            ).first()
            
            if generation:
                session.delete(generation)
                session.commit()
            
            return await self.show_history(user_id)
        finally:
            session.close()
    
    async def get_generation_for_repeat(self, user_id: int, generation_id: int) -> dict:
        """Получить данные генерации для повтора"""
        session = get_session()
        try:
            generation = session.query(VideoGeneration).filter(
                VideoGeneration.id == generation_id,
                VideoGeneration.user_id == user_id
            ).first()
            
            if not generation:
                return None
            
            return {
                "mode": generation.mode,
                "prompt": generation.prompt,
                "duration": str(generation.duration),
                "aspect_ratio": generation.aspect_ratio,
                "audio": "on" if generation.audio_enabled else "off",
                "input_image_url": generation.input_image_url,
            }
        finally:
            session.close()
