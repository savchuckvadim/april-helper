import re
from pathlib import Path


PROMPT_REFERENCE_PATTERN = re.compile(r"\[\[(folder|path):([^\]]+)\]\]")


class PromptValidationService:
    @staticmethod
    def extract_references(prompt: str) -> list[tuple[str, str]]:
        refs: list[tuple[str, str]] = []
        for match in PROMPT_REFERENCE_PATTERN.finditer(prompt):
            ref_type = match.group(1)
            ref_path = match.group(2).strip().strip("/")
            refs.append((ref_type, ref_path))
        return refs

    @staticmethod
    def extract_valid_relative_paths(prompt: str) -> list[str]:
        paths: list[str] = []
        for _, ref_path in PromptValidationService.extract_references(prompt):
            cleaned = ref_path.strip().strip("/")
            if cleaned and cleaned not in paths:
                paths.append(cleaned)
        return paths

    @staticmethod
    def validate_prompt_references(prompt: str, retrive_root: Path) -> list[dict[str, str]]:
        issues: list[dict[str, str]] = []
        for ref_type, ref_path in PromptValidationService.extract_references(prompt):
            path = (retrive_root / ref_path).resolve()
            try:
                path.relative_to(retrive_root.resolve())
            except ValueError:
                issues.append(
                    {"tag": ref_type, "path": ref_path, "reason": "Path traversal is not allowed"}
                )
                continue

            if not path.exists():
                issues.append({"tag": ref_type, "path": ref_path, "reason": "Referenced path does not exist"})
                continue
            if ref_type == "folder" and not path.is_dir():
                issues.append({"tag": ref_type, "path": ref_path, "reason": "Expected directory for folder tag"})
        return issues

