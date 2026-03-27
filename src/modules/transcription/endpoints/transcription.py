from fastapi import APIRouter, BackgroundTasks

from src.api.http.exceptions import AppException
from src.modules.transcription.model.dto import (
    TranscriptionRequestDto,
    TranscriptionResponseDto,
)
from src.modules.transcription.services.transcription_service import (
    TranscriptionService,
)

router = APIRouter(prefix="/transcription", tags=["Транскрибация"])


@router.post("", response_model=TranscriptionResponseDto)
async def start_transcription(
    dto: TranscriptionRequestDto,
    background_tasks: BackgroundTasks,
):
    try:
        task_id = TranscriptionService.create_task()
        background_tasks.add_task(TranscriptionService.process_task, task_id, dto)
        return TranscriptionResponseDto(taskId=task_id, status="started")
    except Exception as exc:
        raise AppException(
            status_code=500,
            detail=f"failed to start transcription: {exc}",
        ) from exc


@router.get("/{task_id}", response_model=TranscriptionResponseDto)
async def get_transcription_result(task_id: str):
    task = TranscriptionService.get_task(task_id)
    return TranscriptionResponseDto(
        taskId=task.get("taskId", task_id),
        status=task.get("status", "not_found"),
        text=task.get("text"),
        error=task.get("error"),
        transcriptionId=task.get("transcriptionId"),
    )
