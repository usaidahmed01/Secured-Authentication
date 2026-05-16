import asyncio

from app.db.base import Base
from app.db.session import engine
from app.models import User  # noqa: F401


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    print("Database tables created successfully")


asyncio.run(create_tables())