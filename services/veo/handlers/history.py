"""
Veo Service — History Handler
"""
from typing import TYPE_CHECKING
from datetime import datetime

from ..config import DURATION_NAMES, ASPECT_RATIO_NAMES
from .. import messages as msg
from .. import keyboards as kb
from ..database import get_session, VideoGeneration

if TYPE_CHECKING:
    from ..service import VeoService


class HistoryHandler:
    """Обработчик истории генераций"""
    
    ITEMS_PER_PAGE = 5
    
    def __init__(self, service: "VeoService"):
        self.service = service
        self.core = service.core
    
    async def show_history(self, user_id: int, page: int = 1) -> dict:
        """Показать историю генераций"""
        session = get_session()
        try:
            # Получаем общее количество
            total = session.query(VideoGeneration).filter(
                VideoGeneration.user_id == user_id
            ).count()
            
            if total == 0:
                return {
                    "text": msg.HISTORY_EMPTY,
                    "keyboard": kb.back_to_main_keyboard(),
                }
            
            # Пагинация
            total_pages = (total + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
            page = max(1, min(page, total_pages))
            offset = (page - 1) * self.ITEMS_PER_PAGE
            
            # Получаем записи
            generations = session.query(VideoGeneration).filter(
                VideoGeneration.user_id == user_id
            ).order_by(VideoGeneration.created_at.desc()).offset(offset).limit(self.ITEMS_PER_PAGE).all()
            
            # Формируем список для клавиатуры
            items = []
            for gen in generations:
                items.append({
                    "id": gen.id,
                    "date": gen.created_at.strftime("%d.%m.%Y"),
                })
            
            text = msg.HISTORY_TITLE.format(page=page, total_pages=total_pages)
            
            # Добавляем информацию о каждой генерации
            for gen in generations:
                prompt_preview = gen.prompt[:50] + "..." if len(gen.prompt) > 50 else gen.prompt
                text += "\n\n" + msg.HISTORY_ITEM.format(
                    id=gen.id,
                    date=gen.created_at.strftime("%d.%m.%Y %H:%M"),
                    prompt_preview=prompt_preview,
                    duration=DURATION_NAMES.get(gen.duration, gen.duration),
                    cost=f"{gen.cost_gton:.4f}" if gen.cost_gton else "0",
                )
            
            return {
                "text": text,
                "keyboard": kb.history_keyboard(page, total_pages, items),
            }
        finally:
            session.close()
    
    async def view_generation(self, user_id: int, generation_id: int) -> dict:
        """Просмотр конкретной генерации"""
        session = get_session()
        try:
            generation = session.query(VideoGeneration).filter(
                VideoGeneration.id == generation_id,
                VideoGeneration.user_id == user_id,
            ).first()
            
            if not generation:
                return {
                    "text": "❌ Генерация не найдена.",
                    "keyboard": kb.back_to_main_keyboard(),
                }
            
            text = msg.VIEW_GENERATION.format(
                id=generation.id,
                prompt=generation.prompt,
                duration=DURATION_NAMES.get(generation.duration, generation.duration),
                aspect_ratio=ASPECT_RATIO_NAMES.get(generation.aspect_ratio, generation.aspect_ratio),
                cost=f"{generation.cost_gton:.4f}" if generation.cost_gton else "0",
                date=generation.created_at.strftime("%d.%m.%Y %H:%M"),
            )
            
            has_video = bool(generation.video_url or generation.file_id)
            
            return {
                "text": text,
                "keyboard": kb.view_generation_keyboard(generation_id, has_video),
                "video_url": generation.video_url,
                "file_id": generation.file_id,
            }
        finally:
            session.close()
    
    async def delete_generation(self, user_id: int, generation_id: int) -> dict:
        """Удалить генерацию"""
        session = get_session()
        try:
            generation = session.query(VideoGeneration).filter(
                VideoGeneration.id == generation_id,
                VideoGeneration.user_id == user_id,
            ).first()
            
            if generation:
                session.delete(generation)
                session.commit()
            
            return await self.show_history(user_id)
        finally:
            session.close()
    
    async def save_file_id(self, generation_id: int, file_id: str):
        """Сохранить file_id от Telegram"""
        session = get_session()
        try:
            generation = session.query(VideoGeneration).get(generation_id)
            if generation:
                generation.file_id = file_id
                session.commit()
        finally:
            session.close()
