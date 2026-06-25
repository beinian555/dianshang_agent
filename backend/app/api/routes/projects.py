from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.repositories.factory import get_store
from app.repositories.base import StoreBase
from app.schemas.project import Project, CreateProjectRequest, ImportResult
from app.utils.csv_parser import (
    parse_product_csv_with_validation,
    parse_competitors_csv_with_validation,
    parse_reviews_csv_with_validation,
    parse_metrics_csv_with_validation,
)

router = APIRouter(tags=["projects"])


@router.post("/projects")
async def create_project(request: CreateProjectRequest, store: StoreBase = Depends(get_store)):
    project = Project(name=request.name, category=request.category, platform=request.platform)
    return await store.create_project(project)


@router.get("/projects")
async def list_projects(store: StoreBase = Depends(get_store)):
    return await store.list_projects()


@router.get("/projects/{project_id}")
async def get_project(project_id: str, store: StoreBase = Depends(get_store)):
    project = await store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects/{project_id}/import/product")
async def import_product(project_id: str, file: UploadFile = File(...), store: StoreBase = Depends(get_store)):
    project = await store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    raw = await file.read()
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    content = raw.decode("utf-8")

    product_id = f"{project_id}-product"
    product, result = parse_product_csv_with_validation(content, product_id)
    result.project_id = project_id

    if product:
        await store.set_product(product_id, product)
        project.product = product

    return result


@router.post("/projects/{project_id}/import/competitors")
async def import_competitors(project_id: str, file: UploadFile = File(...), store: StoreBase = Depends(get_store)):
    project = await store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    raw = await file.read()
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    content = raw.decode("utf-8")

    product_id = f"{project_id}-product"
    competitors, result = parse_competitors_csv_with_validation(content, product_id)
    result.project_id = project_id

    if competitors:
        await store.set_competitors(product_id, competitors)
        project.competitors = competitors

    return result


@router.post("/projects/{project_id}/import/reviews")
async def import_reviews(project_id: str, file: UploadFile = File(...), store: StoreBase = Depends(get_store)):
    project = await store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    raw = await file.read()
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    content = raw.decode("utf-8")

    product_id = f"{project_id}-product"
    reviews, result = parse_reviews_csv_with_validation(content, product_id)
    result.project_id = project_id

    if reviews:
        await store.set_reviews(product_id, reviews)
        project.reviews = reviews

    return result


@router.post("/projects/{project_id}/import/metrics")
async def import_metrics(project_id: str, file: UploadFile = File(...), store: StoreBase = Depends(get_store)):
    project = await store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    raw = await file.read()
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    content = raw.decode("utf-8")

    product_id = f"{project_id}-product"
    metrics, result = parse_metrics_csv_with_validation(content)
    result.project_id = project_id

    if metrics:
        await store.set_weekly_metrics(product_id, metrics)
        project.weekly_metrics = metrics

    return result


@router.post("/projects/{project_id}/analysis", status_code=202)
async def run_project_analysis(project_id: str, store: StoreBase = Depends(get_store)):
    project = await store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.product:
        raise HTTPException(
            status_code=400,
            detail="Project has no product data. Import product first.",
        )

    from app.agents.orchestrator import AnalysisOrchestrator
    from app.schemas.product import CreateAnalysisRequest
    from app.schemas.job import AnalysisJob, AnalysisJobStatus

    product_id = f"{project_id}-product"

    # Create pending job
    job = AnalysisJob(project_id=project_id)
    await store.save_analysis_job(job)

    request = CreateAnalysisRequest(
        product_url=project.product.url,
        competitor_urls=[c.url for c in project.competitors],
        category=project.category,
        platform=project.platform,
        use_seed_data=False,
    )

    async def progress_callback(pct: int, label: str):
        await store.update_analysis_job(
            job.id,
            status=AnalysisJobStatus.RUNNING.value,
            progress=pct,
            current_step=label,
        )

    async def run_analysis():
        try:
            await store.update_analysis_job(
                job.id, status=AnalysisJobStatus.RUNNING.value, progress=0, current_step="启动分析"
            )
            orchestrator = AnalysisOrchestrator(project_id=product_id, store=store)
            report = await orchestrator.run(request, progress_callback=progress_callback)
            await store.add_report_to_project(project_id, report)
            await store.update_analysis_job(
                job.id,
                status=AnalysisJobStatus.COMPLETED.value,
                progress=100,
                current_step="完成",
                report_id=report.id,
            )
        except Exception as e:
            await store.update_analysis_job(
                job.id,
                status=AnalysisJobStatus.FAILED.value,
                error_message=str(e),
            )

    import asyncio
    asyncio.create_task(run_analysis())

    return job
