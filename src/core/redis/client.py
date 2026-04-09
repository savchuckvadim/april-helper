from typing import Any

import aioredis

from src.core.config.settings import settings


_redis_client: Any | None = None


async def get_redis_client() -> Any:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def close_redis_client() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None

