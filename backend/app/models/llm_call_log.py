from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from app.models.base import Base


class LLMCallLogModel(Base):
    __tablename__ = "llm_call_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_name = Column(String, default="")
    provider = Column(String, default="")
    model = Column(String, nullable=True)
    call_type = Column(String, default="generate_json")
    latency_ms = Column(Float, default=0.0)
    success = Column(Boolean, default=True)
    fallback_used = Column(Boolean, default=False)
    error_message = Column(String, nullable=True)
    prompt_length = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
