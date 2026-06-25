from datetime import datetime

from pydantic import BaseModel, Field


class Review(BaseModel):
    id: str
    product_id: str
    source: str
    rating: int
    content: str
    created_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)
