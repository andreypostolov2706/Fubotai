"""
Скрипт установки сервиса Nano Banano
Запустите: python -m services.nano_banano.install_service
"""
import asyncio
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from loguru import logger


async def install():
    """Установить сервис Nano Banano"""
    from core.database import get_db
    from core.database.models import Service
    from sqlalchemy import select
    
    service_data = {
        "id": "nano_banano",
        "name": "Nano Banano",
        "description": "Генерация и редактирование изображений с помощью ИИ",
        "version": "1.0.0",
        "author": "FuBot Team",
        "icon": "🍌",
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
                "nano_banana": 0.04,
                "nano_banana_pro_1k": 0.15,
                "nano_banana_pro_2k": 0.22,
                "nano_banana_pro_4k": 0.30,
            },
            "referral_bonus_enabled": True,
            "referral_bonus_percent": 10,
            "gallery_channel_id": "",
            "gallery_enabled": False,
            "max_images_per_request": 4,
            "max_input_images": 4,
        },
    }
    
    async with get_db() as session:
        # Проверяем существует ли уже
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
    from services.nano_banano.database import init_db
    init_db()
    
    logger.info(f"✅ Сервис Nano Banano успешно установлен!")
    logger.info(f"")
    logger.info(f"Не забудьте:")
    logger.info(f"1. Указать fal_api_key в настройках сервиса")
    logger.info(f"2. Перезапустить бота")


async def uninstall():
    """Удалить сервис Nano Banano"""
    from core.database import get_db
    from core.database.models import Service
    from sqlalchemy import delete
    
    async with get_db() as session:
        await session.execute(
            delete(Service).where(Service.id == "nano_banano")
        )
        await session.commit()
    
    logger.info(f"✅ Сервис Nano Banano удалён из базы данных")
    logger.info(f"База данных сервиса (data/nano_banano.db) сохранена")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Управление сервисом Nano Banano")
    parser.add_argument("action", choices=["install", "uninstall"], help="Действие")
    args = parser.parse_args()
    
    if args.action == "install":
        asyncio.run(install())
    elif args.action == "uninstall":
        asyncio.run(uninstall())
