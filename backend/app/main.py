from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from .core.config import settings
from .core.database import Base, engine
from .core.migrations import run_platform_migrations
from .models import database_models  # noqa: F401 - registers ORM models
from .api import alerts, analytics, auth, behavior, cameras, dashboard, heatmaps, mapping, products, reports, shelves, stores, tracking, users, zones


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        if settings.AUTO_MIGRATE:
            await run_platform_migrations(connection)
        await connection.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description="Production backend for camera mapping, shopper tracking, attention analytics and retail intelligence.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("static/heatmaps", exist_ok=True)
os.makedirs("static/uploads/videos", exist_ok=True)
os.makedirs("static/uploads/captures", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Canonical API surface. Legacy duplicate routers are intentionally not mounted
# because they duplicated /api/cameras, /api/products and /api/layout routes.
for router_module in (
    auth,
    stores,
    users,
    cameras,
    zones,
    shelves,
    mapping,
    products,
    tracking,
    analytics,
    behavior,
    heatmaps,
    dashboard,
    reports,
    alerts,
):
    app.include_router(router_module.router)


@app.get("/", tags=["Health Check"])
async def read_root():
    return {"status": "online", "service": settings.PROJECT_NAME, "version": app.version}


@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "healthy"}


@app.get("/health/db", tags=["Health Check"])
async def database_health_check():
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT current_database(), current_setting('server_version'), extname FROM pg_extension WHERE extname = 'timescaledb'"))
        row = result.first()
    if row is None:
        return {"status": "healthy", "database": settings.POSTGRES_DB, "timescaledb": False}
    return {"status": "healthy", "database": row[0], "postgres_version": row[1], "timescaledb": True}
