from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from app.core.config import settings

redis_client: Redis | None = None


async def connect_redis() -> None:
    global redis_client

    redis_client = Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )

    await redis_client.ping()


async def close_redis() -> None:
    if redis_client:
        await redis_client.aclose()


async def get_redis() -> AsyncGenerator[Redis]:
    if not redis_client:
        raise RuntimeError("Redis client is not connected")

    yield redis_client