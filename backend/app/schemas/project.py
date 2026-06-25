import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from app.schemas.product import Product
from app.schemas.competitor import CompetitorProduct
from app.schemas.review import Review
from app.schemas.analysis import WeeklyMetrics
from app.schemas.report import AnalysisReport


class Project(BaseModel):
    id: str = Field(default_factory=lambda: f"project-{uuid.uuid4().hex[:8]}")
    name: str
    category: str = "beauty_skincare"
    platform: str = "mock_tmall"
    product: Product | None = None
    competitors: list[CompetitorProduct] = Field(default_factory=list)
    reviews: list[Review] = Field(default_factory=list)
    weekly_metrics: dict[str, WeeklyMetrics] = Field(default_factory=dict)
    reports: list[AnalysisReport] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = "created"


class CreateProjectRequest(BaseModel):
    name: str
    category: str = "beauty_skincare"
    platform: str = "mock_tmall"


class ImportResult(BaseModel):
    project_id: str
    import_type: str
    success_count: int = 0
    failed_count: int = 0
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    preview: list[dict] = Field(default_factory=list)
