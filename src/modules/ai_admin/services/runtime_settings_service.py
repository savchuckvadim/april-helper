from dataclasses import dataclass
from pathlib import Path
from fastapi import HTTPException

from src.modules.ai.model.prompts import RECOMMENDATION_SYSTEM_PROMPT, RESUME_SYSTEM_PROMPT
from src.modules.ai_admin.model.dto import PromptKind
from src.modules.ai_admin.services.domain_storage_service import DomainStorageService
from src.modules.ai_admin.services.prompt_validation_service import PromptValidationService


@dataclass
class RuntimeConfig:
    source: str
    prompt: str
    retrive_root: Path
    retrive_paths: list[str]
    content_hash: str
    issues: list[dict[str, str]]


class RuntimeSettingsService:
    def __init__(self) -> None:
        self.storage = DomainStorageService()

    def resolve(self, domain: str | None, kind: PromptKind, use_portal_settings: bool) -> RuntimeConfig:
        if not use_portal_settings or not domain:
            default_prompt = RESUME_SYSTEM_PROMPT if kind == "resume" else RECOMMENDATION_SYSTEM_PROMPT
            _, hash_value, _ = self.storage.read_prompt("default", kind, fallback_to_default=True)
            return RuntimeConfig(
                source="default",
                prompt=default_prompt,
                retrive_root=Path("retrive_data").resolve(),
                retrive_paths=[],
                content_hash=hash_value,
                issues=[],
            )

        retrive_root = self.storage.get_retrive_root(domain, kind)
        try:
            prompt, hash_value, _ = self.storage.read_prompt(domain, kind, fallback_to_default=False)
        except HTTPException:
            default_prompt = RESUME_SYSTEM_PROMPT if kind == "resume" else RECOMMENDATION_SYSTEM_PROMPT
            _, fallback_hash, _ = self.storage.read_prompt("default", kind, fallback_to_default=True)
            return RuntimeConfig(
                source="default_missing_portal",
                prompt=default_prompt,
                retrive_root=Path("retrive_data").resolve(),
                retrive_paths=[],
                content_hash=fallback_hash,
                issues=[{"tag": "prompt", "path": "prompt.txt", "reason": "Prompt not found for domain"}],
            )
        if not self.storage.has_documents(domain, kind):
            default_prompt = RESUME_SYSTEM_PROMPT if kind == "resume" else RECOMMENDATION_SYSTEM_PROMPT
            _, fallback_hash, _ = self.storage.read_prompt("default", kind, fallback_to_default=True)
            return RuntimeConfig(
                source="default_missing_retrive",
                prompt=default_prompt,
                retrive_root=Path("retrive_data").resolve(),
                retrive_paths=[],
                content_hash=fallback_hash,
                issues=[{"tag": "retrive", "path": "retrive", "reason": "No retrive documents for domain"}],
            )
        issues = PromptValidationService.validate_prompt_references(prompt, retrive_root)
        if issues:
            default_prompt = RESUME_SYSTEM_PROMPT if kind == "resume" else RECOMMENDATION_SYSTEM_PROMPT
            _, fallback_hash, _ = self.storage.read_prompt("default", kind, fallback_to_default=True)
            return RuntimeConfig(
                source="default_invalid_portal",
                prompt=default_prompt,
                retrive_root=Path("retrive_data").resolve(),
                retrive_paths=[],
                content_hash=fallback_hash,
                issues=issues,
            )

        retrive_paths = PromptValidationService.extract_valid_relative_paths(prompt)
        return RuntimeConfig(
            source="portal",
            prompt=prompt,
            retrive_root=retrive_root,
            retrive_paths=retrive_paths,
            content_hash=hash_value,
            issues=[],
        )

