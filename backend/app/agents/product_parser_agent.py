from app.agents.base import BaseAgent
from app.schemas.product import Product
from app.repositories.factory import get_store


class ProductParserAgent(BaseAgent):
    name = "ProductParserAgent"

    async def run(self, input_data: dict) -> Product:
        product_url: str = input_data["product_url"]
        use_seed_data: bool = input_data.get("use_seed_data", True)
        project_id: str | None = input_data.get("project_id")

        if use_seed_data:
            product = await get_store().get_product("beauty-main-001")
            if product:
                return product
        elif project_id:
            product = await get_store().get_product(project_id)
            if product:
                return product

        from app.seed.beauty_products import MAIN_PRODUCT
        return MAIN_PRODUCT
