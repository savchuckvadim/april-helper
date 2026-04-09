from fastapi import APIRouter
from src.modules.header import header_router
from src.modules.audio import audio_router
from src.modules.ai import ai_router
from src.modules.ai_admin import ai_admin_router
from src.modules.transcription import transcription_router


router = APIRouter(prefix="/helper")

router.include_router(router=header_router)
router.include_router(router=audio_router)
router.include_router(router=ai_router)
router.include_router(router=ai_admin_router)
router.include_router(router=transcription_router)

