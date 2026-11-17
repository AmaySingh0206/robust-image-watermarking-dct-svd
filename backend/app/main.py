from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.models.database import init_db
from backend.app.api.routes import health, watermark, extraction, experiments, jobs, reports
from backend.app.security import authentication


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables and storage directories on startup
    init_db()
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Advanced Digital Image Watermarking, Copyright Protection and Forensic Verification Platform Using DCT and SVD",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file mounts for processed images & reports
app.mount("/static/processed", StaticFiles(directory=str(settings.PROCESSED_DIR)), name="processed")
app.mount("/static/reports", StaticFiles(directory=str(settings.REPORTS_DIR)), name="reports")

# Base Health Routes
app.include_router(health.router)

# Versioned API Routes (/api/v1/...)
api_v1 = FastAPI(title=f"{settings.APP_NAME} API v1")
api_v1.include_router(watermark.router)
api_v1.include_router(extraction.router)
api_v1.include_router(experiments.router)
api_v1.include_router(jobs.router)
api_v1.include_router(reports.router)
api_v1.include_router(authentication.router)

app.mount(settings.API_V1_STR, api_v1)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "tagline": "Protect. Embed. Verify.",
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "api_v1_docs": f"{settings.API_V1_STR}/docs",
    }
