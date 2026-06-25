"""PostgreSQL-backed store implementing StoreBase."""

from sqlalchemy import select, update

from app.core.database import get_sessionmaker
from app.models.project import ProjectModel
from app.models.analysis_job import AnalysisJobModel
from app.models.llm_call_log import LLMCallLogModel
from app.repositories.base import StoreBase
from app.schemas.product import Product
from app.schemas.competitor import CompetitorProduct
from app.schemas.review import Review
from app.schemas.report import AnalysisReport
from app.schemas.analysis import WeeklyMetrics
from app.schemas.project import Project
from app.schemas.job import AnalysisJob
from app.schemas.llm_log import LLMCallLog


class PostgresStore(StoreBase):

    # ── Helpers ──

    def _project_to_model(self, project: Project) -> ProjectModel:
        return ProjectModel(
            id=project.id,
            name=project.name,
            category=project.category,
            platform=project.platform,
            product=project.product,
            competitors=project.competitors,
            reviews=project.reviews,
            weekly_metrics={k: v.model_dump(mode="json") if hasattr(v, 'model_dump') else v for k, v in project.weekly_metrics.items()} if project.weekly_metrics else None,
            reports=project.reports,
            status=project.status,
            created_at=project.created_at,
        )

    def _model_to_project(self, model: ProjectModel) -> Project:
        return Project(
            id=model.id,
            name=model.name,
            category=model.category,
            platform=model.platform,
            product=model.product,
            competitors=model.competitors or [],
            reviews=model.reviews or [],
            weekly_metrics=model.weekly_metrics or {},
            reports=model.reports or [],
            status=model.status,
            created_at=model.created_at,
        )

    # ── Seed ──

    async def seed_beauty_data(self) -> dict:
        from app.seed.beauty_products import MAIN_PRODUCT
        from app.seed.beauty_competitors import ALL_COMPETITORS
        from app.seed.beauty_reviews import NEGATIVE_REVIEWS
        from app.seed.beauty_weekly_metrics import LAST_WEEK, THIS_WEEK

        project = Project(
            id=f"project-beauty-seed",
            name="Beauty Seed",
            category="beauty_skincare",
            platform="mock_tmall",
            product=MAIN_PRODUCT,
            competitors=ALL_COMPETITORS,
            reviews=NEGATIVE_REVIEWS,
            weekly_metrics={"last_week": LAST_WEEK, "this_week": THIS_WEEK},
            status="seeded",
        )
        await self.create_project(project)
        return {
            "product_id": MAIN_PRODUCT.id,
            "competitor_count": len(ALL_COMPETITORS),
            "review_count": len(NEGATIVE_REVIEWS),
        }

    # ── Product ──

    async def get_product(self, product_id: str) -> Product | None:
        project = await self._get_project_by_product_id(product_id)
        return project.product if project else None

    async def set_product(self, product_id: str, product: Product) -> None:
        project_id = self._product_id_to_project_id(product_id)
        sm = get_sessionmaker()
        async with sm() as session:
            await session.execute(
                update(ProjectModel)
                .where(ProjectModel.id == project_id)
                .values(product=product)
            )
            await session.commit()

    # ── Competitors ──

    async def get_competitors(self, product_id: str) -> list[CompetitorProduct]:
        project = await self._get_project_by_product_id(product_id)
        return project.competitors if project else []

    async def set_competitors(self, product_id: str, competitors: list[CompetitorProduct]) -> None:
        project_id = self._product_id_to_project_id(product_id)
        sm = get_sessionmaker()
        async with sm() as session:
            await session.execute(
                update(ProjectModel)
                .where(ProjectModel.id == project_id)
                .values(competitors=competitors)
            )
            await session.commit()

    # ── Reviews ──

    async def get_reviews(self, product_id: str) -> list[Review]:
        project = await self._get_project_by_product_id(product_id)
        return project.reviews if project else []

    async def set_reviews(self, product_id: str, reviews: list[Review]) -> None:
        project_id = self._product_id_to_project_id(product_id)
        sm = get_sessionmaker()
        async with sm() as session:
            await session.execute(
                update(ProjectModel)
                .where(ProjectModel.id == project_id)
                .values(reviews=reviews)
            )
            await session.commit()

    # ── Weekly metrics ──

    async def get_weekly_metrics(self, product_id: str) -> dict[str, WeeklyMetrics]:
        project = await self._get_project_by_product_id(product_id)
        return project.weekly_metrics if project else {}

    async def set_weekly_metrics(self, product_id: str, metrics: dict[str, WeeklyMetrics]) -> None:
        project_id = self._product_id_to_project_id(product_id)
        sm = get_sessionmaker()
        serialized = {k: v.model_dump(mode="json") for k, v in metrics.items()}
        async with sm() as session:
            await session.execute(
                update(ProjectModel)
                .where(ProjectModel.id == project_id)
                .values(weekly_metrics=serialized)
            )
            await session.commit()

    # ── Reports ──

    async def save_report(self, report: AnalysisReport) -> None:
        sm = get_sessionmaker()
        project_id = self._product_id_to_project_id(report.product_id)
        async with sm() as session:
            stmt = select(ProjectModel).where(ProjectModel.id == project_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model:
                existing = model.reports or []
                if not any(r.id == report.id for r in existing):
                    existing.append(report)
                    model.reports = existing
                await session.commit()

    async def get_report(self, report_id: str) -> AnalysisReport | None:
        sm = get_sessionmaker()
        async with sm() as session:
            stmt = select(ProjectModel)
            result = await session.execute(stmt)
            for model in result.scalars():
                for r in (model.reports or []):
                    if r.id == report_id:
                        return r
        return None

    # ── Projects ──

    async def create_project(self, project: Project) -> Project:
        sm = get_sessionmaker()
        async with sm() as session:
            model = self._project_to_model(project)
            session.add(model)
            await session.commit()
            return project

    async def get_project(self, project_id: str) -> Project | None:
        sm = get_sessionmaker()
        async with sm() as session:
            stmt = select(ProjectModel).where(ProjectModel.id == project_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            return self._model_to_project(model) if model else None

    async def list_projects(self) -> list[Project]:
        sm = get_sessionmaker()
        async with sm() as session:
            stmt = select(ProjectModel).order_by(ProjectModel.created_at.desc())
            result = await session.execute(stmt)
            return [self._model_to_project(m) for m in result.scalars()]

    async def add_report_to_project(self, project_id: str, report: AnalysisReport) -> None:
        sm = get_sessionmaker()
        async with sm() as session:
            stmt = select(ProjectModel).where(ProjectModel.id == project_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model:
                existing = model.reports or []
                if not any(r.id == report.id for r in existing):
                    existing.append(report)
                    model.reports = existing
                await session.commit()

    # ── Analysis Jobs ──

    async def save_analysis_job(self, job: AnalysisJob) -> None:
        sm = get_sessionmaker()
        async with sm() as session:
            model = AnalysisJobModel(
                id=job.id,
                project_id=job.project_id,
                status=job.status.value if hasattr(job.status, 'value') else job.status,
                progress=job.progress,
                current_step=job.current_step,
                report_id=job.report_id,
                error_message=job.error_message,
                created_at=job.created_at,
                updated_at=job.updated_at,
            )
            session.add(model)
            await session.commit()

    async def get_analysis_job(self, job_id: str) -> AnalysisJob | None:
        sm = get_sessionmaker()
        async with sm() as session:
            stmt = select(AnalysisJobModel).where(AnalysisJobModel.id == job_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return AnalysisJob(
                id=model.id,
                project_id=model.project_id,
                status=model.status,
                progress=model.progress,
                current_step=model.current_step,
                report_id=model.report_id,
                error_message=model.error_message,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )

    async def update_analysis_job(self, job_id: str, **kwargs) -> None:
        from datetime import datetime
        sm = get_sessionmaker()
        async with sm() as session:
            values = {**kwargs, "updated_at": datetime.now()}
            await session.execute(
                update(AnalysisJobModel)
                .where(AnalysisJobModel.id == job_id)
                .values(**values)
            )
            await session.commit()

    # ── LLM Logs ──

    async def save_llm_log(self, log: LLMCallLog) -> None:
        sm = get_sessionmaker()
        async with sm() as session:
            model = LLMCallLogModel(
                agent_name=log.agent_name,
                provider=log.provider,
                model=log.model,
                call_type=log.call_type,
                latency_ms=log.latency_ms,
                success=log.success,
                fallback_used=log.fallback_used,
                error_message=log.error_message,
                prompt_length=log.prompt_length,
                created_at=log.created_at,
            )
            session.add(model)
            await session.commit()

    # ── Internal helpers ──

    async def _get_project_by_product_id(self, product_id: str) -> Project | None:
        project_id = self._product_id_to_project_id(product_id)
        return await self.get_project(project_id)

    @staticmethod
    def _product_id_to_project_id(product_id: str) -> str:
        if product_id.endswith("-product"):
            return product_id[:-8]
        return product_id
