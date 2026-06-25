from fastapi import APIRouter

from app.agents.orchestrator import AnalysisOrchestrator
from app.schemas.product import CreateAnalysisRequest

router = APIRouter(tags=["analysis"])


@router.post("/analysis")
async def create_analysis(request: CreateAnalysisRequest):
    orchestrator = AnalysisOrchestrator()
    report = await orchestrator.run(request)
    return {
        "analysis_id": f"analysis-{report.id.split('-')[-1]}",
        "status": report.status,
        "report_id": report.id,
    }
