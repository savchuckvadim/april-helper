import json
from typing import Any

from src.core.config.settings import settings
from src.core.redis import get_redis_client


class QueueTaskStoreService:
    def __init__(self, namespace: str):
        self.namespace = namespace
        self.ttl_seconds = settings.queue_task_ttl_seconds

    def _task_key(self, task_id: str) -> str:
        return f"queue:task:{self.namespace}:{task_id}"

    async def set_task(self, task_id: str, data: dict[str, Any]) -> None:
        redis = await get_redis_client()
        await redis.set(self._task_key(task_id), json.dumps(data), ex=self.ttl_seconds)

    async def get_task(self, task_id: str) -> dict[str, Any]:
        redis = await get_redis_client()
        raw = await redis.get(self._task_key(task_id))
        if not raw:
            return {"taskId": task_id, "status": "not_found"}
        return json.loads(raw)

    async def update_task(self, task_id: str, **updates: Any) -> dict[str, Any]:
        current = await self.get_task(task_id)
        current.update(updates)
        await self.set_task(task_id, current)
        return current

