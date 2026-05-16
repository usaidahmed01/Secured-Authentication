import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.redis import close_redis, connect_redis
from app.db.session import engine
from app.main import app


@pytest_asyncio.fixture
async def client():
    await connect_redis()

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client

    await close_redis()
    await engine.dispose()