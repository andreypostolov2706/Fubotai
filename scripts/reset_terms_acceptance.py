#!/usr/bin/env python3
"""
Reset terms acceptance for testing
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from core.database import get_db
from core.database.connection import db_manager
from loguru import logger


async def reset_terms():
    """Reset terms_accepted for all users or specific user"""
    
    logger.info("Resetting terms acceptance...")
    
    # Initialize database
    await db_manager.init()
    logger.info("Database initialized")
    
    async with get_db() as session:
        try:
            # Option 1: Reset for all users
            result = await session.execute(
                text("""
                    UPDATE users 
                    SET terms_accepted = 0, 
                        terms_accepted_at = NULL
                """)
            )
            
            logger.info(f"Reset terms_accepted for all users")
            
            # Show count
            count_result = await session.execute(
                text("SELECT COUNT(*) FROM users WHERE terms_accepted = 0")
            )
            count = count_result.scalar()
            logger.info(f"Total users with terms_accepted = FALSE: {count}")
            
        except Exception as e:
            logger.error(f"Reset failed: {e}")
            raise


async def reset_specific_user(telegram_id: int):
    """Reset terms acceptance for specific user by telegram_id"""
    
    logger.info(f"Resetting terms acceptance for user {telegram_id}...")
    
    # Initialize database
    await db_manager.init()
    logger.info("Database initialized")
    
    async with get_db() as session:
        try:
            result = await session.execute(
                text("""
                    UPDATE users 
                    SET terms_accepted = 0, 
                        terms_accepted_at = NULL
                    WHERE telegram_id = :telegram_id
                """),
                {"telegram_id": telegram_id}
            )
            
            if result.rowcount > 0:
                logger.info(f"Reset terms_accepted for user {telegram_id}")
            else:
                logger.warning(f"User {telegram_id} not found")
            
        except Exception as e:
            logger.error(f"Reset failed: {e}")
            raise


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Reset specific user by telegram_id
        telegram_id = int(sys.argv[1])
        asyncio.run(reset_specific_user(telegram_id))
    else:
        # Reset all users
        asyncio.run(reset_terms())
