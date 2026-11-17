"""FastAPI routes for Watermark Embedding and Capacity Inquiries."""

from typing import Dict, Any
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.schemas.watermark_schema import CapacityRequest, CapacityResponse, EmbedResponse
from backend.app.core.watermarking.capacity import CapacityEstimator
from backend.app.services.watermark_service import WatermarkService

router = APIRouter(prefix="/watermarks", tags=["Watermarking"])


@router.post("/capacity", response_model=CapacityResponse)
async def check_capacity(req: CapacityRequest):
    """Calculates embedding capacity and block feasibility for given dimensions."""
    rep = req.repetition_factor
    res = CapacityEstimator.analyze_capacity(
        height=req.height,
        width=req.width,
        repetition=rep,
        parity_bytes=req.parity_bytes,
    )
    return CapacityResponse(
        image_dimensions=list(res["image_dimensions"]),
        total_blocks=res["total_blocks"],
        repetition_factor=res["repetition_factor"],
        overhead_bytes=res["overhead_bytes"],
        overhead_blocks=res["overhead_blocks"],
        max_payload_bytes=res["max_payload_bytes"],
        is_feasible=res["is_feasible"],
        recommended_min_dimension=res["recommended_min_dimension"],
    )


@router.post("/embed", response_model=EmbedResponse)
async def embed_watermark(
    file: UploadFile = File(..., description="Original image file (PNG, JPEG, TIFF, WebP)"),
    payload: str = Form(..., description="Copyright ownership message or asset identifier"),
    secret_key: str = Form(..., description="Confidential passphrase for HMAC block permutation"),
    strength_profile: str = Form("balanced", description="high_quality, balanced, or high_robustness"),
    repetition_factor: int = Form(5, description="Repetition factor (3, 5, or 7)"),
    db: Session = Depends(get_db),
):
    """Embeds an invisible blind watermark into an uploaded host image."""
    if not payload.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload message cannot be empty.",
        )
    if not secret_key.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Secret watermark key cannot be empty.",
        )

    try:
        content = await file.read()
        res = await WatermarkService.process_embed_job(
            image_bytes=content,
            payload_message=payload,
            secret_key=secret_key,
            strength_profile=strength_profile,
            repetition=repetition_factor,
            db=db,
        )
        return EmbedResponse(**res)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Watermark embedding failed: {str(e)}",
        )

