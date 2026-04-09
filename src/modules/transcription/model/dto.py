from pydantic import BaseModel


class TranscriptionRequestDto(BaseModel):
    fileUrl: str
    fileName: str
    userId: str
    userName: str
    appName: str
    activityId: str
    fileId: str | int
    duration: str
    department: str
    entityType: str
    entityId: str | int
    entityName: str
    domain: str


class TranscriptionResponseDto(BaseModel):
    taskId: str
    status: str
    text: str | None = None
    error: str | None = None
    transcriptionId: int | None = None
