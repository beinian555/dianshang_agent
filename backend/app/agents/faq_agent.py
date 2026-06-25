from app.agents.base import BaseAgent
from app.schemas.analysis import ReviewCluster, FAQItem


class FAQAgent(BaseAgent):
    name = "FAQAgent"

    async def run(self, input_data: dict) -> list[FAQItem]:
        clusters: list[ReviewCluster] = input_data.get("review_clusters", [])

        faq_items = [
            FAQItem(
                question="敏感肌可以用吗？",
                answer="可以作为日常修护精华尝试，但不同肤质耐受情况不同，建议先在耳后或局部少量试用，确认无不适后再全脸使用。含有烟酰胺，初次使用建议隔天使用建立耐受。",
                type="pre_sale",
                risk_level="high",
                source="review_cluster",
            ),
            FAQItem(
                question="用多久能看到效果？",
                answer="补水保湿效果使用后即可感受到，肌肤更水润不紧绷。提亮肤色和改善暗沉通常需要坚持使用2-4周。因个体差异效果时间不同，请耐心使用。",
                type="pre_sale",
                risk_level="medium",
                source="review_cluster",
            ),
            FAQItem(
                question="早上用后上妆会搓泥吗？",
                answer="建议使用按压手法（不要揉搓），按压吸收后等待2-3分钟再上妆。如果后续使用防晒或妆前乳，建议等待每层产品吸收后再叠加。",
                type="usage",
                risk_level="medium",
                source="review_cluster",
            ),
            FAQItem(
                question="30ml 能用多久？",
                answer="早晚各使用一次，每次按压2泵，30ml 大约可用1.5-2个月。具体用量因人而异，可根据个人情况调整。",
                type="pre_sale",
                risk_level="low",
                source="review_cluster",
            ),
            FAQItem(
                question="保质期和储存方式？",
                answer="未开封保质期3年，开封后建议6个月内用完。请存放在阴凉干燥处，避免阳光直射。",
                type="usage",
                risk_level="low",
                source="product",
            ),
            FAQItem(
                question="用后泛红/刺痛怎么办？",
                answer="如出现泛红或刺痛，请立即停止使用，并用清水清洗。可能是对烟酰胺不耐受，建议先隔天使用建立耐受。如持续不适，请停止使用并咨询皮肤科医生。",
                type="concern",
                risk_level="high",
                source="review_cluster",
            ),
            FAQItem(
                question="孕妇/哺乳期可以用吗？",
                answer="产品成分温和，但因孕期/哺乳期皮肤状态特殊，建议使用前咨询医生。",
                type="concern",
                risk_level="medium",
                source="product",
            ),
            FAQItem(
                question="可以退货吗？",
                answer="支持7天无理由退货（未拆封使用）。如使用后有不适，请先联系客服确认情况，我们会根据具体情况处理。",
                type="after_sale",
                risk_level="medium",
                source="product",
            ),
        ]

        return faq_items
