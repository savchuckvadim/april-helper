import os
from .base import BaseLLM
from src.modules.ai.services.openai_service import OpenAIService
from src.modules.ai.services.services.gigachat_service import GigaChatService


def get_llm_provider() -> BaseLLM:
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "gigachat":
        return GigaChatService()
    return OpenAIService()
