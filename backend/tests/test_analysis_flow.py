import pytest
import pytest_asyncio

from app.agents.orchestrator import AnalysisOrchestrator
from app.schemas.product import CreateAnalysisRequest
from app.repositories.store import store


class TestAnalysisFlow:

    @pytest_asyncio.fixture(autouse=True)
    async def setup_seed(self):
        await store.seed_beauty_data()

    @pytest.mark.asyncio
    async def test_full_analysis_flow(self):
        request = CreateAnalysisRequest(
            product_url="https://mock.shop/product/beauty-serum-main",
            competitor_urls=[
                "https://mock.shop/product/competitor-a",
                "https://mock.shop/product/competitor-b",
                "https://mock.shop/product/competitor-c",
            ],
            category="beauty_skincare",
            platform="mock_tmall",
            use_seed_data=True,
        )

        orchestrator = AnalysisOrchestrator()
        report = await orchestrator.run(request)

        assert report.status == "completed"
        assert report.product_id == "beauty-main-001"
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
        assert "核心结论" in report.markdown_report
        assert "下周优化任务" in report.markdown_report
        assert "评分依据" in report.markdown_report
        # Verify new score structure
        assert report.scores.review_risk.score >= 0
        assert report.scores.review_health.score >= 0
        assert report.scores.title_search.reason != ""

    @pytest.mark.asyncio
    async def test_report_saved_to_store(self):
        request = CreateAnalysisRequest(
            product_url="https://mock.shop/product/beauty-serum-main",
            competitor_urls=["https://mock.shop/product/competitor-a"],
            category="beauty_skincare",
            platform="mock_tmall",
            use_seed_data=True,
        )

        orchestrator = AnalysisOrchestrator()
        report = await orchestrator.run(request)

        saved = await store.get_report(report.id)
        assert saved is not None
        assert saved.id == report.id
        assert saved.status == "completed"
