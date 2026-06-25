import os
import pytest

from app.repositories.store import store
from app.schemas.project import Project
from app.utils.csv_parser import (
    parse_product_csv_with_validation,
    parse_competitors_csv_with_validation,
    parse_reviews_csv_with_validation,
    parse_metrics_csv_with_validation,
)

ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "sample_data")
DATASETS = ["beauty_serum", "sunscreen", "foundation"]


def read_dataset_file(dataset: str, filename: str) -> str:
    path = os.path.join(ROOT, dataset, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestAllDatasetsImport:

    @pytest.mark.parametrize("dataset", DATASETS)
    def test_product_import(self, dataset):
        content = read_dataset_file(dataset, "product.csv")
        product_id = f"test-{dataset}-product"
        product, result = parse_product_csv_with_validation(content, product_id)
        assert product is not None, f"{dataset} product should parse: {result.errors}"
        assert result.success_count == 1
        assert result.failed_count == 0
        assert product.title
        assert product.url
        assert product.platform

    @pytest.mark.parametrize("dataset", DATASETS)
    def test_competitors_import(self, dataset):
        content = read_dataset_file(dataset, "competitors.csv")
        comps, result = parse_competitors_csv_with_validation(content, f"test-{dataset}")
        assert result.success_count == 3, f"{dataset} should have 3 competitors: {result.errors}"
        assert result.failed_count == 0
        assert len(comps) == 3

    @pytest.mark.parametrize("dataset", DATASETS)
    def test_reviews_import(self, dataset):
        content = read_dataset_file(dataset, "reviews.csv")
        reviews, result = parse_reviews_csv_with_validation(content, f"test-{dataset}")
        assert result.success_count >= 5, f"{dataset} should have >= 5 reviews, got {result.success_count}: {result.errors}"
        assert result.failed_count == 0
        assert len(reviews) >= 5

    @pytest.mark.parametrize("dataset", DATASETS)
    def test_metrics_import(self, dataset):
        content = read_dataset_file(dataset, "metrics.csv")
        metrics, result = parse_metrics_csv_with_validation(content)
        assert result.success_count == 2, f"{dataset} should have 2 period rows: {result.errors}"
        assert "last_week" in metrics
        assert "this_week" in metrics
        assert metrics["last_week"].impressions > 0
        assert metrics["this_week"].orders > 0


class TestAllDatasetsFullAnalysis:

    @pytest.mark.parametrize("dataset", DATASETS)
    @pytest.mark.asyncio
    async def test_full_analysis_flow(self, dataset):
        project = Project(
            name=f"test-{dataset}-analysis",
            category="beauty_skincare",
            platform="mock_tmall",
        )
        await store.create_project(project)
        product_id = f"{project.id}-product"

        content = read_dataset_file(dataset, "product.csv")
        product, _ = parse_product_csv_with_validation(content, product_id)
        assert product is not None
        await store.set_product(product_id, product)

        content = read_dataset_file(dataset, "competitors.csv")
        comps, _ = parse_competitors_csv_with_validation(content, product_id)
        await store.set_competitors(product_id, comps)

        content = read_dataset_file(dataset, "reviews.csv")
        reviews, _ = parse_reviews_csv_with_validation(content, product_id)
        await store.set_reviews(product_id, reviews)

        content = read_dataset_file(dataset, "metrics.csv")
        metrics, _ = parse_metrics_csv_with_validation(content)
        await store.set_weekly_metrics(product_id, metrics)

        from app.agents.orchestrator import AnalysisOrchestrator
        from app.schemas.product import CreateAnalysisRequest

        request = CreateAnalysisRequest(
            product_url=product.url,
            competitor_urls=[c.url for c in comps],
            category=product.category or "beauty_skincare",
            platform=product.platform,
            use_seed_data=False,
        )

        orchestrator = AnalysisOrchestrator(project_id=product_id)
        report = await orchestrator.run(request)

        assert report.status == "completed"
        assert report.scores.total_score > 0, f"{dataset} total_score should be > 0"
        assert len(report.competitor_insights) == 3, f"{dataset} should have 3 competitor insights"
        assert len(report.title_suggestions) == 3
        assert len(report.image_copy_suggestions) == 5
        assert len(report.detail_page_structure) == 9
        assert report.weekly_report is not None
        assert len(report.markdown_report) > 100

        # Verify scoring dimensions all have reasons
        assert report.scores.title_search.reason
        assert report.scores.main_image_click.reason
        assert report.scores.detail_conversion.reason
        assert report.scores.competitor_diff.reason
        assert report.scores.review_risk.reason
        assert report.scores.review_health.reason
        assert report.scores.ad_landing.reason

        # Verify evidence is present in markdown
        assert "评分依据" in report.markdown_report

    @pytest.mark.parametrize("dataset", DATASETS)
    @pytest.mark.asyncio
    async def test_analysis_saved_to_project(self, dataset):
        project = Project(
            name=f"test-{dataset}-save",
            category="beauty_skincare",
            platform="mock_tmall",
        )
        await store.create_project(project)
        product_id = f"{project.id}-product"

        content = read_dataset_file(dataset, "product.csv")
        product, _ = parse_product_csv_with_validation(content, product_id)
        await store.set_product(product_id, product)

        content = read_dataset_file(dataset, "competitors.csv")
        await store.set_competitors(product_id, parse_competitors_csv_with_validation(content, product_id)[0])

        content = read_dataset_file(dataset, "reviews.csv")
        await store.set_reviews(product_id, parse_reviews_csv_with_validation(content, product_id)[0])

        content = read_dataset_file(dataset, "metrics.csv")
        await store.set_weekly_metrics(product_id, parse_metrics_csv_with_validation(content)[0])

        from app.agents.orchestrator import AnalysisOrchestrator
        from app.schemas.product import CreateAnalysisRequest

        request = CreateAnalysisRequest(
            product_url=product.url,
            competitor_urls=[],
            category=product.category or "beauty_skincare",
            platform=product.platform,
            use_seed_data=False,
        )

        orchestrator = AnalysisOrchestrator(project_id=product_id)
        report = await orchestrator.run(request)

        await store.add_report_to_project(project.id, report)
        saved = await store.get_project(project.id)
        assert saved is not None
        assert len(saved.reports) >= 1
        assert saved.reports[-1].id == report.id


class TestDatasetSpecifics:

    def test_beauty_serum_review_tags(self):
        """Beauty serum reviews should cover sensitivity, expectations, texture issues."""
        content = read_dataset_file("beauty_serum", "reviews.csv")
        reviews, _ = parse_reviews_csv_with_validation(content, "test")
        tags = [t for r in reviews for t in r.tags]
        assert any("敏感" in t for t in tags), "should have sensitivity tags"
        assert any("刺激" in t for t in tags)

    def test_sunscreen_review_tags(self):
        """Sunscreen reviews should cover acne, white cast, texture."""
        content = read_dataset_file("sunscreen", "reviews.csv")
        reviews, _ = parse_reviews_csv_with_validation(content, "test")
        tags = [t for r in reviews for t in r.tags]
        assert any("闷痘" in t for t in tags), "should have acne tags"
        assert any("泛白" in t for t in tags), "should have white cast tags"
        assert any("搓泥" in t for t in tags), "should have pilling tags"

    def test_foundation_review_tags(self):
        """Foundation reviews should cover shade mismatch, caking, oxidation, coverage."""
        content = read_dataset_file("foundation", "reviews.csv")
        reviews, _ = parse_reviews_csv_with_validation(content, "test")
        tags = [t for r in reviews for t in r.tags]
        assert any("色号" in t for t in tags), "should have shade tags"
        assert any("卡粉" in t for t in tags), "should have caking tags"
        assert any("持妆" in t for t in tags), "should have longevity tags"
        assert any("暗沉" in t for t in tags), "should have oxidation tags"
        assert any("遮瑕" in t for t in tags), "should have coverage tags"
