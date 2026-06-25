"""Abstract store base for MemoryStore and PostgresStore."""

from abc import ABC, abstractmethod

from app.schemas.product import Product
from app.schemas.competitor import CompetitorProduct
from app.schemas.review import Review
from app.schemas.report import AnalysisReport
from app.schemas.analysis import WeeklyMetrics
from app.schemas.project import Project
from app.schemas.job import AnalysisJob
from app.schemas.llm_log import LLMCallLog


class StoreBase(ABC):

    # ── Seed ──

    @abstractmethod
    async def seed_beauty_data(self) -> dict: ...

    # ── Product ──

    @abstractmethod
    async def get_product(self, product_id: str) -> Product | None: ...

    @abstractmethod
    async def set_product(self, product_id: str, product: Product) -> None: ...

    # ── Competitors ──

    @abstractmethod
    async def get_competitors(self, product_id: str) -> list[CompetitorProduct]: ...

    @abstractmethod
    async def set_competitors(self, product_id: str, competitors: list[CompetitorProduct]) -> None: ...

    # ── Reviews ──

    @abstractmethod
    async def get_reviews(self, product_id: str) -> list[Review]: ...

    @abstractmethod
    async def set_reviews(self, product_id: str, reviews: list[Review]) -> None: ...

    # ── Weekly metrics ──

    @abstractmethod
    async def get_weekly_metrics(self, product_id: str) -> dict[str, WeeklyMetrics]: ...

    @abstractmethod
    async def set_weekly_metrics(self, product_id: str, metrics: dict[str, WeeklyMetrics]) -> None: ...

    # ── Reports ──

    @abstractmethod
    async def save_report(self, report: AnalysisReport) -> None: ...

    @abstractmethod
    async def get_report(self, report_id: str) -> AnalysisReport | None: ...

    # ── Projects ──

    @abstractmethod
    async def create_project(self, project: Project) -> Project: ...

    @abstractmethod
    async def get_project(self, project_id: str) -> Project | None: ...

    @abstractmethod
    async def list_projects(self) -> list[Project]: ...

    @abstractmethod
    async def add_report_to_project(self, project_id: str, report: AnalysisReport) -> None: ...

    # ── Analysis Jobs ──

    @abstractmethod
    async def save_analysis_job(self, job: AnalysisJob) -> None: ...

    @abstractmethod
    async def get_analysis_job(self, job_id: str) -> AnalysisJob | None: ...

    @abstractmethod
    async def update_analysis_job(self, job_id: str, **kwargs) -> None: ...

    # ── LLM Logs ──

    @abstractmethod
    async def save_llm_log(self, log: LLMCallLog) -> None: ...
