import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AnalysisJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisJob(BaseModel):
    id: str = Field(default_factory=lambda: f"job-{uuid.uuid4().hex[:8]}")
    project_id: str
    status: AnalysisJobStatus = AnalysisJobStatus.PENDING
    progress: int = Field(default=0, ge=0, le=100)
    current_step: str | None = None
    report_id: str | None = None
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class AnalysisJobResponse(AnalysisJob):
    pass
