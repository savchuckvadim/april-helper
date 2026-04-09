import asyncio
import logging

from dotenv import load_dotenv

from src.core.queue.worker import QueueWorker
from src.modules.transcription.queue.handlers import register_transcription_handlers


async def main() -> None:
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    worker = QueueWorker()
    register_transcription_handlers(worker)
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())

