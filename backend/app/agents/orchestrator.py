import asyncio
import uuid
from collections.abc import Callable, Awaitable

from app.agents.mock_llm import MockLLMProvider
from app.agents.llm_logger import LoggingLLMProvider
from app.agents.product_parser_agent import ProductParserAgent
from app.agents.competitor_analyzer_agent import CompetitorAnalyzerAgent
from app.agents.review_cluster_agent import ReviewClusterAgent
from app.agents.title_optimizer_agent import TitleOptimizerAgent
from app.agents.image_copy_agent import ImageCopyAgent
from app.agents.detail_page_agent import DetailPageAgent
from app.agents.faq_agent import FAQAgent
from app.agents.ad_material_agent import AdMaterialAgent
from app.agents.weekly_report_agent import WeeklyReportAgent
from app.schemas.product import CreateAnalysisRequest
from app.schemas.report import AnalysisReport
from app.services.growth_scoring_service import GrowthScoringService
from app.services.report_service import ReportService
from app.repositories.factory import get_store

STEP_PROGRESS = {
    "parse_product": (5, "解析商品数据"),
    "load_data": (10, "加载竞品和评价数据"),
    "competitor_analysis": (20, "竞品分析"),
    "review_clustering": (30, "差评聚类"),
    "growth_scoring": (40, "增长评分"),
    "title_optimization": (50, "标题优化"),
    "image_copy": (60, "图文卖点"),
    "detail_page": (70, "详情页结构"),
    "faq": (80, "FAQ生成"),
    "ad_material": (85, "广告素材"),
    "weekly_report": (90, "周报生成"),
    "build_report": (95, "生成报告"),
    "complete": (100, "完成"),
}


class AnalysisOrchestrator:

    def __init__(self, project_id: str | None = None, store=None):
        self.project_id = project_id
        self.store = store if store is not None else get_store()
        llm = LoggingLLMProvider(MockLLMProvider(), agent_name="orchestrator")
        self.product_parser = ProductParserAgent(llm)
        self.competitor_analyzer = CompetitorAnalyzerAgent(llm)
        self.review_cluster = ReviewClusterAgent(llm)
        self.title_optimizer = TitleOptimizerAgent(llm)
        self.image_copy = ImageCopyAgent(llm)
        self.detail_page = DetailPageAgent(llm)
        self.faq = FAQAgent(llm)
        self.ad_material = AdMaterialAgent(llm)
        self.weekly_report = WeeklyReportAgent(llm)
        self.scoring_service = GrowthScoringService()
        self.report_service = ReportService()

    async def run(
        self,
        request: CreateAnalysisRequest,
        progress_callback: Callable[[int, str], Awaitable[None]] | None = None,
    ) -> AnalysisReport:
        async def step(name: str):
            pct, label = STEP_PROGRESS[name]
            if progress_callback:
                await progress_callback(pct, label)

        await step("parse_product")

        # 1. Parse product
        product = await self.product_parser.run({
            "product_url": request.product_url,
            "category": request.category,
            "platform": request.platform,
            "use_seed_data": request.use_seed_data,
            "project_id": self.project_id,
        })

        await step("load_data")

        # 2. Get competitors
        competitors = await self.store.get_competitors(product.id)

        # 3. Get reviews
        reviews = await self.store.get_reviews(product.id)

        await step("competitor_analysis")

        # 4. Run competitor analysis
        competitor_insights = await self.competitor_analyzer.run({
            "product": product,
            "competitors": competitors,
        })

        await step("review_clustering")

        # 5. Run review clustering
        review_clusters = await self.review_cluster.run(reviews)

        await step("growth_scoring")

        # 6. Growth scoring
        scores = self.scoring_service.calculate(product, competitors, review_clusters)

        await step("title_optimization")

        # 7. Title optimization
        title_suggestions = await self.title_optimizer.run({
            "product": product,
            "competitors": competitors,
            "review_clusters": review_clusters,
        })

        await step("image_copy")

        # 8. Image copy
        image_copy_suggestions = await self.image_copy.run({
            "product": product,
        })

        await step("detail_page")

        # 9. Detail page structure
        detail_page_structure = await self.detail_page.run({
            "product": product,
        })

        await step("faq")

        # 10. FAQ
        faq_items = await self.faq.run({
            "review_clusters": review_clusters,
        })

        await step("ad_material")

        # 11. Ad material suggestions
        ad_material_suggestions = await self.ad_material.run({
            "product": product,
        })

        await step("weekly_report")

        # 12. Weekly report
        metrics = await self.store.get_weekly_metrics(product.id)
        weekly_report_data = await self.weekly_report.run(metrics) if metrics else None

        await step("build_report")

        # 13. Build report
        report_id = f"report-{uuid.uuid4().hex[:8]}"

        report = AnalysisReport(
            id=report_id,
            product_id=product.id,
            status="completed",
            summary=self._build_summary(product, scores, review_clusters),
            scores=scores,
            competitor_insights=competitor_insights,
            title_suggestions=title_suggestions,
            image_copy_suggestions=image_copy_suggestions,
            detail_page_structure=detail_page_structure,
            review_clusters=review_clusters,
            faq_items=faq_items,
            ad_material_suggestions=ad_material_suggestions,
            weekly_report=weekly_report_data,
        )

        # 14. Generate markdown
        report.markdown_report = self.report_service.generate_markdown(report)

        # 15. Save report
        await self.store.save_report(report)

        await step("complete")

        return report

    def _build_summary(self, product, scores, clusters) -> str:
        return (
            f"{product.brand}「{product.title}」的综合增长评分为 {scores.total_score} 分。"
            f"竞品环境中，主要面临低价走量型、成分党专业型、敏感肌温和型三类竞品。"
            f"差评主要集中在{len(clusters)}个方面，其中敏感肌刺激、效果预期不符是最核心的转化风险。"
            f"建议优先优化详情页前3屏和敏感肌使用提示，同步调整客服话术降低售后风险。"
        )
