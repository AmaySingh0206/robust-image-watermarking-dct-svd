from fastapi import APIRouter
from backend.app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health/live")
async def health_live():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": "live",
    }


@router.get("/health/ready")
async def health_ready():
    # Verify writeable data directories
    storage_ready = (
        settings.UPLOAD_DIR.exists()
        and settings.PROCESSED_DIR.exists()
        and settings.REPORTS_DIR.exists()
    )
    return {
        "status": "ready" if storage_ready else "degraded",
        "service": settings.APP_NAME,
        "storage": "operational" if storage_ready else "failed",
        "engine": "DCT-SVD-QIM",
    }

