from fastapi import APIRouter

from src.api.http.exceptions import AppException
from src.core.queue import QueueDispatcherService, QueueNames
from src.modules.transcription.model.dto import (
    TranscriptionRequestDto,
    TranscriptionResponseDto,
)
from src.modules.transcription.queue import TranscribeJobHandlerId
from src.modules.transcription.services.transcription_service import (
    TranscriptionService,
)

router = APIRouter(prefix="/transcription", tags=["Транскрибация"])
queue = QueueDispatcherService()


@router.post("", response_model=TranscriptionResponseDto)
async def start_transcription(dto: TranscriptionRequestDto):
    try:
        task_id = TranscriptionService.create_task_id()
        await TranscriptionService.create_task(task_id)
        await queue.dispatch(
            QueueNames.TRANSCRIBE_AUDIO,
            TranscribeJobHandlerId.TRANSCRIBE,
            {
                "taskId": task_id,
                **dto.model_dump(),
            },
        )
        return TranscriptionResponseDto(taskId=task_id, status="started")
    except Exception as exc:
        raise AppException(
            status_code=500,
            detail=f"failed to start transcription: {exc}",
        ) from exc


@router.get("/{task_id}", response_model=TranscriptionResponseDto)
async def get_transcription_result(task_id: str):
    task = await TranscriptionService.get_task(task_id)
    return TranscriptionResponseDto(
        taskId=task.get("taskId", task_id),
        status=task.get("status", "not_found"),
        text=task.get("text"),
        chunks=task.get("chunks"),
        error=task.get("error"),
        transcriptionId=task.get("transcriptionId"),
    )
