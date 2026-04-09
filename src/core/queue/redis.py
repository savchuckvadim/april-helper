from src.core.redis.client import close_redis_client, get_redis_client


async def get_redis():
    return await get_redis_client()


async def close_redis() -> None:
    await close_redis_client()

