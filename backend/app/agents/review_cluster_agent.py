import logging

from app.agents.base import BaseAgent
from app.agents.provider_factory import get_llm_provider
from app.schemas.review import Review
from app.schemas.analysis import ReviewCluster

logger = logging.getLogger(__name__)

CLUSTER_RULES: list[dict] = [
    {
        "cluster_name": "敏感肌刺激顾虑",
        "problem_type": "product_expectation_risk",
        "keywords": ["敏感肌", "刺痛", "泛红", "不耐受", "刺激", "过敏"],
        "user_concern": "用户担心敏感肌可用的承诺过强，实际存在刺痛和泛红风险。",
        "business_impact": "会影响敏感肌人群转化，也可能导致售后和差评增加。",
        "suggested_action": "详情页增加局部测试提示，客服话术避免绝对承诺，将\"敏感肌可用\"改为\"敏感肌建议先局部试用\"。",
    },
    {
        "cluster_name": "效果预期不符",
        "problem_type": "product_expectation_gap",
        "keywords": ["没感觉", "不明显", "普通", "没有详情页说得", "预期不符", "没有特别惊喜", "效果", "晒黑", "晒伤"],
        "user_concern": "用户认为产品效果与详情页描述差距大，缺乏可感知的差异化价值。",
        "business_impact": "削弱复购意愿，用户会转向其他同价位产品。",
        "suggested_action": "详情页降低夸大表达，增加使用前后对比数据（非医学），强化肤感体验描述。",
    },
    {
        "cluster_name": "规格性价比问题",
        "problem_type": "perceived_value_risk",
        "keywords": ["小", "30ml", "性价比", "贵", "很快就用完", "不值", "用量"],
        "user_concern": "用户觉得容量小、用得快的心理预期与实际不符，觉得不够划算。",
        "business_impact": "可能导致用户选择竞品的大容量或低价产品。",
        "suggested_action": "主图增加容量使用时长说明，或推出组合套装提升价值感。",
    },
    {
        "cluster_name": "使用体验问题",
        "problem_type": "product_experience_risk",
        "keywords": ["黏", "搓泥", "不好吸收", "上妆", "油腻", "肤感", "厚重", "成膜", "泛白", "质地"],
        "user_concern": "产品质地影响日常使用体验，搓泥/油腻/泛白等问题让用户不敢继续使用。",
        "business_impact": "限制用户使用场景，尤其是妆前使用场景，影响年轻女性用户转化。",
        "suggested_action": "详情页增加正确的使用手法说明和等待吸收时间提示，FAQ增加妆前使用注意事项。",
    },
    {
        "cluster_name": "物流包装问题",
        "problem_type": "logistics_experience_risk",
        "keywords": ["物流", "压坏", "包装", "漏", "退货"],
        "user_concern": "快递包装质量影响用户对品牌品质的感知。",
        "business_impact": "虽然不影响产品本身质量，但会拉低整体购物体验评价。",
        "suggested_action": "与仓库确认包装标准，增加缓冲材料，考虑品牌化包装提升开箱体验。",
    },
    {
        "cluster_name": "客服承诺问题",
        "problem_type": "service_commitment_risk",
        "keywords": ["客服说", "客服承诺", "详情页说"],
        "user_concern": "用户依赖客服/详情页的建议，但承诺与实际体验不一致。",
        "business_impact": "增加售后纠纷风险，损害品牌信任度。",
        "suggested_action": "统一客服话术，敏感肌相关问题统一回答建议先局部试用，避免绝对化承诺。",
    },
    {
        "cluster_name": "闷痘/闭口问题",
        "problem_type": "product_experience_risk",
        "keywords": ["闷痘", "闭口", "痘痘", "痘", "长痘"],
        "user_concern": "用户担心产品致痘或堵塞毛孔，停用后痘痘消失加强了产品是原因的认知。",
        "business_impact": "对油皮/痘肌用户群体转化率影响大，可能引发负面口碑传播。",
        "suggested_action": "详情页明确标注致痘成分风险，建议油皮/痘肌用户局部试用后再全脸使用。",
    },
    {
        "cluster_name": "色号/妆效问题",
        "problem_type": "product_expectation_gap",
        "keywords": ["色号", "卡粉", "暗沉", "遮瑕", "斑驳", "脱妆", "起皮", "持妆", "发灰", "发黄"],
        "user_concern": "色号不匹配或妆效不持久导致用户对产品不满意。",
        "business_impact": "影响底妆类产品的核心转化率，色号问题是底妆退货的主要原因之一。",
        "suggested_action": "详情页增加色号对比图和选色指南，提供试色卡或小样降低选色风险。",
    },
]


class ReviewClusterAgent(BaseAgent):
    name = "ReviewClusterAgent"

    async def run(self, reviews: list[Review]) -> list[ReviewCluster]:
        try:
            provider = get_llm_provider()
            from app.agents.mock_llm import MockLLMProvider
            if not isinstance(provider, MockLLMProvider):
                return await self._run_with_llm(provider, reviews)
        except Exception as e:
            logger.warning(f"LLM review clustering failed, falling back to rules: {e}")

        return self._run_with_rules(reviews)

    async def _run_with_llm(self, provider, reviews: list[Review]) -> list[ReviewCluster]:
        from app.prompts.review_cluster import REVIEW_CLUSTER_SYSTEM, build_review_cluster_user_prompt

        reviews_text = "\n".join(
            f"{r.id}|{r.rating}|{r.content}"
            for r in reviews
        )

        result = await provider.generate_json(
            system_prompt=REVIEW_CLUSTER_SYSTEM,
            user_prompt=build_review_cluster_user_prompt("商品", reviews_text),
        )

        clusters_data = result if isinstance(result, list) else result.get("clusters", [])
        total = sum(c.get("review_count", 0) for c in clusters_data)

        clusters = []
        for c in clusters_data:
            clusters.append(ReviewCluster(
                id=f"cluster-llm-{len(clusters) + 1:03d}",
                product_id="",
                cluster_name=c.get("cluster_name", ""),
                problem_type=c.get("problem_type", "product_experience_risk"),
                review_count=c.get("review_count", 0),
                ratio=round(c.get("review_count", 0) / max(total, 1), 2),
                representative_reviews=c.get("representative_reviews", []),
                user_concern=c.get("user_concern", ""),
                business_impact=c.get("business_impact", ""),
                suggested_action=c.get("suggested_action", ""),
            ))
        return clusters

    def _run_with_rules(self, reviews: list[Review]) -> list[ReviewCluster]:
        clusters: list[ReviewCluster] = []
        assigned_review_ids: set[str] = set()
        total = len(reviews)

        for idx, rule in enumerate(CLUSTER_RULES):
            matched = [
                r for r in reviews
                if r.id not in assigned_review_ids
                and any(kw in r.content for kw in rule["keywords"])
            ]
            if not matched:
                continue

            for r in matched:
                assigned_review_ids.add(r.id)

            clusters.append(
                ReviewCluster(
                    id=f"cluster-{idx + 1:03d}",
                    product_id="beauty-main-001",
                    cluster_name=rule["cluster_name"],
                    problem_type=rule["problem_type"],
                    review_count=len(matched),
                    ratio=round(len(matched) / total, 2) if total > 0 else 0,
                    representative_reviews=[r.content for r in matched],
                    user_concern=rule["user_concern"],
                    business_impact=rule["business_impact"],
                    suggested_action=rule["suggested_action"],
                )
            )

        return clusters
