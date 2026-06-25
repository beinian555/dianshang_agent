from app.agents.base import BaseAgent
from app.schemas.product import Product
from app.schemas.analysis import DetailPageSection


class DetailPageAgent(BaseAgent):
    name = "DetailPageAgent"

    async def run(self, input_data: dict) -> list[DetailPageSection]:
        product: Product = input_data["product"]
        ingredients = " + ".join(product.ingredients[:4])
        users = "、".join(product.target_users[:3])
        scenarios = "、".join(product.usage_scenarios[:3])

        return [
            DetailPageSection(
                section_no=1,
                section_name="首屏利益点",
                goal="让用户快速理解产品解决什么问题。",
                content_points=[
                    "熬夜暗沉、干燥起皮、换季不稳定",
                    "补水保湿 + 舒缓修护 + 提亮肤色感",
                ],
                copy_suggestion="给熬夜肌的日常修护精华",
            ),
            DetailPageSection(
                section_no=2,
                section_name="用户痛点",
                goal="唤起用户对当前皮肤状态的关注。",
                content_points=[
                    "熬夜后脸黄、干、上妆卡粉",
                    "换季期皮肤泛红不稳定",
                    "用了很多产品但效果不明显",
                ],
                copy_suggestion="你是不是也在经历这些？",
            ),
            DetailPageSection(
                section_no=3,
                section_name="成分方案",
                goal="用成分建立专业感和信任。",
                content_points=[
                    f"核心成分：{ingredients}",
                    "每种成分对应解决一个皮肤问题",
                    "不添加酒精、香精、矿物油",
                ],
                copy_suggestion="科学配方，一瓶解决多维度问题",
            ),
            DetailPageSection(
                section_no=4,
                section_name="使用场景",
                goal="让用户对号入座，找到自己的使用场景。",
                content_points=[
                    f"适合人群：{users}",
                    f"使用场景：{scenarios}",
                ],
                copy_suggestion="无论哪种场景，都为你准备",
            ),
            DetailPageSection(
                section_no=5,
                section_name="竞品对比",
                goal="在不贬低竞品的前提下突出自身优势。",
                content_points=[
                    "vs 低价型：我们更注重成分品质和肤感体验",
                    "vs 高浓度型：我们更温和、新手友好、敏感肌可尝试",
                    "vs 敏感肌型：我们兼顾提亮和修护，不只做维稳",
                ],
                copy_suggestion="三合一修护精华，不只做一件事",
            ),
            DetailPageSection(
                section_no=6,
                section_name="敏感肌使用提示",
                goal="主动提供风险提示，降低售后差评。",
                content_points=[
                    "建议先在耳后或手臂内侧局部测试",
                    "确认无不适后再全脸使用",
                    "烟酰胺初次使用建议隔天使用，建立耐受",
                ],
                copy_suggestion="温和不等于100%不过敏，请先局部测试",
            ),
            DetailPageSection(
                section_no=7,
                section_name="使用方法",
                goal="指导正确使用手法，避免搓泥等体验问题。",
                content_points=[
                    "早晚洁面、爽肤水后使用",
                    "按压2泵于掌心，轻拍上脸至吸收",
                    "妆前使用建议等待2-3分钟后再上妆",
                    "白天使用建议配合防晒",
                ],
                copy_suggestion="用对手法，效果加倍",
            ),
            DetailPageSection(
                section_no=8,
                section_name="FAQ",
                goal="预判用户常见问题，减少客服压力。",
                content_points=[
                    "Q: 敏感肌可以用吗？ A: 建议先局部测试",
                    "Q: 多久见效？ A: 补水效果即时，提亮需坚持使用2-4周",
                    "Q: 会搓泥吗？ A: 按压手法 + 等待吸收可避免",
                ],
                copy_suggestion="你可能想知道的",
            ),
            DetailPageSection(
                section_no=9,
                section_name="规格与成交引导",
                goal="提供清晰的规格对比和购买建议。",
                content_points=[
                    "30ml 日常装：适合首次尝试",
                    "50ml 大容量：更划算，适合长期使用",
                    "套装组合：精华+面霜，搭配使用效果更佳",
                ],
                copy_suggestion="选择你的修护方案",
            ),
        ]
