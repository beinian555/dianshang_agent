import json
import logging

from app.agents.base import BaseAgent
from app.agents.provider_factory import get_llm_provider
from app.schemas.product import Product
from app.schemas.competitor import CompetitorProduct
from app.schemas.analysis import CompetitorInsight

logger = logging.getLogger(__name__)


class CompetitorAnalyzerAgent(BaseAgent):
    name = "CompetitorAnalyzerAgent"

    async def run(self, input_data: dict) -> list[CompetitorInsight]:
        product: Product = input_data["product"]
        competitors: list[CompetitorProduct] = input_data["competitors"]

        try:
            provider = get_llm_provider()
            from app.agents.mock_llm import MockLLMProvider
            if not isinstance(provider, MockLLMProvider):
                return await self._run_with_llm(provider, product, competitors)
        except Exception as e:
            logger.warning(f"LLM competitor analysis failed, falling back to rules: {e}")

        return self._run_with_rules(product, competitors)

    async def _run_with_llm(self, provider, product: Product, competitors: list[CompetitorProduct]) -> list[CompetitorInsight]:
        from app.prompts.competitor_analyzer import COMPETITOR_SYSTEM, build_competitor_user_prompt

        product_info = json.dumps({
            "title": product.title,
            "price": product.price,
            "brand": product.brand,
            "selling_points": product.selling_points,
            "target_users": product.target_users,
        }, ensure_ascii=False)

        competitor_info = json.dumps([
            {
                "id": c.id,
                "title": c.title,
                "price": c.price,
                "brand": c.brand,
                "sales_hint": c.sales_hint,
                "rating": c.rating,
                "review_count": c.review_count,
                "selling_points": c.selling_points,
                "weakness_hints": c.weakness_hints,
            }
            for c in competitors
        ], ensure_ascii=False)

        result = await provider.generate_json(
            system_prompt=COMPETITOR_SYSTEM,
            user_prompt=build_competitor_user_prompt(product_info, competitor_info),
        )

        # result should be a list of competitor insights
        items = result if isinstance(result, list) else result.get("competitors", result.get("insights", []))

        insights = []
        for item in items:
            insights.append(CompetitorInsight(
                competitor_id=item.get("competitor_id", ""),
                positioning=item.get("positioning", "综合型"),
                main_selling_points=item.get("main_selling_points", []),
                strengths=item.get("strengths", []),
                weaknesses=item.get("weaknesses", []),
                learnable_points=item.get("learnable_points", []),
                avoid_points=item.get("avoid_points", []),
            ))
        return insights

    def _run_with_rules(self, product: Product, competitors: list[CompetitorProduct]) -> list[CompetitorInsight]:
        insights: list[CompetitorInsight] = []
        for comp in competitors:
            positioning = self._determine_positioning(comp)
            strengths = self._analyze_strengths(comp, product)
            weaknesses = self._analyze_weaknesses(comp)
            learnable = self._find_learnable_points(comp, product)
            avoid = self._find_avoid_points(comp)

            insights.append(
                CompetitorInsight(
                    competitor_id=comp.id,
                    positioning=positioning,
                    main_selling_points=comp.selling_points,
                    strengths=strengths,
                    weaknesses=weaknesses,
                    learnable_points=learnable,
                    avoid_points=avoid,
                )
            )
        return insights

    def _determine_positioning(self, comp: CompetitorProduct) -> str:
        price = comp.price or 0
        points = comp.selling_points
        low_price_keywords = {"低价", "学生党", "平价"}
        expert_keywords = {"高浓度", "成分专业", "功效护肤", "屏障修护"}
        sensitive_keywords = {"敏感肌", "舒缓", "换季维稳", "积雪草"}

        if price < 80 and any(k in low_price_keywords for k in points):
            return "低价走量型"
        elif any(k in expert_keywords for k in points):
            return "成分党专业型"
        elif any(k in sensitive_keywords for k in points):
            return "敏感肌温和型"
        return "综合型"

    def _analyze_strengths(self, comp: CompetitorProduct, product: Product) -> list[str]:
        strengths: list[str] = []
        price = comp.price or 0
        product_price = product.price or 0

        if price < product_price:
            strengths.append(f"价格低于自家产品{product_price - price}元")
        if (comp.review_count or 0) > 5000:
            strengths.append(f"销量基数大，评论量{comp.review_count}+")
        if comp.promotions:
            strengths.append(f"促销手段多：{', '.join(comp.promotions)}")
        if any("成分党" in sp or "成分" in sp for sp in comp.selling_points):
            strengths.append("成分专业形象突出")
        if any("敏感肌" in sp for sp in comp.selling_points):
            strengths.append("敏感肌赛道定位清晰")
        return strengths

    def _analyze_weaknesses(self, comp: CompetitorProduct) -> list[str]:
        return comp.weakness_hints.copy()

    def _find_learnable_points(self, comp: CompetitorProduct, product: Product) -> list[str]:
        learnable: list[str] = []
        comp_title_kws = set(comp.title.replace(" ", ""))
        product_title_kws = set(product.title.replace(" ", ""))

        extra_kws = comp_title_kws - product_title_kws
        if extra_kws:
            learnable.append("标题中覆盖了自家未用的关键词")

        if comp.promotions:
            learnable.append(f"可参考促销方式：{', '.join(comp.promotions)}")

        if comp.sales_hint:
            learnable.append(f"竞品主图展示销量信息：{comp.sales_hint}")

        return learnable

    def _find_avoid_points(self, comp: CompetitorProduct) -> list[str]:
        avoid: list[str] = []
        if any("低价" in sp for sp in comp.selling_points):
            avoid.append("不要只打低价，否则会削弱品牌感")
        if any("敏感肌顾虑明显" in w for w in comp.weakness_hints):
            avoid.append("避免在敏感肌可用上做过度承诺")
        if any("刺激性顾虑" in w for w in comp.weakness_hints):
            avoid.append("高浓度成分需提示耐受建立过程")
        return avoid
