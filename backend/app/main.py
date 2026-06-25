from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, seed, analysis, reports, projects, jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.config import settings
    if settings.store_backend == "postgres" and settings.database_url:
        from app.core.database import create_tables
        await create_tables()
    yield
    from app.core.database import dispose_engine
    await dispose_engine()


app = FastAPI(
    title="电商商品增长分析 Agent",
    description="面向电商单品运营的商品增长分析 Agent",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(seed.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
