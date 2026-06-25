import json
import logging
import re
from typing import Optional

import httpx

from app.agents.llm_provider import LLMProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class RealLLMProvider(LLMProvider):

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.api_key = api_key or settings.llm_api_key
        self.base_url = (base_url or settings.openai_base_url).rstrip("/")
        self.model = model or settings.llm_model or "gpt-4o-mini"
        self.timeout = timeout or settings.llm_timeout

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: Optional[dict] = None,
    ) -> dict:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        body = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2048,
        }

        if schema:
            body["response_format"] = {"type": "json_object", "schema": schema}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers,
                json=body,
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"LLM API error {response.status_code}: {response.text[:500]}"
            )

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", content, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise ValueError(f"Failed to parse LLM JSON response: {content[:500]}")

    async def generate_text(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        body = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": 2048,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers,
                json=body,
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"LLM API error {response.status_code}: {response.text[:500]}"
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]
