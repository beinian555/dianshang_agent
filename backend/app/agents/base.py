from abc import ABC, abstractmethod
from typing import Any

from app.agents.llm_provider import LLMProvider


class BaseAgent(ABC):
    name: str

    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    @abstractmethod
    async def run(self, input_data: Any) -> Any:
        pass
