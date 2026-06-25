from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.analysis import (
    Scores,
    CompetitorInsight,
    TitleSuggestion,
    ImageCopySuggestion,
    DetailPageSection,
    ReviewCluster,
    FAQItem,
    AdMaterialSuggestion,
    WeeklyReportData,
)


class AnalysisReport(BaseModel):
    id: str
    product_id: str
    status: str
    summary: str = ""
    scores: Scores = Field(default_factory=Scores)
    competitor_insights: list[CompetitorInsight] = Field(default_factory=list)
    title_suggestions: list[TitleSuggestion] = Field(default_factory=list)
    image_copy_suggestions: list[ImageCopySuggestion] = Field(default_factory=list)
    detail_page_structure: list[DetailPageSection] = Field(default_factory=list)
    review_clusters: list[ReviewCluster] = Field(default_factory=list)
    faq_items: list[FAQItem] = Field(default_factory=list)
    ad_material_suggestions: list[AdMaterialSuggestion] = Field(default_factory=list)
    weekly_report: WeeklyReportData | None = None
    markdown_report: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
