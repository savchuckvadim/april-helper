import json
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from src.core.redis import close_redis_client, get_redis_client


JobHandler = Callable[[dict[str, Any]], Awaitable[None]]


class QueueWorker:
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.handlers: dict[str, dict[str, JobHandler]] = {}

    @staticmethod
    def _queue_key(queue_name: str) -> str:
        return f"queue:{queue_name}"

    def register_handler(self, queue_name: str, handler_id: str, handler: JobHandler) -> None:
        self.handlers.setdefault(queue_name, {})[handler_id] = handler

    async def run(self) -> None:
        if not self.handlers:
            raise RuntimeError("No queue handlers registered")

        queue_keys = [self._queue_key(queue_name) for queue_name in self.handlers]
        redis = await get_redis_client()
        self.logger.info("Queue worker started for queues: %s", ", ".join(self.handlers))

        try:
            while True:
                item = await redis.brpop(queue_keys, timeout=5)
                if not item:
                    continue

                queue_key, raw_envelope = item
                queue_name = queue_key.split("queue:", 1)[1]
                envelope = json.loads(raw_envelope)
                handler_id = envelope["handlerId"]
                payload = envelope["payload"]

                queue_handlers = self.handlers.get(queue_name, {})
                handler = queue_handlers.get(handler_id)
                if handler is None:
                    self.logger.error("No handler registered for queue=%s handler=%s", queue_name, handler_id)
                    continue

                try:
                    await handler(payload)
                except Exception:
                    self.logger.exception("Queue job failed for queue=%s handler=%s", queue_name, handler_id)
        finally:
            await close_redis_client()

