"""
Diagnose AI Avatar Service Issues
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


async def diagnose():
    """Diagnose AI Avatar service issues"""
    
    logger.info("=== AI Avatar Service Diagnostics ===\n")
    
    # 1. Check database
    logger.info("1. Checking database...")
    from core.database.connection import db_manager
    await db_manager.init()
    
    async with get_db() as session:
        result = await session.execute(
            select(Service).where(Service.id == "ai_avatar")
        )
        service = result.scalar_one_or_none()
        
        if not service:
            logger.error("❌ AI Avatar NOT found in database!")
            logger.info("   Run: python services/ai_avatar/install_service.py")
            return False
        
        logger.success(f"✅ Service found in database")
        logger.info(f"   Status: {service.status}")
        logger.info(f"   Install path: {service.install_path}")
        
        if service.last_error:
            logger.error(f"   Last error: {service.last_error}")
    
    # 2. Check module import
    logger.info("\n2. Testing module import...")
    try:
        from services.ai_avatar import service as ai_avatar_module
        logger.success("✅ Module imported successfully")
    except Exception as e:
        logger.error(f"❌ Failed to import module: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 3. Check service class
    logger.info("\n3. Testing service class...")
    try:
        from services.ai_avatar.service import AIAvatarService
        from core.plugins.core_api import CoreAPI
        
        core_api = CoreAPI("ai_avatar")
        service_instance = AIAvatarService(core_api)
        logger.success("✅ Service class instantiated")
        
        # Test info
        info = service_instance.info
        logger.info(f"   ID: {info.id}")
        logger.info(f"   Name: {info.name}")
        logger.info(f"   Icon: {info.icon}")
        
    except Exception as e:
        logger.error(f"❌ Failed to instantiate service: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. Check service registry
    logger.info("\n4. Checking service registry...")
    try:
        from core.plugins.registry import service_registry
        await service_registry.init()
        
        active_services = service_registry.get_active()
        logger.info(f"   Active services: {len(active_services)}")
        
        ai_avatar_loaded = False
        for svc in active_services:
            logger.info(f"   - {svc.info.id}: {svc.info.name}")
            if svc.info.id == "ai_avatar":
                ai_avatar_loaded = True
        
        if ai_avatar_loaded:
            logger.success("✅ AI Avatar loaded in registry")
        else:
            logger.error("❌ AI Avatar NOT loaded in registry")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to check registry: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Test menu items
    logger.info("\n5. Testing menu items...")
    try:
        from core.plugins.base_service import UserServiceDTO
        
        menu_items = service_instance.get_user_menu_items(1, UserServiceDTO())
        logger.info(f"   Menu items: {len(menu_items)}")
        for item in menu_items:
            logger.info(f"   - {item.text} -> {item.callback}")
        
        if menu_items:
            logger.success("✅ Menu items generated")
        else:
            logger.warning("⚠️  No menu items")
            
    except Exception as e:
        logger.error(f"❌ Failed to get menu items: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    logger.info("\n=== Diagnostics Complete ===")
    logger.success("✅ All checks passed! AI Avatar should work.")
    return True


if __name__ == "__main__":
    result = asyncio.run(diagnose())
    sys.exit(0 if result else 1)
