"""Tests for store operations that work with both MemoryStore and PostgresStore.

Run with:
    STORE_BACKEND=memory   pytest tests/test_postgres_store.py -v   (uses singleton)
    STORE_BACKEND=postgres pytest tests/test_postgres_store.py -v   (requires DATABASE_URL)
"""

import pytest
import pytest_asyncio

from app.repositories.factory import get_store
from app.repositories.base import StoreBase
from app.schemas.project import Project
from app.schemas.product import Product
from app.schemas.competitor import CompetitorProduct
from app.schemas.review import Review
from app.schemas.analysis import WeeklyMetrics
from app.schemas.report import AnalysisReport
from app.schemas.job import AnalysisJob, AnalysisJobStatus
from app.schemas.llm_log import LLMCallLog


@pytest_asyncio.fixture
async def store() -> StoreBase:
    return get_store()


@pytest.mark.asyncio
class TestProjectCRUD:

    async def test_create_and_get_project(self, store: StoreBase):
        project = Project(name="test-pg-create", category="beauty_skincare", platform="mock_tmall")
        created = await store.create_project(project)
        assert created.id == project.id

        fetched = await store.get_project(project.id)
        assert fetched is not None
        assert fetched.name == "test-pg-create"

    async def test_list_projects(self, store: StoreBase):
        p1 = Project(name="list-1", category="beauty", platform="tmall")
        p2 = Project(name="list-2", category="sunscreen", platform="jd")
        await store.create_project(p1)
        await store.create_project(p2)

        projects = await store.list_projects()
        ids = [p.id for p in projects]
        assert p1.id in ids
        assert p2.id in ids

    async def test_get_nonexistent_project(self, store: StoreBase):
        result = await store.get_project("nonexistent-id")
        assert result is None


@pytest.mark.asyncio
class TestProductDataCRUD:

    async def test_product_roundtrip(self, store: StoreBase):
        project = Project(name="product-test", category="beauty", platform="tmall")
        await store.create_project(project)

        product_id = f"{project.id}-product"
        product = Product(
            id=product_id,
            platform="mock_tmall",
            category="beauty_skincare",
            url="https://mock.shop/product/test",
            title="Test Product",
            brand="TestBrand",
            price=99,
            specs=["30ml", "white"],
            selling_points=["hydrating", "brightening"],
            ingredients=["water", "niacinamide"],
            main_image_texts=["main image copy"],
            detail_sections=["section 1"],
            target_users=["oily skin"],
            usage_scenarios=["daily"],
        )

        await store.set_product(product_id, product)
        fetched = await store.get_product(product_id)
        assert fetched is not None
        assert fetched.title == "Test Product"
        assert fetched.price == 99

    async def test_product_not_found(self, store: StoreBase):
        result = await store.get_product("no-such-product")
        assert result is None


@pytest.mark.asyncio
class TestCompetitorsCRUD:

    async def test_competitors_roundtrip(self, store: StoreBase):
        project = Project(name="comp-test", category="beauty", platform="tmall")
        await store.create_project(project)

        product_id = f"{project.id}-product"
        comps = [
            CompetitorProduct(
                id="comp-1", product_id=product_id,
                url="https://mock.shop/c1", title="Comp 1",
                selling_points=["sp1"], main_image_texts=["img1"],
                detail_sections=["s1"], promotions=[], weakness_hints=[],
            ),
            CompetitorProduct(
                id="comp-2", product_id=product_id,
                url="https://mock.shop/c2", title="Comp 2",
                selling_points=["sp2"], main_image_texts=["img2"],
                detail_sections=["s2"], promotions=[], weakness_hints=[],
            ),
        ]

        await store.set_competitors(product_id, comps)
        fetched = await store.get_competitors(product_id)
        assert len(fetched) == 2

    async def test_competitors_empty(self, store: StoreBase):
        result = await store.get_competitors("no-product")
        assert result == []


@pytest.mark.asyncio
class TestReviewsCRUD:

    async def test_reviews_roundtrip(self, store: StoreBase):
        project = Project(name="review-test", category="beauty", platform="tmall")
        await store.create_project(project)

        product_id = f"{project.id}-product"
        reviews = [
            Review(id="r-1", product_id=product_id, source="tmall", rating=2,
                   content="Caused irritation", tags=["sensitive", "irritation"]),
            Review(id="r-2", product_id=product_id, source="jd", rating=3,
                   content="Just ok", tags=["expectation"]),
        ]

        await store.set_reviews(product_id, reviews)
        fetched = await store.get_reviews(product_id)
        assert len(fetched) == 2
        assert fetched[0].rating == 2

    async def test_reviews_empty(self, store: StoreBase):
        result = await store.get_reviews("no-product")
        assert result == []


