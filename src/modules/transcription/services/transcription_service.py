import os
import tempfile
from typing import Any
import time

from faster_whisper import WhisperModel
import httpx

from src.modules.transcription.model.dto import TranscriptionRequestDto


class TranscriptionService:
    _model: WhisperModel | None = None
    _tasks: dict[str, dict[str, Any]] = {}

    @classmethod
    def _get_model(cls) -> WhisperModel:
        if cls._model is None:
            model_size = os.getenv("WHISPER_MODEL_SIZE", "medium")
            device = os.getenv("WHISPER_DEVICE", "cpu")
            compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

            cls._model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
            )
        return cls._model

    @classmethod
    def create_task(cls) -> str:
        task_id = f"transcribe_{int(time.time() * 1000)}"
        cls._tasks[task_id] = {"taskId": task_id, "status": "started"}
        return task_id

    @classmethod
    def get_task(cls, task_id: str) -> dict[str, Any]:
        if task_id not in cls._tasks:
            return {"taskId": task_id, "status": "not_found"}
        return cls._tasks[task_id]

    @classmethod
    async def process_task(cls, task_id: str, dto: TranscriptionRequestDto) -> None:
        cls._tasks[task_id]["status"] = "processing"
        try:
            text, language, detected_duration = await cls._transcribe_from_url(
                dto.fileUrl,
                dto.fileName,
            )
            cls._tasks[task_id].update(
                {
                    "status": "done",
                    "text": text,
                }
            )

            transcription_id = await cls._send_to_store(
                dto=dto,
                text=text,
                duration=dto.duration or str(detected_duration),
                language=language,
            )
            if transcription_id is not None:
                cls._tasks[task_id]["transcriptionId"] = transcription_id
        except Exception as exc:
            cls._tasks[task_id].update(
                {
                    "status": "error",
                    "error": str(exc),
                }
            )

    @classmethod
    async def _transcribe_from_url(cls, file_url: str, file_name: str) -> tuple[str, str, float]:
        suffix = os.path.splitext(file_name or "")[1]

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.get(file_url)
            resp.raise_for_status()
            data = resp.content

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            tmp.write(data)

        try:
            model = cls._get_model()
            segments, info = model.transcribe(tmp_path, beam_size=5)
            text = " ".join(segment.text.strip() for segment in segments).strip()
            return text, info.language, info.duration
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    @classmethod
    async def _send_to_store(
        cls,
        dto: TranscriptionRequestDto,
        text: str,
        duration: str,
        language: str,
    ) -> int | None:
        store_url = os.getenv(
            "NEST_TRANSCRIPTION_STORE_URL",
            "http://host.docker.internal:3000/transcription-store",
        )
        payload = {
            "provider": f"faster-whisper:{language}",
            "activityId": dto.activityId,
            "fileId": dto.fileId,
            "inComment": False,
            "status": "done",
            "text": text,
            "symbolsCount": str(len(text)),
            "price": "0",
            "duration": str(duration),
            "domain": dto.domain,
            "userResult": "{}",
            "userId": dto.userId,
            "userName": dto.userName,
            "app": dto.appName,
            "entityType": dto.entityType,
            "entityId": dto.entityId,
            "entityName": dto.entityName,
            "department": dto.department,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(store_url, json=payload)
            response.raise_for_status()
            body = response.json() if response.content else {}

        raw_id = body.get("id")
        if raw_id is None:
            return None
        try:
            return int(raw_id)
        except (TypeError, ValueError):
            return None
