from fastapi import APIRouter, Depends, HTTPException

from app.repositories.factory import get_store
from app.repositories.base import StoreBase

router = APIRouter(tags=["jobs"])


@router.get("/analysis-jobs/{job_id}")
async def get_analysis_job(job_id: str, store: StoreBase = Depends(get_store)):
    job = await store.get_analysis_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
