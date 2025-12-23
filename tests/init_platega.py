"""Initialize Platega payment provider in database"""

import asyncio
import sys

sys.stdout.reconfigure(encoding="utf-8")

from core.database import get_db, db_manager
from core.database.models import PaymentProvider
from sqlalchemy import select


async def init_platega():
    """Add Platega provider to database"""
    await db_manager.init()
    await db_manager.create_tables()

    async with get_db() as session:
        result = await session.execute(
            select(PaymentProvider).where(PaymentProvider.id == "platega")
        )
        existing = result.scalar_one_or_none()

        if existing:
            print("✅ Platega provider already exists")
            print(f"   Active: {existing.is_active}")
            print(f"   Currencies: {existing.currencies}")
            return

        provider = PaymentProvider(
            id="platega",
            name="СБП (Platega)",
            icon="🏦",
            is_active=True,
            currencies=["RUB"],
            config={},
            fee_percent=0,
            min_amount=50,
            max_amount=100000,
            sort_order=2,
            description="Оплата по СБП через Platega",
        )
        session.add(provider)

        print("✅ Platega provider created!")
        print(f"   ID: {provider.id}")
        print(f"   Currencies: {provider.currencies}")


if __name__ == "__main__":
    print("=== Platega Initialization ===\n")
    asyncio.run(init_platega())
