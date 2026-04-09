import hashlib
import io
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from src.modules.ai.model.prompts import RECOMMENDATION_SYSTEM_PROMPT, RESUME_SYSTEM_PROMPT
from src.modules.ai_admin.model.dto import DomainTreeNodeDto, PromptKind


class DomainStorageService:
    ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx"}

    def __init__(self) -> None:
        self.base_dir = Path(os.getenv("AI_ADMIN_STORAGE_ROOT", "portal_data")).resolve()
        self.max_files_per_request = int(os.getenv("MAX_FILES_PER_REQUEST", "20"))
        self.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "25"))
        self.max_domain_storage_mb = int(os.getenv("MAX_DOMAIN_STORAGE_MB", "500"))
        self.base_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sanitize_domain(domain: str) -> str:
        safe = domain.strip().lower()
        if not safe or "/" in safe or "\\" in safe or ".." in safe:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid domain value")
        return safe

    def get_domain_root(self, domain: str) -> Path:
        safe_domain = self.sanitize_domain(domain)
        root = (self.base_dir / safe_domain).resolve()
        root.mkdir(parents=True, exist_ok=True)
        return root

    def get_kind_root(self, domain: str, kind: PromptKind) -> Path:
        root = self.get_domain_root(domain) / kind
        (root / "retrive").mkdir(parents=True, exist_ok=True)
        return root

    def get_retrive_root(self, domain: str, kind: PromptKind) -> Path:
        return self.get_kind_root(domain, kind) / "retrive"

    def get_prompt_path(self, domain: str, kind: PromptKind) -> Path:
        return self.get_kind_root(domain, kind) / "prompt.txt"

    def has_documents(self, domain: str, kind: PromptKind) -> bool:
        retrive_root = self.get_retrive_root(domain, kind)
        for file_path in retrive_root.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.ALLOWED_EXTENSIONS:
                return True
        return False

    @staticmethod
    def _content_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _total_domain_size(self, domain: str) -> int:
        root = self.get_domain_root(domain)
        total = 0
        for p in root.rglob("*"):
            if p.is_file():
                total += p.stat().st_size
        return total

    def _safe_subpath(self, root: Path, rel_path: str | None) -> Path:
        raw = (rel_path or "").strip().strip("/")
        target = (root / raw).resolve()
        try:
            target.relative_to(root.resolve())
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path traversal is not allowed") from exc
        return target

    def read_prompt(self, domain: str, kind: PromptKind, fallback_to_default: bool = True) -> tuple[str, str, float | None]:
        prompt_path = self.get_prompt_path(domain, kind)
        if prompt_path.exists():
            text = prompt_path.read_text(encoding="utf-8")
            return text, self._content_hash(text), prompt_path.stat().st_mtime

        if fallback_to_default:
            text = RESUME_SYSTEM_PROMPT if kind == "resume" else RECOMMENDATION_SYSTEM_PROMPT
            return text, self._content_hash(text), None

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")

    def write_prompt(self, domain: str, kind: PromptKind, prompt: str) -> tuple[str, float]:
        prompt_path = self.get_prompt_path(domain, kind)
        prompt_path.write_text(prompt, encoding="utf-8")
        return self._content_hash(prompt), prompt_path.stat().st_mtime

    def build_tree(self, domain: str) -> DomainTreeNodeDto:
        root = self.get_domain_root(domain)
        return self._build_tree_node(root, root)

    def _build_tree_node(self, path: Path, root: Path) -> DomainTreeNodeDto:
        rel_path = "." if path == root else str(path.relative_to(root)).replace("\\", "/")
        if path.is_file():
            return DomainTreeNodeDto(name=path.name, path=rel_path, type="file", size=path.stat().st_size)

        children = sorted(path.iterdir(), key=lambda item: (item.is_file(), item.name.lower()))
        return DomainTreeNodeDto(
            name=path.name,
            path=rel_path,
            type="dir",
            children=[self._build_tree_node(child, root) for child in children],
        )

    async def save_files(
        self,
        domain: str,
        kind: PromptKind,
        files: list[UploadFile],
        target_path: str | None,
        overwrite: bool,
    ) -> dict[str, object]:
        if not files:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files uploaded")
        if len(files) > self.max_files_per_request:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Too many files: max {self.max_files_per_request} per request",
            )

        retrive_root = self.get_retrive_root(domain, kind)
        final_target = self._safe_subpath(retrive_root, target_path)
        final_target.mkdir(parents=True, exist_ok=True)

        domain_size_before = self._total_domain_size(domain)
        total_upload_size = 0
        saved: list[str] = []

        with tempfile.TemporaryDirectory() as tmp:
            tmp_target = Path(tmp) / "upload"
            tmp_target.mkdir(parents=True, exist_ok=True)

            for upload in files:
                if not upload.filename:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required")
                ext = Path(upload.filename).suffix.lower()
                if ext not in self.ALLOWED_EXTENSIONS:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Unsupported extension {ext}. Allowed: {sorted(self.ALLOWED_EXTENSIONS)}",
                    )
                data = await upload.read()
                size = len(data)
                if size > self.max_file_size_mb * 1024 * 1024:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File {upload.filename} exceeds max size {self.max_file_size_mb} MB",
                    )
                total_upload_size += size
                (tmp_target / Path(upload.filename).name).write_bytes(data)
                saved.append(Path(upload.filename).name)

            if domain_size_before + total_upload_size > self.max_domain_storage_mb * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Domain storage exceeds limit {self.max_domain_storage_mb} MB",
                )

            if overwrite:
                for item in list(final_target.iterdir()):
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink(missing_ok=True)

            for item in tmp_target.iterdir():
                dst = final_target / item.name
                if dst.exists() and dst.is_dir():
                    shutil.rmtree(dst)
                if dst.exists() and dst.is_file():
                    dst.unlink(missing_ok=True)
                shutil.move(str(item), str(dst))

        return {"saved": saved, "targetPath": str(final_target.relative_to(retrive_root)).replace("\\", "/")}

    def delete_path(self, domain: str, kind: PromptKind, rel_path: str) -> None:
        retrive_root = self.get_retrive_root(domain, kind)
        target = self._safe_subpath(retrive_root, rel_path)
        if not target.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")
        if target.is_dir():
            shutil.rmtree(target)
            return
        target.unlink(missing_ok=True)

    def build_zip(self, domain: str, kind: PromptKind, rel_path: str | None = None) -> tuple[bytes, str]:
        retrive_root = self.get_retrive_root(domain, kind)
        target = self._safe_subpath(retrive_root, rel_path)
        if not target.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Path not found")

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            if target.is_file():
                archive.write(target, arcname=target.name)
            else:
                for file_path in target.rglob("*"):
                    if file_path.is_file():
                        arc_name = str(file_path.relative_to(target)).replace("\\", "/")
                        archive.write(file_path, arcname=arc_name)
        buffer.seek(0)
        filename = f"{domain}-{kind}-{(rel_path or 'retrive').strip('/').replace('/', '_')}.zip"
        return buffer.getvalue(), filename

