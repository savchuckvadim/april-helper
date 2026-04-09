import logging
import os
import tempfile
import time
from typing import Any

import httpx
from faster_whisper import WhisperModel

from src.core.queue.task_store import QueueTaskStoreService
from src.modules.transcription.model.dto import TranscriptionRequestDto


class TranscriptionService:
    _model: WhisperModel | None = None
    _task_store = QueueTaskStoreService("transcription")
    _logger = logging.getLogger("TranscriptionService")

    @classmethod
    def _get_model(cls) -> WhisperModel:
        if cls._model is None:
            model_size = os.getenv("WHISPER_MODEL_SIZE", "medium")
            device = os.getenv("WHISPER_DEVICE", "cpu")
            compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

            cls._logger.info(
                "Loading faster-whisper model size=%s device=%s compute_type=%s",
                model_size,
                device,
                compute_type,
            )
            cls._model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
            )
        return cls._model

    @classmethod
    def create_task_id(cls) -> str:
        return f"transcribe_{int(time.time() * 1000)}"

    @classmethod
    async def create_task(cls, task_id: str) -> None:
        await cls._task_store.set_task(task_id, {"taskId": task_id, "status": "started"})

    @classmethod
    async def get_task(cls, task_id: str) -> dict[str, Any]:
        return await cls._task_store.get_task(task_id)

    @classmethod
    async def process_task(cls, payload: dict[str, Any]) -> None:
        task_id = payload["taskId"]
        dto = TranscriptionRequestDto(**{key: value for key, value in payload.items() if key != "taskId"})

        await cls._task_store.update_task(task_id, status="processing", error=None)
        try:
            text, language, detected_duration, chunks = await cls._transcribe_from_url(
                task_id,
                dto.fileUrl,
                dto.fileName,
            )
            await cls._task_store.update_task(
                task_id,
                text=text,
                chunks=chunks,
            )

            transcription_id = None
            store_error = None
            try:
                transcription_id = await cls._send_to_store(
                    dto=dto,
                    text=text,
                    duration=dto.duration or str(detected_duration),
                    language=language,
                )
            except Exception as exc:
                store_error = str(exc)
                cls._logger.exception("Failed to send transcription result to store taskId=%s", task_id)

            await cls._task_store.update_task(
                task_id,
                status="done" if store_error is None else "error",
                text=text,
                chunks=chunks,
                transcriptionId=transcription_id,
                error=store_error,
            )
        except Exception as exc:
            cls._logger.exception("Transcription job failed taskId=%s", task_id)
            await cls._task_store.update_task(
                task_id,
                status="error",
                error=str(exc),
            )

    @classmethod
    def _build_chunk(cls, segment: Any) -> dict[str, Any] | None:
        chunk_text = segment.text.strip()
        if not chunk_text:
            return None
        return {
            "start": float(segment.start),
            "end": float(segment.end),
            "text": chunk_text,
        }

    @classmethod
    def _transcribe_file(cls, tmp_path: str):
        model = cls._get_model()
        return model.transcribe(tmp_path, beam_size=5)

    @classmethod
    async def _transcribe_from_url(
        cls,
        task_id: str,
        file_url: str,
        file_name: str,
    ) -> tuple[str, str, float, list[dict[str, Any]]]:
        suffix = os.path.splitext(file_name or "")[1]
        cls._logger.info("Downloading audio from url for fileName=%s", file_name)

        async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
            resp = await client.get(file_url)
            resp.raise_for_status()
            data = resp.content

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            tmp.write(data)

        try:
            cls._logger.info("Starting whisper transcription for temp file %s", tmp_path)
            segments, info = cls._transcribe_file(tmp_path)
            chunk_list: list[dict[str, Any]] = []
            text_parts: list[str] = []

            for index, segment in enumerate(segments, start=1):
                chunk = cls._build_chunk(segment)
                if chunk is None:
                    continue
                chunk_list.append(chunk)
                text_parts.append(chunk["text"])

                # Store partial results while whisper is still processing so polling can show progress.
                await cls._task_store.update_task(
                    task_id,
                    status="processing",
                    text=" ".join(text_parts).strip(),
                    chunks=chunk_list,
                )
                cls._logger.info(
                    "Task %s: chunk %s [%0.2f-%0.2f] captured",
                    task_id,
                    index,
                    chunk["start"],
                    chunk["end"],
                )

            text = " ".join(text_parts).strip()
            cls._logger.info("Task %s: transcription complete with %s chunks", task_id, len(chunk_list))
            return text, info.language, info.duration, chunk_list
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
