from abc import ABC, abstractmethod

class BaseLLM(ABC):
    @abstractmethod
    async def resume(self, query: str) -> str:
        ...

    @abstractmethod
    async def recomendation(self, query: str) -> str:
        ...

    @abstractmethod
    async def consultation(self, query: str) -> str:
        ...
