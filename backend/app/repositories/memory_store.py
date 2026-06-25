"""In-memory data store implementing StoreBase. MVP default backend."""

from app.schemas.product import Product
from app.schemas.competitor import CompetitorProduct
from app.schemas.review import Review
from app.schemas.report import AnalysisReport
from app.schemas.analysis import WeeklyMetrics
from app.schemas.project import Project
from app.schemas.job import AnalysisJob
from app.schemas.llm_log import LLMCallLog
from app.repositories.base import StoreBase


class MemoryStore(StoreBase):
    def __init__(self):
        self.products: dict[str, Product] = {}
        self.competitors: dict[str, list[CompetitorProduct]] = {}
        self.reviews: dict[str, list[Review]] = {}
        self.reports: dict[str, AnalysisReport] = {}
        self.weekly_metrics: dict[str, dict[str, WeeklyMetrics]] = {}
        self.projects: dict[str, Project] = {}
        self.analysis_jobs: dict[str, AnalysisJob] = {}
        self.llm_logs: list[LLMCallLog] = []

    # ── Seed ──

    async def seed_beauty_data(self) -> dict:
        from app.seed.beauty_products import MAIN_PRODUCT
        from app.seed.beauty_competitors import ALL_COMPETITORS
        from app.seed.beauty_reviews import NEGATIVE_REVIEWS
        from app.seed.beauty_weekly_metrics import LAST_WEEK, THIS_WEEK

        pid = MAIN_PRODUCT.id
        self.products[pid] = MAIN_PRODUCT
        self.competitors[pid] = ALL_COMPETITORS
        self.reviews[pid] = NEGATIVE_REVIEWS
        self.weekly_metrics[pid] = {
            "last_week": LAST_WEEK,
            "this_week": THIS_WEEK,
        }
        return {
            "product_id": pid,
            "competitor_count": len(ALL_COMPETITORS),
            "review_count": len(NEGATIVE_REVIEWS),
        }

    # ── Product ──

    async def get_product(self, product_id: str) -> Product | None:
        return self.products.get(product_id)

    async def set_product(self, product_id: str, product: Product) -> None:
        self.products[product_id] = product

    # ── Competitors ──

    async def get_competitors(self, product_id: str) -> list[CompetitorProduct]:
        return self.competitors.get(product_id, [])

    async def set_competitors(self, product_id: str, competitors: list[CompetitorProduct]) -> None:
        self.competitors[product_id] = competitors

    # ── Reviews ──

    async def get_reviews(self, product_id: str) -> list[Review]:
        return self.reviews.get(product_id, [])

    async def set_reviews(self, product_id: str, reviews: list[Review]) -> None:
        self.reviews[product_id] = reviews

    # ── Weekly metrics ──

    async def get_weekly_metrics(self, product_id: str) -> dict[str, WeeklyMetrics]:
        return self.weekly_metrics.get(product_id, {})

    async def set_weekly_metrics(self, product_id: str, metrics: dict[str, WeeklyMetrics]) -> None:
        self.weekly_metrics[product_id] = metrics

    # ── Reports ──

    async def save_report(self, report: AnalysisReport) -> None:
        self.reports[report.id] = report

    async def get_report(self, report_id: str) -> AnalysisReport | None:
        return self.reports.get(report_id)

    # ── Projects ──

    async def create_project(self, project: Project) -> Project:
        self.projects[project.id] = project
        return project

    async def get_project(self, project_id: str) -> Project | None:
        return self.projects.get(project_id)

    async def list_projects(self) -> list[Project]:
        return list(self.projects.values())

    async def add_report_to_project(self, project_id: str, report: AnalysisReport) -> None:
        project = self.projects.get(project_id)
        if project:
            project.reports.append(report)
            await self.save_report(report)

    # ── Analysis Jobs ──

    async def save_analysis_job(self, job: AnalysisJob) -> None:
        self.analysis_jobs[job.id] = job

    async def get_analysis_job(self, job_id: str) -> AnalysisJob | None:
        return self.analysis_jobs.get(job_id)

    async def update_analysis_job(self, job_id: str, **kwargs) -> None:
        job = self.analysis_jobs.get(job_id)
        if job:
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            job.updated_at = __import__("datetime").datetime.now()

    # ── LLM Logs ──

    async def save_llm_log(self, log: LLMCallLog) -> None:
        self.llm_logs.append(log)


# Singleton for memory mode
memory_store = MemoryStore()
