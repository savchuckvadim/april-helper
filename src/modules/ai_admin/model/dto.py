from typing import Literal

from pydantic import BaseModel, Field


PromptKind = Literal["resume", "recomendation"]


class PromptGetResponseDto(BaseModel):
    domain: str
    kind: PromptKind
    source: str
    prompt: str
    contentHash: str
    updatedAt: float | None = None


class PromptUpdateRequestDto(BaseModel):
    prompt: str = Field(min_length=1)


class PromptValidationIssueDto(BaseModel):
    tag: str
    path: str
    reason: str


class PromptUpdateResponseDto(BaseModel):
    status: str
    validationPassed: bool
    issues: list[PromptValidationIssueDto] = Field(default_factory=list)
    contentHash: str | None = None


class DomainTreeNodeDto(BaseModel):
    name: str
    path: str
    type: Literal["dir", "file"]
    size: int | None = None
    children: list["DomainTreeNodeDto"] = Field(default_factory=list)


class DomainTreeResponseDto(BaseModel):
    domain: str
    root: DomainTreeNodeDto

