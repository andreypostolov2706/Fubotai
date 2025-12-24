"""
Check AI Avatar Service Installation
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from core.database import get_db
from core.database.models import Service
from sqlalchemy import select


async def check_service():
    """Check if AI Avatar service is installed"""
    
    from core.database.connection import db_manager
    await db_manager.init()
    
    async with get_db() as session:
        result = await session.execute(
            select(Service).where(Service.id == "ai_avatar")
        )
        service = result.scalar_one_or_none()
        
        if not service:
            logger.error("❌ AI Avatar service NOT found in database!")
            logger.info("Run: python services/ai_avatar/install_service.py")
            return False
        
        logger.success(f"✅ AI Avatar service found!")
        logger.info(f"   ID: {service.id}")
        logger.info(f"   Name: {service.name}")
        logger.info(f"   Status: {service.status}")
        logger.info(f"   Install path: {service.install_path}")
        logger.info(f"   Version: {service.version}")
        
        if service.status != "active":
            logger.warning(f"⚠️  Service status is '{service.status}', should be 'active'")
            logger.info("Fixing status...")
            service.status = "active"
            await session.commit()
            logger.success("✅ Status fixed!")
        
        if service.last_error:
            logger.error(f"❌ Last error: {service.last_error}")
        
        return True


if __name__ == "__main__":
    asyncio.run(check_service())
