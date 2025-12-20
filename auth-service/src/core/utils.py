import time

from db.redis_db import get_redis


async def add_token_to_redis(jti: str, expires_at: int):
    """Добавляем jti в redis с TTL = expires_at - now"""
    temp_redis = await get_redis()
    ttl = max(0, expires_at - int(time.time()))
    if ttl <= 0:
        return
    key = f"blacklist:{jti}"
    await temp_redis.set(key, "true", ex=ttl)


async def is_token_blacklisted(jti: str) -> bool:
    temp_redis = await get_redis()
    key = f"blacklist:{jti}"
    return await temp_redis.exists(key) == 1
