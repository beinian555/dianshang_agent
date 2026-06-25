from app.agents.llm_provider import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing. Returns structured data matching the expected schema."""

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: dict | None = None,
    ) -> dict:
        return {}

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        return ""