@pytest.mark.asyncio
class TestWeeklyMetricsCRUD:

    async def test_metrics_roundtrip(self, store: StoreBase):
        project = Project(name="metrics-test", category="beauty", platform="tmall")
        await store.create_project(project)

        product_id = f"{project.id}-product"
        last_week = WeeklyMetrics(
            impressions=1000, clicks=100, ctr=10.0, orders=20,
            conversion_rate=20.0, refund_rate=1.0, ad_spend=500,
            revenue=2000, roi=4.0,
        )
        this_week = WeeklyMetrics(
            impressions=1200, clicks=120, ctr=10.0, orders=25,
            conversion_rate=20.8, refund_rate=0.8, ad_spend=550,
            revenue=2500, roi=4.5,
        )

        await store.set_weekly_metrics(product_id, {"last_week": last_week, "this_week": this_week})
        fetched = await store.get_weekly_metrics(product_id)
        assert "last_week" in fetched
        assert fetched["last_week"].impressions == 1000
        assert fetched["this_week"].roi == 4.5

    async def test_metrics_empty(self, store: StoreBase):
        result = await store.get_weekly_metrics("no-product")
        assert result == {}


@pytest.mark.asyncio
class TestReportCRUD:

    async def test_save_and_get_report(self, store: StoreBase):
        project = Project(name="report-test", category="beauty", platform="tmall")
        await store.create_project(project)

        report = AnalysisReport(
            id="rpt-test-001",
            product_id=f"{project.id}-product",
            status="completed",
            summary="Test summary",
        )
        await store.add_report_to_project(project.id, report)

        fetched = await store.get_report("rpt-test-001")
        assert fetched is not None
        assert fetched.status == "completed"

    async def test_report_not_found(self, store: StoreBase):
        result = await store.get_report("no-such-report")
        assert result is None


@pytest.mark.asyncio
class TestAnalysisJobCRUD:

    async def test_job_lifecycle(self, store: StoreBase):
        job = AnalysisJob(project_id="proj-001")
        await store.save_analysis_job(job)

        fetched = await store.get_analysis_job(job.id)
        assert fetched is not None
        assert fetched.status == AnalysisJobStatus.PENDING

        await store.update_analysis_job(
            job.id,
            status=AnalysisJobStatus.RUNNING.value,
            progress=50,
            current_step="review_clustering",
        )
        updated = await store.get_analysis_job(job.id)
        assert updated.status == AnalysisJobStatus.RUNNING
        assert updated.progress == 50
        assert updated.current_step == "review_clustering"

        await store.update_analysis_job(
            job.id,
            status=AnalysisJobStatus.COMPLETED.value,
            progress=100,
            report_id="rpt-final",
        )
        completed = await store.get_analysis_job(job.id)
        assert completed.status == AnalysisJobStatus.COMPLETED
        assert completed.report_id == "rpt-final"

    async def test_job_not_found(self, store: StoreBase):
        result = await store.get_analysis_job("no-such-job")
        assert result is None


@pytest.mark.asyncio
class TestLLMLogCRUD:

    async def test_save_llm_log(self, store: StoreBase):
        log = LLMCallLog(
            agent_name="TestAgent",
            provider="MockLLMProvider",
            model="mock-v1",
            call_type="generate_json",
            latency_ms=123.45,
            success=True,
            prompt_length=500,
        )
        await store.save_llm_log(log)
        # MemoryStore appends to list, PostgresStore persists to DB
        # Both should not raise

    async def test_save_failed_llm_log(self, store: StoreBase):
        log = LLMCallLog(
            agent_name="FailingAgent",
            provider="MockLLMProvider",
            call_type="generate_text",
            latency_ms=50.0,
            success=False,
            fallback_used=True,
            error_message="timeout",
        )
        await store.save_llm_log(log)
        # Should not raise


@pytest.mark.asyncio
class TestSeed:

    async def test_seed_beauty_data(self, store: StoreBase):
        result = await store.seed_beauty_data()
        assert "product_id" in result
        assert result["competitor_count"] == 3
        assert result["review_count"] == 8

        product = await store.get_product(result["product_id"])
        assert product is not None
        assert product.brand == "LumiSkin"
