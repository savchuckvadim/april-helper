from src.modules.ai.services.gigachat_service import GigaChatService
from src.modules.ai.services.openai_service import OpenAIService
from src.modules.ai.services.fake_service import FakeService
from src.modules.ai.services.ollama_service import OllamaService

class LLMUseCase:
    def __init__(self, model: str):
        self.service = self._get_service(model)

    def _get_service(self, model: str):
        match model:
            case "gigachat":
                return GigaChatService()
            case "openai":
                return OpenAIService()
            case "ollama":
                return OllamaService()
            case "fake":
                return FakeService()
            case _:
                raise ValueError(f"❌ Unknown model: {model}")

    async def resume(self, query: str):
        return await self.service.resume(query)

    async def recomendation(self, query: str):
        return await self.service.recomendation(query)
