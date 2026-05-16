# import pytest_asyncio
# from httpx import ASGITransport, AsyncClient

# from app.db.redis import close_redis, connect_redis
# from app.db.session import engine
# from app.main import app


# @pytest_asyncio.fixture
# async def client():
#     await connect_redis()

#     transport = ASGITransport(app=app)

#     async with AsyncClient(
#         transport=transport,
#         base_url="http://testserver",
#     ) as test_client:
#         yield test_client

#     await close_redis()
#     await engine.dispose()











import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.base import Base
from app.db.redis import close_redis, connect_redis
from app.db.session import engine
from app.main import app
from app.models import User  # noqa: F401


@pytest_asyncio.fixture
async def client():
    await connect_redis()

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as test_client:
        yield test_client

    await close_redis()
    await engine.dispose()