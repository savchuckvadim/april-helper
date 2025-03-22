from fastapi import APIRouter
from src.modules.header import header_router
from src.modules.audio import audio_router
from src.modules.ai import ai_router


router = APIRouter(prefix="/helper")

router.include_router(router=header_router)
router.include_router(router=audio_router)
router.include_router(router=ai_router)

