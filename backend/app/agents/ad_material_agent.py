import json
import logging

from app.agents.base import BaseAgent
from app.agents.provider_factory import get_llm_provider
from app.schemas.product import Product
from app.schemas.analysis import AdMaterialSuggestion

logger = logging.getLogger(__name__)


class AdMaterialAgent(BaseAgent):
    name = "AdMaterialAgent"

    async def run(self, input_data: dict) -> list[AdMaterialSuggestion]:
        product: Product = input_data["product"]

        try:
            provider = get_llm_provider()
            from app.agents.mock_llm import MockLLMProvider
            if not isinstance(provider, MockLLMProvider):
                return await self._run_with_llm(provider, product)
        except Exception as e:
            logger.warning(f"LLM ad material generation failed, falling back to rules: {e}")

        return self._run_with_rules(product)

    async def _run_with_llm(self, provider, product: Product) -> list[AdMaterialSuggestion]:
        from app.prompts.ad_material import AD_SYSTEM, build_ad_material_user_prompt

        product_info = json.dumps({
            "title": product.title,
            "brand": product.brand,
            "price": product.price,
            "selling_points": product.selling_points,
            "ingredients": product.ingredients,
            "target_users": product.target_users,
            "usage_scenarios": product.usage_scenarios,
        }, ensure_ascii=False)

        result = await provider.generate_json(
            system_prompt=AD_SYSTEM,
            user_prompt=build_ad_material_user_prompt(product_info),
        )

        items = result if isinstance(result, list) else result.get("suggestions", [])

        suggestions = []
        for item in items:
            suggestions.append(AdMaterialSuggestion(
                angle=item.get("angle", ""),
                target_user=item.get("target_user", ""),
                hook=item.get("hook", ""),
                script_structure=item.get("script_structure", []),
                landing_page_requirement=item.get("landing_page_requirement", ""),
                risk_note=item.get("risk_note", ""),
            ))
        return suggestions

    def _run_with_rules(self, product: Product) -> list[AdMaterialSuggestion]:
        ingredients = " + ".join(product.ingredients[:2])

        return [
            AdMaterialSuggestion(
                angle="熬夜肌痛点型",
                target_user="经常熬夜、肤色暗沉、妆前卡粉的年轻女性（22-30岁）",
                hook="熬夜后脸看起来又干又黄？",
                script_structure=[
                    "展示熬夜后皮肤状态（暗沉、干燥、疲惫感）",
                    "指出干燥暗沉导致上妆不服帖的痛点",
                    f"引出{product.brand}修护精华，{ingredients}成分方案",
                    "展示清爽质地和快速吸收效果",
                    "引导查看商品详情页了解更多",
                ],
                landing_page_requirement="详情页首屏必须承接熬夜肌、补水保湿、妆前服帖等信息。",
                risk_note="不要承诺快速美白或医学修复效果。",
            ),
            AdMaterialSuggestion(
                angle="成分科普型",
                target_user="关注成分、看测评、做功课的理性消费者（25-35岁）",
                hook=f"{ingredients}，你的皮肤真的选对了吗？",
                script_structure=[
                    f"逐一介绍{product.ingredients[0]}、{product.ingredients[1]}的作用",
                    "对比低价产品和专业产品的成分差异",
                    f"展示{product.brand}的成分配比和温和性",
                    "强调无酒精、无香精、无矿物油",
                    "引导高知用户进入详情页了解完整成分表",
                ],
                landing_page_requirement="详情页成分区需要完整的成分说明和功效对应。",
                risk_note="成分科普要准确，不要夸大单一成分功效。",
            ),
            AdMaterialSuggestion(
                angle="场景代入型",
                target_user="换季期皮肤不稳定、经常出差、作息不规律的用户",
                hook="换季 + 熬夜，皮肤还能稳住吗？",
                script_structure=[
                    "展示换季皮肤泛红场景",
                    "展示熬夜加班后用精华的放松感",
                    "展示妆前使用后妆容更服帖",
                    "强调一瓶应对多种不稳定场景",
                    "引导进入详情页选择规格",
                ],
                landing_page_requirement="详情页需要有明确的场景分区和使用建议。",
                risk_note="场景展示要真实，不要过度美化效果。",
            ),
            AdMaterialSuggestion(
                angle="对比选择型",
                target_user="在多个产品间犹豫、正在做购买决策的用户",
                hook="同是修护精华，为什么选它？",
                script_structure=[
                    "列出用户挑选精华时的几个关键维度",
                    f"对比{product.brand}在成分、温和性、价格上的综合优势",
                    "不贬低竞品，而是展示适合什么人群",
                    "给出明确的选择建议：如果你是XX，就选它",
                    "引导查看详情页的竞品对比区",
                ],
                landing_page_requirement="详情页竞品对比区必须客观真实，避免贬低竞品。",
                risk_note="对比内容必须真实可查，不可编造竞品数据。",
            ),
        ]
