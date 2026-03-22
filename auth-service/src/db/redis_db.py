import time
from typing import Optional
from redis.asyncio import Redis

redis: Optional[Redis] = None


async def get_redis() -> Redis:
    return redis


async def revoke_access_token(jti: str, exp: int):
    ttl = exp - int(time.time())
    if ttl > 0:
        await redis.setex(f"access:{jti}", ttl, "revoked")


async def is_access_token_revoked(jti: str) -> bool:
    return await redis.exists(f"access:{jti}") == 1


async def store_refresh_token(jti: str, user_id: str, exp: int):
    ttl = exp - int(time.time())
    if ttl > 0:
        token_key = f"refresh:{jti}"
        await redis.setex(token_key, ttl, user_id)

        user_tokens_key = f"user_tokens:{user_id}"
        await redis.sadd(user_tokens_key, token_key)
        await redis.expire(user_tokens_key, ttl)


async def is_refresh_token_valid(jti: str) -> bool:
    return await redis.exists(f"refresh:{jti}") == 1


async def revoke_refresh_token(jti: str):
    token_key = f"refresh:{jti}"
    user_id = await redis.get(token_key)

    if user_id:
        user_tokens_key = f"user_tokens:{user_id}"
        await redis.srem(user_tokens_key, token_key)
        if await redis.scard(user_tokens_key) == 0:
            await redis.delete(user_tokens_key)

    await redis.delete(token_key)


async def revoke_all_refresh_tokens(user_id: str):
    """
    Logout from all devices
    """
    user_tokens_key = f"user_tokens:{user_id}"
    
    token_keys = await redis.smembers(user_tokens_key)
    
    if not token_keys:
        return
    
    pipe = redis.pipeline()
    for token_key in token_keys:
        pipe.delete(token_key)
    pipe.delete(user_tokens_key)
    
    await pipe.execute()
