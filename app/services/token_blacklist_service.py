from redis.asyncio import Redis

BLACKLIST_PREFIX = "blacklist:access:"


async def blacklist_access_token(
    redis: Redis,
    token_jti: str,
    expires_in_seconds: int,
) -> None:
    key = f"{BLACKLIST_PREFIX}{token_jti}"

    await redis.set(
        key,
        "revoked",
        ex=expires_in_seconds,
    )


async def is_access_token_blacklisted(
    redis: Redis,
    token_jti: str,
) -> bool:
    key = f"{BLACKLIST_PREFIX}{token_jti}"

    value = await redis.get(key)

    return value is not None