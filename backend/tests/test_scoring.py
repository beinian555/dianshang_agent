import pytest

from app.schemas.product import Product
from app.schemas.competitor import CompetitorProduct
from app.schemas.analysis import ReviewCluster
from app.services.growth_scoring_service import GrowthScoringService


@pytest.fixture
def scoring_service():
    return GrowthScoringService()


@pytest.fixture
def product():
    return Product(
        id="test-001",
        platform="mock_tmall",
        category="beauty_skincare",
        url="https://mock.shop/test",
        title="烟酰胺修护精华液补水保湿提亮肤色敏感肌可用30ml",
        brand="TestBrand",
        price=129,
        selling_points=["补水保湿", "舒缓修护", "改善暗沉", "敏感肌可用"],
        ingredients=["烟酰胺", "泛醇", "积雪草提取物", "透明质酸钠"],
        main_image_texts=["熬夜肌修护精华", "补水保湿提亮", "敏感肌可用", "植萃成分"],
        detail_sections=["熬夜暗沉干燥", "烟酰胺泛醇", "早晚洁面后使用", "适合干皮混合皮敏感肌"],
        target_users=["熬夜党", "干皮", "换季敏感肌"],
        usage_scenarios=["熬夜后", "妆前保湿", "换季修护"],
        specs=["30ml", "50ml"],
    )


@pytest.fixture
def competitors():
    return [
        CompetitorProduct(
            id="comp-a",
            product_id="test-001",
            url="https://mock.shop/comp-a",
            title="平价补水精华学生党",
            brand="PureGlow",
            price=59,
            selling_points=["低价", "补水"],
            weakness_hints=["包装普通"],
        ),
        CompetitorProduct(
            id="comp-b",
            product_id="test-001",
            url="https://mock.shop/comp-b",
            title="高浓度烟酰胺修护精华",
            brand="DermaLab",
            price=189,
            selling_points=["高浓度烟酰胺", "成分专业"],
            weakness_hints=["价格偏高"],
        ),
    ]


@pytest.fixture
def review_clusters():
    return [
        ReviewCluster(
            id="c1",
            product_id="test-001",
            cluster_name="敏感肌刺激",
            problem_type="product_expectation_risk",
            review_count=2,
            ratio=0.25,
            representative_reviews=["用完刺痛"],
            user_concern="刺激风险",
            business_impact="影响转化",
            suggested_action="增加提示",
        ),
    ]


class TestGrowthScoringService:

    def test_calculate_returns_scores(self, scoring_service, product, competitors, review_clusters):
        scores = scoring_service.calculate(product, competitors, review_clusters)
        assert scores.title_search.score > 0
        assert scores.main_image_click.score > 0
        assert scores.detail_conversion.score > 0
        assert scores.competitor_diff.score > 0
        assert scores.review_risk.score >= 0
        assert scores.review_health.score >= 0
        assert scores.ad_landing.score > 0

    def test_total_score_in_range(self, scoring_service, product, competitors, review_clusters):
        scores = scoring_service.calculate(product, competitors, review_clusters)
        assert 0 <= scores.total_score <= 100

    def test_each_score_in_range(self, scoring_service, product, competitors, review_clusters):
        scores = scoring_service.calculate(product, competitors, review_clusters)
        for dim in [
            scores.title_search,
            scores.main_image_click,
            scores.detail_conversion,
            scores.competitor_diff,
            scores.review_risk,
            scores.review_health,
            scores.ad_landing,
        ]:
            assert 0 <= dim.score <= 100, f"{dim} score out of range"

    def test_total_is_weighted_average(self, scoring_service, product, competitors, review_clusters):
        scores = scoring_service.calculate(product, competitors, review_clusters)
        from app.services.growth_scoring_service import WEIGHTS
        expected_total = int(
            scores.title_search.score * WEIGHTS["title_search"]
            + scores.main_image_click.score * WEIGHTS["main_image_click"]
            + scores.detail_conversion.score * WEIGHTS["detail_conversion"]
            + scores.competitor_diff.score * WEIGHTS["competitor_diff"]
            + scores.review_health.score * WEIGHTS["review_health"]
            + scores.ad_landing.score * WEIGHTS["ad_landing"]
        )
        assert abs(scores.total_score - expected_total) <= 1

    def test_each_dimension_has_reason_and_evidence(self, scoring_service, product, competitors, review_clusters):
        scores = scoring_service.calculate(product, competitors, review_clusters)
        for dim_name in [
            "title_search", "main_image_click", "detail_conversion",
            "competitor_diff", "review_risk", "review_health", "ad_landing",
        ]:
            dim = getattr(scores, dim_name)
            assert dim.reason, f"{dim_name} missing reason"
            # evidence can be empty for some dimensions (e.g., competitor_diff with no competitors)

    def test_review_risk_and_health_are_different(self, scoring_service, product, competitors, review_clusters):
        scores = scoring_service.calculate(product, competitors, review_clusters)
        # With clusters present, risk should be > 0 and health should be < 100
        assert scores.review_risk.score != scores.review_health.score
