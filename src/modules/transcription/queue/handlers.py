from src.core.queue import QueueNames, QueueWorker
from src.modules.transcription.queue.transcribe_job_handler_id import TranscribeJobHandlerId
from src.modules.transcription.services.transcription_service import TranscriptionService


def register_transcription_handlers(worker: QueueWorker) -> None:
    worker.register_handler(
        QueueNames.TRANSCRIBE_AUDIO,
        TranscribeJobHandlerId.TRANSCRIBE,
        TranscriptionService.process_task,
    )

