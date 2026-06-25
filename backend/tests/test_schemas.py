from app.schemas.product import Product, CreateAnalysisRequest
from app.schemas.competitor import CompetitorProduct
from app.schemas.review import Review
from app.schemas.analysis import ReviewCluster, Scores, ScoreDimension, WeeklyMetrics
from app.schemas.report import AnalysisReport


class TestProductSchema:
    def test_product_creation(self):
        product = Product(
            id="test-001",
            platform="mock_tmall",
            category="beauty_skincare",
            url="https://mock.shop/product/test",
            title="测试精华液 30ml",
        )
        assert product.id == "test-001"
        assert product.specs == []
        assert product.selling_points == []

    def test_create_analysis_request(self):
        req = CreateAnalysisRequest(
            product_url="https://mock.shop/product/test",
            competitor_urls=["https://mock.shop/product/comp-a"],
            category="beauty_skincare",
            platform="mock_tmall",
            use_seed_data=True,
        )
        assert req.use_seed_data is True


class TestCompetitorSchema:
    def test_competitor_creation(self):
        comp = CompetitorProduct(
            id="comp-001",
            product_id="prod-001",
            url="https://mock.shop/comp",
            title="竞品精华液",
            price=59,
        )
        assert comp.id == "comp-001"
        assert comp.selling_points == []


class TestReviewSchema:
    def test_review_creation(self):
        review = Review(
            id="rev-001",
            product_id="prod-001",
            source="mock",
            rating=2,
            content="产品效果一般",
            tags=["效果预期"],
        )
        assert review.rating == 2
        assert len(review.tags) == 1


class TestReviewClusterSchema:
    def test_review_cluster_creation(self):
        cluster = ReviewCluster(
            id="cluster-001",
            product_id="prod-001",
            cluster_name="敏感肌刺激顾虑",
            problem_type="product_expectation_risk",
            review_count=2,
            ratio=0.25,
            representative_reviews=["用完刺痛"],
            user_concern="用户担心过敏",
            business_impact="影响敏感肌人群转化",
            suggested_action="增加局部测试提示",
        )
        assert cluster.cluster_name == "敏感肌刺激顾虑"
        assert cluster.review_count == 2


class TestScoreDimensionSchema:
    def test_score_dimension_default(self):
        dim = ScoreDimension()
        assert dim.score == 0
        assert dim.reason == ""
        assert dim.evidence == []

    def test_score_dimension_with_evidence(self):
        dim = ScoreDimension(score=75, reason="test reason", evidence=["item1", "item2"])
        assert dim.score == 75
        assert len(dim.evidence) == 2


class TestScoresSchema:
    def test_scores_default(self):
        scores = Scores()
        assert scores.title_search.score == 0
        assert scores.review_risk.score == 0
        assert scores.review_health.score == 0
        assert scores.total_score == 0

    def test_scores_with_dimensions(self):
        scores = Scores(
            title_search=ScoreDimension(score=80, reason="good title", evidence=["covers keywords"]),
            main_image_click=ScoreDimension(score=70, reason="good image"),
            detail_conversion=ScoreDimension(score=60, reason="ok detail"),
            competitor_diff=ScoreDimension(score=50, reason="some diff"),
            review_risk=ScoreDimension(score=30, reason="low risk"),
            review_health=ScoreDimension(score=75, reason="healthy"),
            ad_landing=ScoreDimension(score=40, reason="basic landing"),
            total_score=61,
        )
        assert scores.title_search.score == 80
        assert scores.title_search.evidence == ["covers keywords"]
        assert scores.review_risk.score == 30
        assert scores.review_health.score == 75
        assert scores.total_score == 61


class TestWeeklyMetricsSchema:
    def test_weekly_metrics_creation(self):
        metrics = WeeklyMetrics(
            impressions=12000,
            clicks=480,
            ctr=0.04,
            orders=38,
            conversion_rate=0.079,
            refund_rate=0.052,
            ad_spend=1800,
            revenue=4902,
            roi=2.72,
        )
        assert metrics.impressions == 12000
        assert metrics.roi == 2.72


class TestAnalysisReportSchema:
    def test_report_creation(self):
        report = AnalysisReport(
            id="report-001",
            product_id="prod-001",
            status="completed",
            summary="测试报告",
        )
        assert report.id == "report-001"
        assert report.status == "completed"
        assert report.scores.total_score == 0
        assert report.competitor_insights == []
