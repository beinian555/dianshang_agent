from app.agents.base import BaseAgent
from app.schemas.product import Product
from app.schemas.analysis import ImageCopySuggestion


class ImageCopyAgent(BaseAgent):
    name = "ImageCopyAgent"

    async def run(self, input_data: dict) -> list[ImageCopySuggestion]:
        product: Product = input_data["product"]
        ingredients = product.ingredients[:3]

        return [
            ImageCopySuggestion(
                image_no=1,
                goal="提升点击",
                visual_focus="产品瓶身居中，背景为干净浅色，突出熬夜肌修护场景。",
                main_copy="熬夜肌修护精华",
                sub_copy="补水保湿｜舒缓干燥｜改善暗沉感",
                notes="不要写三天变白、立即修复等夸张承诺。",
            ),
            ImageCopySuggestion(
                image_no=2,
                goal="建立信任",
                visual_focus=f"核心成分{', '.join(ingredients)}文字排版，配合植物原料视觉。",
                main_copy=f"{' + '.join(ingredients)}",
                sub_copy="科学配比｜温和不刺激｜植萃修护",
                notes="成分名准确标注，不要捏造活性物浓度。",
            ),
            ImageCopySuggestion(
                image_no=3,
                goal="激发需求",
                visual_focus="熬夜、换季、妆前三大使用场景拼图。",
                main_copy="熬夜后 / 换季期 / 妆前打底",
                sub_copy="一瓶搞定多重肌肤不稳定",
                notes="场景图避免强调前后对比的医疗化表达。",
            ),
            ImageCopySuggestion(
                image_no=4,
                goal="消除顾虑",
                visual_focus="局部测试示意图，温和成分安全标注。",
                main_copy="敏感肌建议先局部试用",
                sub_copy="温和配方｜无酒精｜无香精",
                notes="敏感肌可用改为建议局部测试，不要做绝对承诺。",
            ),
            ImageCopySuggestion(
                image_no=5,
                goal="促进成交",
                visual_focus="30ml/50ml 规格对比展示 + 套装组合推荐。",
                main_copy=f"{product.sku_name or '30ml'} 日常装 / 50ml 大容量",
                sub_copy="2瓶装更划算 加购立减",
                notes="促销信息需与店铺实际活动一致。",
            ),
        ]
