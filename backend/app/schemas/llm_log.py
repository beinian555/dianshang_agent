from datetime import datetime

from pydantic import BaseModel, Field


class LLMCallLog(BaseModel):
    id: int | None = None
    agent_name: str = ""
    provider: str = ""
    model: str | None = None
    call_type: str = "generate_json"
    latency_ms: float = 0.0
    success: bool = True
    fallback_used: bool = False
    error_message: str | None = None
    prompt_length: int | None = None
    created_at: datetime = Field(default_factory=datetime.now)
