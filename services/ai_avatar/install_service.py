"""
AI Avatar Service Installation Script
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from core.database import get_db
from core.database.models import Service
from sqlalchemy import select


async def install_service():
    """Установка сервиса AI Avatar"""
    
    logger.info("Начало установки сервиса AI Avatar...")
    
    try:
        # Инициализируем БД
        from core.database.connection import db_manager
        await db_manager.init()
        
        async with get_db() as session:
            # Проверяем, не установлен ли уже сервис
            result = await session.execute(
                select(Service).where(Service.id == "ai_avatar")
            )
            existing_service = result.scalar_one_or_none()
            
            if existing_service:
                logger.warning("Сервис AI Avatar уже установлен!")
                response = input("Переустановить? (y/n): ")
                if response.lower() != 'y':
                    logger.info("Установка отменена")
                    return
                
                # Удаляем старую запись
                await session.delete(existing_service)
                await session.commit()
                logger.info("Старая версия удалена")
            
            # Создаём новую запись сервиса
            service = Service(
                id="ai_avatar",
                name="AI Avatar",
                description="Превращает фото в говорящее видео с синхронизацией губ",
                version="1.0.0",
                author="FuBot Team",
                status="active",
                install_path="services.ai_avatar",
                icon="🎭",
                config={
                    "fal_api_key": "",
                    "margin_multiplier": 0.3,
                    "prices": {
                        "480p": 0.10,
                        "720p": 0.14,
                    },
                    "referral_bonus_enabled": True,
                    "referral_bonus_percent": 10,
                    "gallery_channel_id": "",
                    "gallery_enabled": False,
                    "max_video_duration": 60,
                    "max_file_size_mb": 10,
                },
                permissions=[
                    "balance:read",
                    "balance:deduct",
                    "balance:add",
                    "notifications:send",
                    "analytics:track",
                ],
                features={
                    "subscriptions": False,
                    "broadcasts": False,
                    "partner_menu": False,
                    "voice_messages": True,
                },
                menu_order=20,
            )
            
            session.add(service)
            await session.commit()
            
            logger.success("✅ Сервис AI Avatar успешно установлен!")
            logger.info("Следующие шаги:")
            logger.info("1. Получите API ключ на https://fal.ai")
            logger.info("2. Настройте API ключ в админ-панели бота")
            logger.info("3. Перезапустите бота: supervisorctl restart fubotai")
            
    except Exception as e:
        logger.error(f"❌ Ошибка установки: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(install_service())
