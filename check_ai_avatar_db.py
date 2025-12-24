import asyncio
from core.database.connection import db_manager
from sqlalchemy import select, text

async def check():
    await db_manager.init()
    
    async with db_manager.session() as session:
        # Check service status
        result = await session.execute(
            text("SELECT id, name, status, last_error FROM services WHERE id = 'ai_avatar'")
        )
        row = result.fetchone()
        
        if row:
            print(f"AI Avatar in DB:")
            print(f"  ID: {row[0]}")
            print(f"  Name: {row[1]}")
            print(f"  Status: {row[2]}")
            print(f"  Last Error: {row[3]}")
        else:
            print("AI Avatar NOT FOUND in database!")
        
        # Check all services
        result = await session.execute(
            text("SELECT id, status FROM services ORDER BY id")
        )
        print("\nAll services:")
        for row in result:
            print(f"  {row[0]}: {row[1]}")

asyncio.run(check())
