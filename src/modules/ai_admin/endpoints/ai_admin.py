from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import StreamingResponse

from src.modules.ai_admin.model.dto import (
    DomainTreeResponseDto,
    PromptGetResponseDto,
    PromptKind,
    PromptUpdateRequestDto,
    PromptUpdateResponseDto,
)
from src.modules.ai_admin.services.auth_service import admin_auth_dependency
from src.modules.ai_admin.services.domain_storage_service import DomainStorageService
from src.modules.ai_admin.services.prompt_validation_service import PromptValidationService

router = APIRouter(prefix="/ai-admin", tags=["AI Admin"])
storage = DomainStorageService()


@router.get("/{domain}/tree", response_model=DomainTreeResponseDto, dependencies=[Depends(admin_auth_dependency)])
async def get_domain_tree(domain: str):
    return DomainTreeResponseDto(domain=domain, root=storage.build_tree(domain))


@router.get(
    "/{domain}/prompt/{kind}",
    response_model=PromptGetResponseDto,
    dependencies=[Depends(admin_auth_dependency)],
)
async def get_prompt(domain: str, kind: PromptKind):
    prompt, content_hash, updated_at = storage.read_prompt(domain, kind, fallback_to_default=True)
    source = "portal" if updated_at else "default"
    return PromptGetResponseDto(
        domain=domain,
        kind=kind,
        source=source,
        prompt=prompt,
        contentHash=content_hash,
        updatedAt=updated_at,
    )


@router.put(
    "/{domain}/prompt/{kind}",
    response_model=PromptUpdateResponseDto,
    dependencies=[Depends(admin_auth_dependency)],
)
async def update_prompt(domain: str, kind: PromptKind, body: PromptUpdateRequestDto):
    retrive_root = storage.get_retrive_root(domain, kind)
    issues = PromptValidationService.validate_prompt_references(body.prompt, retrive_root)
    if issues:
        return PromptUpdateResponseDto(status="validation_error", validationPassed=False, issues=issues)

    content_hash, _ = storage.write_prompt(domain, kind, body.prompt)
    return PromptUpdateResponseDto(
        status="ok",
        validationPassed=True,
        issues=[],
        contentHash=content_hash,
    )


@router.post("/{domain}/upload/{kind}", dependencies=[Depends(admin_auth_dependency)])
async def upload_documents(
    domain: str,
    kind: PromptKind,
    files: list[UploadFile] = File(...),
    targetPath: str | None = Query(default=None),
    overwrite: bool = Query(default=False),
):
    result = await storage.save_files(domain, kind, files, targetPath, overwrite)
    return {"status": "ok", **result}


@router.get("/{domain}/download/{kind}", dependencies=[Depends(admin_auth_dependency)])
async def download_documents(domain: str, kind: PromptKind, path: str | None = Query(default=None)):
    content, filename = storage.build_zip(domain, kind, path)
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(iter([content]), media_type="application/zip", headers=headers)


@router.delete("/{domain}/path/{kind}", dependencies=[Depends(admin_auth_dependency)])
async def delete_path(domain: str, kind: PromptKind, path: str = Query(...)):
    storage.delete_path(domain, kind, path)
    return {"status": "ok"}

