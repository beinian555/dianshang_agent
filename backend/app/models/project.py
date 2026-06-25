from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, String

from app.models.base import Base, PydanticJSONB
from app.schemas.product import Product
from app.schemas.competitor import CompetitorProduct
from app.schemas.review import Review
from app.schemas.report import AnalysisReport


class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, default="beauty")
    platform = Column(String, default="unknown")

    product = Column(PydanticJSONB(Product))
    competitors = Column(PydanticJSONB(CompetitorProduct, is_list=True))
    reviews = Column(PydanticJSONB(Review, is_list=True))
    weekly_metrics = Column(JSON)
    reports = Column(PydanticJSONB(AnalysisReport, is_list=True))

    status = Column(String, default="draft")
    created_at = Column(DateTime, default=datetime.now)
