from app.agents.base import BaseAgent
from app.schemas.product import Product
from app.schemas.competitor import CompetitorProduct
from app.schemas.analysis import ReviewCluster, TitleSuggestion


class TitleOptimizerAgent(BaseAgent):
    name = "TitleOptimizerAgent"

    async def run(self, input_data: dict) -> list[TitleSuggestion]:
        product: Product = input_data["product"]
        competitors: list[CompetitorProduct] = input_data.get("competitors", [])
        clusters: list[ReviewCluster] = input_data.get("review_clusters", [])

        ingredients_str = " ".join(product.ingredients[:3])
        users_str = " ".join(product.target_users[:3])

        return [
            TitleSuggestion(
                type="search_traffic",
                title=(
                    f"{ingredients_str}修护精华液女补水保湿提亮肤色"
                    f"{'敏感肌' if any('敏感肌' in c.cluster_name for c in clusters) else '换季维稳'}"
                    f"面部精华{product.sku_name or '30ml'}"
                ),
                reason="覆盖烟酰胺、修护、补水、提亮、敏感肌、换季维稳等搜索词，最大化搜索曝光。",
                risk_note="敏感肌表达避免绝对化，可在详情页补充局部测试提示。",
            ),
            TitleSuggestion(
                type="conversion_selling",
                title=(
                    f"熬夜肌专研修护精华 "
                    f"{' '.join(product.ingredients[:2])}补水保湿"
                    f" 改善暗沉粗糙 {product.sku_name or '30ml'}"
                ),
                reason="聚焦熬夜肌痛点，突出核心成分和功效，提升搜索到点击的转化率。",
                risk_note="避免使用\"立即见效\"\"根源解决\"等夸张表达。",
            ),
            TitleSuggestion(
                type="brand_premium",
                title=(
                    f"{product.brand or ''}植萃修护精华 "
                    f"{' '.join(product.ingredients[:2])} "
                    f"温和保湿舒缓 {product.sku_name or '30ml'}"
                ),
                reason="突出品牌感和成分品质，适合品牌专区搜索和忠实用户复购。",
                risk_note="品牌词搭配功效词需确保在品牌授权范围内。",
            ),
        ]
