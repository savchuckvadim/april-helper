from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Literal
from src.modules.ai.usecases.llm_service_manager import LLMUseCase

router = APIRouter(prefix="/ai", tags=["Помошник ИИ"])


class ResumeRequest(BaseModel):
    query: str
    model: Literal["openai", "gigachat", "ollama", "fake"] = Field(..., description="LLM provider to use")



@router.post("/resume")
async def resume(request: ResumeRequest):
    case = LLMUseCase(request.model)
    text = await case.resume(request.query)
    if text:
        return JSONResponse({"result": text, "resultCode": 0}, status_code=200)
    else:
        return JSONResponse({"error": "no text"}, status_code=500)




@router.post("/recomendation")
async def recomendation(request: ResumeRequest):
    case = LLMUseCase(request.model)
    text = await case.recomendation(request.query)
    if text:
        return JSONResponse({"result": text, "resultCode": 0}, status_code=200)
    else:
        return JSONResponse({"error": "no text"}, status_code=500)
