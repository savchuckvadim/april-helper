import json
import time
from typing import Any

from src.core.redis import get_redis_client


class QueueDispatcherService:
    @staticmethod
    def _queue_key(queue_name: str) -> str:
        return f"queue:{queue_name}"

    async def dispatch(self, queue_name: str, handler_id: str, payload: dict[str, Any]) -> None:
        envelope = {
            "queue": queue_name,
            "handlerId": handler_id,
            "payload": payload,
            "enqueuedAt": time.time(),
        }
        redis = await get_redis_client()
        await redis.lpush(self._queue_key(queue_name), json.dumps(envelope))

