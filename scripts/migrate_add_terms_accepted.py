#!/usr/bin/env python3
"""
Migration: Add terms_accepted fields to users table
Date: 2024-12-24
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


async def migrate():
    """Apply migration to add terms_accepted fields"""
    
    logger.info("Starting migration: add terms_accepted fields")
    
    # Initialize database
    await db_manager.init()
    logger.info("Database initialized")
    
    async with get_db() as session:
        try:
            # Check if columns already exist
            result = await session.execute(
                text("PRAGMA table_info(users)")
            )
            columns = [row[1] for row in result.fetchall()]
            
            if 'terms_accepted' in columns:
                logger.info("Column 'terms_accepted' already exists, skipping migration")
                return
            
            # Add terms_accepted column
            logger.info("Adding column 'terms_accepted'...")
            await session.execute(
                text("ALTER TABLE users ADD COLUMN terms_accepted BOOLEAN DEFAULT 0")
            )
            
            # Add terms_accepted_at column
            logger.info("Adding column 'terms_accepted_at'...")
            await session.execute(
                text("ALTER TABLE users ADD COLUMN terms_accepted_at TIMESTAMP NULL")
            )
            
            # Update existing users to have terms_accepted = TRUE (grandfather clause)
            logger.info("Updating existing users...")
            await session.execute(
                text("""
                    UPDATE users 
                    SET terms_accepted = 1, 
                        terms_accepted_at = created_at 
                    WHERE terms_accepted = 0
                """)
            )
            
            logger.info("Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(migrate())
