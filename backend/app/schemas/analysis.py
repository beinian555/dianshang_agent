from pydantic import BaseModel, Field


class ReviewCluster(BaseModel):
    id: str
    product_id: str
    cluster_name: str
    problem_type: str
    review_count: int
    ratio: float
    representative_reviews: list[str] = Field(default_factory=list)
    user_concern: str
    business_impact: str
    suggested_action: str


class CompetitorInsight(BaseModel):
    competitor_id: str
    positioning: str
    main_selling_points: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    learnable_points: list[str] = Field(default_factory=list)
    avoid_points: list[str] = Field(default_factory=list)


class TitleSuggestion(BaseModel):
    type: str
    title: str
    reason: str
    risk_note: str


class ImageCopySuggestion(BaseModel):
    image_no: int
    goal: str
    visual_focus: str
    main_copy: str
    sub_copy: str
    notes: str


class DetailPageSection(BaseModel):
    section_no: int
    section_name: str
    goal: str
    content_points: list[str] = Field(default_factory=list)
    copy_suggestion: str


class FAQItem(BaseModel):
    question: str
    answer: str
    type: str
    risk_level: str
    source: str


class AdMaterialSuggestion(BaseModel):
    angle: str
    target_user: str
    hook: str
    script_structure: list[str] = Field(default_factory=list)
    landing_page_requirement: str
    risk_note: str


class WeeklyMetrics(BaseModel):
    impressions: int
    clicks: int
    ctr: float
    orders: int
    conversion_rate: float
    refund_rate: float
    ad_spend: float
    revenue: float
    roi: float


class WeeklyReportData(BaseModel):
    summary: str
    metrics_change: list[dict] = Field(default_factory=list)
    problems: list[str] = Field(default_factory=list)
    next_week_actions: list[str] = Field(default_factory=list)
    risk_notes: list[str] = Field(default_factory=list)


class ScoreDimension(BaseModel):
    score: int = Field(default=0, ge=0, le=100)
    reason: str = ""
    evidence: list[str] = Field(default_factory=list)


class Scores(BaseModel):
    title_search: ScoreDimension = Field(default_factory=ScoreDimension)
    main_image_click: ScoreDimension = Field(default_factory=ScoreDimension)
    detail_conversion: ScoreDimension = Field(default_factory=ScoreDimension)
    competitor_diff: ScoreDimension = Field(default_factory=ScoreDimension)
    review_risk: ScoreDimension = Field(default_factory=ScoreDimension)
    review_health: ScoreDimension = Field(default_factory=ScoreDimension)
    ad_landing: ScoreDimension = Field(default_factory=ScoreDimension)
    total_score: int = Field(default=0, ge=0, le=100)
