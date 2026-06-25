import os
import logging

from app.agents.llm_provider import LLMProvider
from app.agents.mock_llm import MockLLMProvider

logger = logging.getLogger(__name__)

_real_provider: LLMProvider | None = None


def get_llm_provider() -> LLMProvider:
    """Return the configured LLM provider based on LLM_PROVIDER env var.

    LLM_PROVIDER=mock (default) -> MockLLMProvider
    LLM_PROVIDER=real -> RealLLMProvider
    """
    provider_type = os.getenv("LLM_PROVIDER", "mock").strip().lower()

    if provider_type == "real":
        global _real_provider
        if _real_provider is None:
            from app.agents.real_llm import RealLLMProvider
            _real_provider = RealLLMProvider()
            logger.info("Using RealLLMProvider")
        return _real_provider

    return MockLLMProvider()
