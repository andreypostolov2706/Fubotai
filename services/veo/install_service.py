"""
Скрипт установки сервиса Veo
Запустите: python -m services.veo.install_service install
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from loguru import logger


async def install():
    """Установить сервис Veo"""
    from core.database import get_db
    from core.database.models import Service
    from sqlalchemy import select
    
    service_data = {
        "id": "veo",
        "name": "Veo",
        "description": "Генерация видео с помощью Google Veo 2",
        "version": "1.0.0",
        "author": "FuBot Team",
        "icon": "🎬",
        "status": "active",
        "features": {
            "subscriptions": False,
            "broadcasts": False,
            "partner_menu": False,
            "voice_messages": False,
        },
        "permissions": [
            "balance:read",
            "balance:deduct",
            "balance:add",
            "notifications:send",
            "analytics:track",
        ],
        "config": {
            "fal_api_key": "",
            "margin_multiplier": 0.3,
            "prices": {
                "5s": 2.50,
                "6s": 3.00,
                "7s": 3.50,
                "8s": 4.00,
            },
            "gallery_channel_id": "",
            "gallery_enabled": False,
        },
    }
    
    async with get_db() as session:
        result = await session.execute(
            select(Service).where(Service.id == service_data["id"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info(f"Сервис {service_data['id']} уже установлен. Обновляем...")
            existing.name = service_data["name"]
            existing.description = service_data["description"]
            existing.version = service_data["version"]
            existing.author = service_data["author"]
            existing.icon = service_data["icon"]
            existing.status = service_data["status"]
            existing.features = service_data["features"]
            existing.permissions = service_data["permissions"]
            existing.config = service_data["config"]
        else:
            logger.info(f"Устанавливаем сервис {service_data['id']}...")
            service = Service(**service_data)
            session.add(service)
        
        await session.commit()
    
    # Инициализируем БД сервиса
    from services.veo.database import init_db
    init_db()
    
    logger.info(f"✅ Сервис Veo успешно установлен!")
    logger.info(f"")
    logger.info(f"Не забудьте:")
    logger.info(f"1. Указать fal_api_key в настройках сервиса")
    logger.info(f"2. Перезапустить бота")


async def uninstall():
    """Удалить сервис Veo"""
    from core.database import get_db
    from core.database.models import Service
    from sqlalchemy import delete
    
    async with get_db() as session:
        await session.execute(
            delete(Service).where(Service.id == "veo")
        )
        await session.commit()
    
    logger.info(f"✅ Сервис Veo удалён из базы данных")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Управление сервисом Veo")
    parser.add_argument("action", choices=["install", "uninstall"], help="Действие")
    args = parser.parse_args()
    
    if args.action == "install":
        asyncio.run(install())
    elif args.action == "uninstall":
        asyncio.run(uninstall())
