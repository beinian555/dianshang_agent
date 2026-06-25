import os
import pytest

from app.repositories.store import store
from app.schemas.project import Project, CreateProjectRequest
from app.utils.csv_parser import (
    parse_product_csv,
    parse_competitors_csv,
    parse_reviews_csv,
    parse_metrics_csv,
)

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "sample_data", "beauty_serum")


def read_sample(filename: str) -> str:
    path = os.path.join(SAMPLE_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class TestCSVParsing:

    def test_parse_product_csv(self):
        content = read_sample("product.csv")
        product = parse_product_csv(content, "test-product-id")
        assert product.id == "test-product-id"
        assert product.title != ""
        assert product.brand == "LumiSkin"
        assert product.price == 129
        assert len(product.selling_points) == 4
        assert len(product.ingredients) == 4
        assert len(product.specs) == 3

    def test_parse_competitors_csv(self):
        content = read_sample("competitors.csv")
        competitors = parse_competitors_csv(content, "test-product-id")
        assert len(competitors) == 3
        assert competitors[0].id == "competitor-a"
        assert competitors[1].id == "competitor-b"
        assert competitors[2].id == "competitor-c"
        assert len(competitors[0].selling_points) == 4

    def test_parse_reviews_csv(self):
        content = read_sample("reviews.csv")
        reviews = parse_reviews_csv(content, "test-product-id")
        assert len(reviews) == 8
        assert reviews[0].rating == 2
        assert len(reviews[0].tags) == 2

    def test_parse_metrics_csv(self):
        content = read_sample("metrics.csv")
        metrics = parse_metrics_csv(content)
        assert "last_week" in metrics
        assert "this_week" in metrics
        assert metrics["last_week"].impressions == 12000
        assert metrics["this_week"].roi == 2.68


class TestCSVImportToStore:

    @pytest.mark.asyncio
    async def test_import_product_to_store(self):
        content = read_sample("product.csv")
        product = parse_product_csv(content, "store-test-product")
        await store.set_product("store-test-product", product)
        retrieved = await store.get_product("store-test-product")
        assert retrieved is not None
        assert retrieved.title == product.title

    @pytest.mark.asyncio
    async def test_import_competitors_to_store(self):
        content = read_sample("competitors.csv")
        competitors = parse_competitors_csv(content, "store-test-product")
        await store.set_competitors("store-test-product", competitors)
        retrieved = await store.get_competitors("store-test-product")
        assert len(retrieved) == 3

    @pytest.mark.asyncio
    async def test_import_reviews_to_store(self):
        content = read_sample("reviews.csv")
        reviews = parse_reviews_csv(content, "store-test-product")
        await store.set_reviews("store-test-product", reviews)
        retrieved = await store.get_reviews("store-test-product")
        assert len(retrieved) == 8

    @pytest.mark.asyncio
    async def test_import_metrics_to_store(self):
        content = read_sample("metrics.csv")
        metrics = parse_metrics_csv(content)
        await store.set_weekly_metrics("store-test-product", metrics)
        retrieved = await store.get_weekly_metrics("store-test-product")
        assert "last_week" in retrieved
        assert retrieved["last_week"].impressions == 12000
