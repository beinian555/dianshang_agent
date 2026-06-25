import os
import pytest
import pytest_asyncio

from app.repositories.store import store
from app.schemas.project import Project
from app.utils.csv_parser import (
    parse_product_csv,
    parse_competitors_csv,
    parse_reviews_csv,
    parse_metrics_csv,
)

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "sample_data", "beauty_serum")


def read_sample(filename: str) -> str:
    path = os.path.join(SAMPLE_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestProjectAnalysisFlow:

    @pytest_asyncio.fixture
    async def project(self):
        project = Project(
            name="test-beauty-analysis",
            category="beauty_skincare",
            platform="mock_tmall",
        )
        await store.create_project(project)
        return project

    async def _import_all_data(self, project: Project):
        product_id = f"{project.id}-product"
        await store.set_product(product_id, parse_product_csv(read_sample("product.csv"), product_id))
        await store.set_competitors(product_id, parse_competitors_csv(read_sample("competitors.csv"), product_id))
        await store.set_reviews(product_id, parse_reviews_csv(read_sample("reviews.csv"), product_id))
        await store.set_weekly_metrics(product_id, parse_metrics_csv(read_sample("metrics.csv")))

    @pytest.mark.asyncio
    async def test_full_project_analysis_flow(self, project):
        await self._import_all_data(project)

        from app.agents.orchestrator import AnalysisOrchestrator
        from app.schemas.product import CreateAnalysisRequest

        product_id = f"{project.id}-product"
        request = CreateAnalysisRequest(
            product_url="https://mock.shop/product/beauty-serum-main",
            competitor_urls=[
                "https://mock.shop/product/competitor-a",
                "https://mock.shop/product/competitor-b",
                "https://mock.shop/product/competitor-c",
            ],
            category="beauty_skincare",
            platform="mock_tmall",
            use_seed_data=False,
        )

        orchestrator = AnalysisOrchestrator(project_id=product_id)
        report = await orchestrator.run(request)

        assert report.status == "completed"
        assert report.scores.total_score > 0
        assert len(report.competitor_insights) == 3
        assert len(report.review_clusters) >= 5
        assert len(report.title_suggestions) == 3
        assert len(report.image_copy_suggestions) == 5
        assert len(report.detail_page_structure) == 9
        assert len(report.faq_items) >= 8
        assert len(report.ad_material_suggestions) == 4
        assert report.weekly_report is not None
        assert len(report.markdown_report) > 100

    @pytest.mark.asyncio
    async def test_project_report_has_evidence(self, project):
        await self._import_all_data(project)

        from app.agents.orchestrator import AnalysisOrchestrator
        from app.schemas.product import CreateAnalysisRequest

        product_id = f"{project.id}-product"
        request = CreateAnalysisRequest(
            product_url="https://mock.shop/product/beauty-serum-main",
            competitor_urls=[],
            category="beauty_skincare",
            platform="mock_tmall",
            use_seed_data=False,
        )

        orchestrator = AnalysisOrchestrator(project_id=product_id)
        report = await orchestrator.run(request)

        assert "评分依据" in report.markdown_report
        # Each dimension should have a reason
        assert report.scores.title_search.reason
        assert report.scores.review_risk.reason
        assert report.scores.review_health.reason

    @pytest.mark.asyncio
    async def test_project_report_saved_to_store(self, project):
        await self._import_all_data(project)

        from app.agents.orchestrator import AnalysisOrchestrator
        from app.schemas.product import CreateAnalysisRequest

        product_id = f"{project.id}-product"
        request = CreateAnalysisRequest(
            product_url="https://mock.shop/product/beauty-serum-main",
            competitor_urls=[],
            category="beauty_skincare",
            platform="mock_tmall",
            use_seed_data=False,
        )

        orchestrator = AnalysisOrchestrator(project_id=product_id)
        report = await orchestrator.run(request)

        await store.add_report_to_project(project.id, report)
        saved_project = await store.get_project(project.id)
        assert saved_project is not None
        assert len(saved_project.reports) >= 1
        assert saved_project.reports[-1].id == report.id

    @pytest.mark.asyncio
    async def test_review_scores_are_split(self, project):
        """Verify review_risk and review_health are separate dimensions."""
        await self._import_all_data(project)

        from app.agents.orchestrator import AnalysisOrchestrator
        from app.schemas.product import CreateAnalysisRequest

        product_id = f"{project.id}-product"
        request = CreateAnalysisRequest(
            product_url="https://mock.shop/product/beauty-serum-main",
            competitor_urls=[],
            category="beauty_skincare",
            platform="mock_tmall",
            use_seed_data=False,
        )

        orchestrator = AnalysisOrchestrator(project_id=product_id)
        report = await orchestrator.run(request)

        # review_risk: higher = more risky
        # review_health: higher = healthier
        # With the seed data having high-risk clusters, these should differ
        assert report.scores.review_risk.score != report.scores.review_health.score
        # Risk score should be > 0 (there ARE high-risk clusters)
        assert report.scores.review_risk.score > 0
        # Health score should be < 100 (not perfect health)
        assert report.scores.review_health.score < 100
