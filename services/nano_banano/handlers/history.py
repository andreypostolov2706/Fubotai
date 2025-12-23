"""
Nano Banano — History Handler
"""
from datetime import datetime
from typing import TYPE_CHECKING

from loguru import logger

from .. import messages as msg
from .. import keyboards as kb
from ..database import get_session, Generation

if TYPE_CHECKING:
    from ..service import NanoBananoService


ITEMS_PER_PAGE = 6


class HistoryHandler:
    """Обработчик истории генераций"""
    
    def __init__(self, service: "NanoBananoService"):
        self.service = service
        self.core = service.core
    
    async def show_history(self, user_id: int, page: int = 1) -> dict:
        """Показать историю генераций"""
        with get_session() as session:
            # Получаем общее количество
            total = session.query(Generation).filter(
                Generation.user_id == user_id,
                Generation.status == "completed"
            ).count()
            
            if total == 0:
                return {
                    "text": msg.HISTORY_EMPTY,
                    "keyboard": kb.back_to_main_keyboard(),
                }
            
            # Пагинация
            total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            page = max(1, min(page, total_pages))
            offset = (page - 1) * ITEMS_PER_PAGE
            
            # Получаем генерации
            generations = session.query(Generation).filter(
                Generation.user_id == user_id,
                Generation.status == "completed"
            ).order_by(Generation.created_at.desc()).offset(offset).limit(ITEMS_PER_PAGE).all()
            
            text = msg.HISTORY_LIST.format(
                total=total,
                page=page,
                total_pages=total_pages,
            )
            
            return {
                "text": text,
                "keyboard": kb.history_keyboard(page, total_pages, generations),
            }
    
    async def view_generation(self, user_id: int, generation_id: int) -> dict:
        """Просмотр конкретной генерации"""
        with get_session() as session:
            gen = session.query(Generation).filter(
                Generation.id == generation_id,
                Generation.user_id == user_id
            ).first()
            
            if not gen:
                return {
                    "text": "❌ Генерация не найдена",
                    "keyboard": kb.back_to_main_keyboard(),
                }
            
            # Формируем текст
            negative_section = ""
            if gen.negative_prompt:
                negative_section = f"🚫 <b>Негатив:</b>\n<i>{gen.negative_prompt}</i>\n\n"
            
            date_str = gen.created_at.strftime("%d.%m.%Y %H:%M") if gen.created_at else "—"
            
            text = msg.GENERATION_VIEW.format(
                prompt=gen.prompt,
                negative_section=negative_section,
                model_name=msg.MODEL_NAMES.get(gen.model, gen.model),
                aspect_ratio=gen.aspect_ratio or "—",
                cost=f"{gen.cost_gton:.4f}" if gen.cost_gton else "—",
                date=date_str,
            )
            
            # Проверяем включена ли галерея
            config = await self.core.get_service_config()
            gallery_enabled = (
                config.get("gallery_enabled", False) and 
                config.get("gallery_channel_id", "") and
                not gen.published_to_gallery
            )
            
            return {
                "text": text,
                "keyboard": kb.generation_view_keyboard(generation_id, gallery_enabled),
                "photo_url": gen.image_url,
                "file_id": gen.file_id,
            }
    
    async def delete_generation(self, user_id: int, generation_id: int) -> dict:
        """Удалить генерацию"""
        with get_session() as session:
            gen = session.query(Generation).filter(
                Generation.id == generation_id,
                Generation.user_id == user_id
            ).first()
            
            if not gen:
                return {
                    "text": "❌ Генерация не найдена",
                    "keyboard": kb.back_to_main_keyboard(),
                }
            
            session.delete(gen)
            session.commit()
        
        return await self.show_history(user_id)
    
    async def save_file_id(self, generation_id: int, file_id: str):
        """Сохранить Telegram file_id для быстрой повторной отправки"""
        with get_session() as session:
            gen = session.query(Generation).filter(Generation.id == generation_id).first()
            if gen:
                gen.file_id = file_id
                session.commit()
