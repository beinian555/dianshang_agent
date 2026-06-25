from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.models.base import Base


class AnalysisJobModel(Base):
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    status = Column(String, default="pending")
    progress = Column(Integer, default=0)
    current_step = Column(String, nullable=True)
    report_id = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
