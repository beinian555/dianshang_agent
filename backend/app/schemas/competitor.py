from typing import Optional

from pydantic import BaseModel, Field


class CompetitorProduct(BaseModel):
    id: str
    product_id: str
    url: str
    title: str
    brand: Optional[str] = None
    price: Optional[float] = None
    sales_hint: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    selling_points: list[str] = Field(default_factory=list)
    main_image_texts: list[str] = Field(default_factory=list)
    detail_sections: list[str] = Field(default_factory=list)
    promotions: list[str] = Field(default_factory=list)
    weakness_hints: list[str] = Field(default_factory=list)
