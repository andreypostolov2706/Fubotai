"""
FLUX 2 Flex — Скрипт установки сервиса
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database.connection import db_manager, get_db
from core.database.models import Service
from sqlalchemy import select

from . import config


async def install():
    """Установить сервис в БД"""
    await db_manager.init()
    
    async with get_db() as session:
        result = await session.execute(
            select(Service).where(Service.id == config.SERVICE_ID)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"Сервис {config.SERVICE_ID} уже установлен")
            return False
        
        service = Service(
            id=config.SERVICE_ID,
            name=config.SERVICE_NAME,
            description=config.SERVICE_DESCRIPTION,
            version=config.SERVICE_VERSION,
            author=config.SERVICE_AUTHOR,
            icon=config.SERVICE_ICON,
            status="active",
            config=config.DEFAULT_SERVICE_CONFIG,
            features={
                "text_to_image": True,
            },
            permissions=[
                "balance:read",
                "balance:deduct",
                "balance:add",
            ],
            menu_order=15,
        )
        session.add(service)
        await session.commit()
        print(f"✅ Сервис {config.SERVICE_NAME} установлен!")
        return True


async def uninstall():
    """Удалить сервис из БД"""
    await db_manager.init()
    
    async with get_db() as session:
        result = await session.execute(
            select(Service).where(Service.id == config.SERVICE_ID)
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            print(f"Сервис {config.SERVICE_ID} не найден")
            return False
        
        await session.delete(existing)
        await session.commit()
        print(f"✅ Сервис {config.SERVICE_NAME} удалён!")
        return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        asyncio.run(uninstall())
    else:
        asyncio.run(install())
