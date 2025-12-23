"""
Sora 2 Service Installation Script
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database import get_db
from core.database.connection import db_manager
from core.database.models import Service
from sqlalchemy import select


async def install():
    """Install Sora service to database"""
    await db_manager.init()
    
    async with get_db() as session:
        # Check if service exists
        result = await session.execute(
            select(Service).where(Service.id == "sora")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("Service 'sora' already exists. Updating...")
            existing.name = "Sora 2"
            existing.description = "Генерация видео с помощью OpenAI Sora 2"
            existing.version = "1.0.0"
            existing.author = "FuBot Team"
            existing.icon = "🎬"
            existing.status = "active"
            existing.menu_order = 25
        else:
            print("Creating service 'sora'...")
            service = Service(
                id="sora",
                name="Sora 2",
                description="Генерация видео с помощью OpenAI Sora 2",
                version="1.0.0",
                author="FuBot Team",
                icon="🎬",
                install_path="services/sora",
                status="active",
                config={
                    "fal_api_key": "",
                    "margin_multiplier": 0.3,
                    "prices": {
                        "4s": 0.50,
                        "8s": 1.00,
                        "12s": 1.50,
                    },
                    "gallery_channel_id": "",
                    "gallery_enabled": False,
                },
                features=["text_to_video", "image_to_video"],
                permissions=["balance.deduct", "storage.upload"],
                menu_order=25,
            )
            session.add(service)
        
        await session.commit()
        print("Service 'sora' installed successfully!")


async def uninstall():
    """Remove Sora service from database"""
    await db_manager.init()
    
    async with get_db() as session:
        result = await session.execute(
            select(Service).where(Service.id == "sora")
        )
        service = result.scalar_one_or_none()
        
        if service:
            await session.delete(service)
            await session.commit()
            print("Service 'sora' uninstalled successfully!")
        else:
            print("Service 'sora' not found.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        asyncio.run(uninstall())
    else:
        asyncio.run(install())
