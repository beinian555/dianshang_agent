from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str
    platform: str
    category: str
    url: str
    title: str
    brand: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    sku_name: Optional[str] = None
    specs: list[str] = Field(default_factory=list)
    main_image_texts: list[str] = Field(default_factory=list)
    detail_sections: list[str] = Field(default_factory=list)
    selling_points: list[str] = Field(default_factory=list)
    ingredients: list[str] = Field(default_factory=list)
    target_users: list[str] = Field(default_factory=list)
    usage_scenarios: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class CreateAnalysisRequest(BaseModel):
    product_url: str
    competitor_urls: list[str]
    category: str
    platform: str
    use_seed_data: bool = True
