"""Transparent LLM logging wrapper — intercepts generate_json/text calls and logs to the store."""

import time
import logging

from app.agents.llm_provider import LLMProvider
from app.repositories.factory import get_store
from app.schemas.llm_log import LLMCallLog

logger = logging.getLogger(__name__)


class LoggingLLMProvider(LLMProvider):
    """Wraps an LLMProvider, logging every call to the store."""

    def __init__(self, inner: LLMProvider, agent_name: str = ""):
        self._inner = inner
        self._agent_name = agent_name
        self._model = getattr(inner, "model", None)
        self._provider_name = inner.__class__.__name__

    async def generate_json(
        self, system_prompt: str, user_prompt: str, schema: dict | None = None
    ) -> dict:
        return await self._call("generate_json", system_prompt, user_prompt, schema)

    async def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        result = await self._call("generate_text", system_prompt, user_prompt)
        return result

    async def _call(
        self,
        call_type: str,
        system_prompt: str,
        user_prompt: str,
        schema: dict | None = None,
    ):
        start = time.perf_counter()
        success = True
        error_message = None
        try:
            if call_type == "generate_json":
                result = await self._inner.generate_json(system_prompt, user_prompt, schema)
            else:
                result = await self._inner.generate_text(system_prompt, user_prompt)
        except Exception as e:
            success = False
            error_message = str(e)

        latency_ms = (time.perf_counter() - start) * 1000

        log = LLMCallLog(
            agent_name=self._agent_name,
            provider=self._provider_name,
            model=self._model,
            call_type=call_type,
            latency_ms=round(latency_ms, 2),
            success=success,
            fallback_used=False,
            error_message=error_message,
            prompt_length=len(system_prompt) + len(user_prompt),
        )
        await get_store().save_llm_log(log)
        logger.info(
            "%s (%s) %.0fms %s len=%d",
            self._agent_name,
            call_type,
            round(latency_ms, 2),
            success,
            error_message,
        )

        if not success:
            raise e

        return result
