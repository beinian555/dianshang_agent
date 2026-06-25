import pytest

from app.schemas.report import AnalysisReport
from app.schemas.analysis import (
    Scores,
    ScoreDimension,
    CompetitorInsight,
    TitleSuggestion,
    ImageCopySuggestion,
    DetailPageSection,
    ReviewCluster,
    FAQItem,
    AdMaterialSuggestion,
    WeeklyReportData,
)
from app.services.report_service import ReportService


@pytest.fixture
def report_service():
    return ReportService()


@pytest.fixture
def sample_report():
    return AnalysisReport(
        id="test-report",
        product_id="test-product",
        status="completed",
        summary="Test summary",
        scores=Scores(
            title_search=ScoreDimension(score=68, reason="覆盖品类关键词",
                                        evidence=["标题包含品类词: 精华"]),
            main_image_click=ScoreDimension(score=62, reason="主图展示利益点",
                                             evidence=["主图包含利益点: 补水, 保湿"]),
            detail_conversion=ScoreDimension(score=58, reason="覆盖用户痛点",
                                              evidence=["详情页包含用户痛点描述"]),
            competitor_diff=ScoreDimension(score=55, reason="有差异化卖点",
                                            evidence=["差异卖点: 舒缓修护"]),
            review_risk=ScoreDimension(score=40, reason="存在高风险聚类",
                                        evidence=["高风险聚类(['敏感肌刺激'])"]),
            review_health=ScoreDimension(score=60, reason="评价生态尚可",
                                          evidence=["共3类差评需要关注"]),
            ad_landing=ScoreDimension(score=64, reason="卖点清晰",
                                       evidence=["有明确卖点: 4个"]),
            total_score=61,
        ),
        competitor_insights=[
            CompetitorInsight(
                competitor_id="comp-a", positioning="Low price",
                main_selling_points=["low price"], strengths=["cheap"],
                weaknesses=["poor packaging"], learnable_points=["promotions"],
                avoid_points=["don't go too cheap"],
            ),
        ],
        title_suggestions=[
            TitleSuggestion(type="search_traffic", title="Test title",
                            reason="Test reason", risk_note="Test risk"),
        ],
        image_copy_suggestions=[
            ImageCopySuggestion(image_no=1, goal="CTR", visual_focus="product",
                                main_copy="Test copy", sub_copy="Test sub", notes="Test notes"),
        ],
        detail_page_structure=[
            DetailPageSection(section_no=1, section_name="Test section", goal="Test goal",
                              content_points=["point 1"], copy_suggestion="Test suggestion"),
        ],
        review_clusters=[
            ReviewCluster(
                id="c1", product_id="test-product", cluster_name="Test cluster",
                problem_type="product_expectation_risk", review_count=1, ratio=0.1,
                representative_reviews=["test review"], user_concern="test concern",
                business_impact="test impact", suggested_action="test action",
            ),
        ],
        faq_items=[
            FAQItem(question="Test Q?", answer="Test A.", type="pre_sale",
                    risk_level="low", source="product"),
        ],
        ad_material_suggestions=[
            AdMaterialSuggestion(angle="Test angle", target_user="Test user", hook="Test hook",
                                 script_structure=["step 1"], landing_page_requirement="Test req",
                                 risk_note="Test risk"),
        ],
        weekly_report=WeeklyReportData(
            summary="Test weekly summary", problems=["Test problem"],
            next_week_actions=["Test action"],
        ),
    )


class TestReportService:

    def test_generate_markdown_contains_all_sections(self, report_service, sample_report):
        md = report_service.generate_markdown(sample_report)
        assert "核心结论" in md
        assert "SKU 增长评分" in md
        assert "评分依据" in md
        assert "竞品卖点拆解" in md
        assert "标题优化建议" in md
        assert "主图文案建议" in md
        assert "详情页结构建议" in md
        assert "差评聚类分析" in md
        assert "客服 FAQ" in md
        assert "投流素材建议" in md
        assert "本周数据复盘" in md
        assert "下周优化任务" in md

    def test_generate_markdown_returns_non_empty_string(self, report_service, sample_report):
        md = report_service.generate_markdown(sample_report)
        assert len(md) > 100

    def test_generate_markdown_contains_scores(self, report_service, sample_report):
        md = report_service.generate_markdown(sample_report)
        assert "68" in md
        assert "62" in md
        assert "61" in md

    def test_generate_markdown_contains_evidence(self, report_service, sample_report):
        md = report_service.generate_markdown(sample_report)
        assert "标题包含品类词" in md
        assert "主图包含利益点" in md

    def test_generate_markdown_contains_review_split(self, report_service, sample_report):
        md = report_service.generate_markdown(sample_report)
        assert "差评风险度" in md
        assert "评价健康度" in md
