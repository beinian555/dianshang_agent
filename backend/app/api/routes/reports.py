from fastapi import APIRouter, Depends, HTTPException

from app.repositories.factory import get_store
from app.repositories.base import StoreBase

router = APIRouter(tags=["reports"])


@router.get("/reports/{report_id}")
async def get_report(report_id: str, store: StoreBase = Depends(get_store)):
    report = await store.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/reports/{report_id}/markdown")
async def get_report_markdown(report_id: str, store: StoreBase = Depends(get_store)):
    report = await store.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "filename": f"beauty-growth-report-{report_id}.md",
        "content": report.markdown_report,
    }
