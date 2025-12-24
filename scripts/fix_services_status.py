"""
Fix services status - reset all error services to active
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from core.database import get_db
from core.database.models import Service
from sqlalchemy import select, update


async def fix_services():
    """Reset all error services to active"""
    
    from core.database.connection import db_manager
    await db_manager.init()
    
    async with get_db() as session:
        # Get all services with error status
        result = await session.execute(
            select(Service).where(Service.status == "error")
        )
        error_services = result.scalars().all()
        
        if not error_services:
            logger.info("✅ No services with error status found")
            return
        
        logger.info(f"Found {len(error_services)} services with error status:")
        for service in error_services:
            logger.info(f"  - {service.id}: {service.last_error}")
        
        # Reset status to active and clear errors
        await session.execute(
            update(Service)
            .where(Service.status == "error")
            .values(
                status="active",
                last_error=None,
                error_count=0
            )
        )
        
        await session.commit()
        
        logger.success(f"✅ Fixed {len(error_services)} services!")
        logger.info("Restart the bot: supervisorctl restart fubotai")


if __name__ == "__main__":
    asyncio.run(fix_services())
