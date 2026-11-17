"""FastAPI routes for Watermark Blind Extraction and Forensic Verification."""

import json
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.schemas.extraction_schema import ExtractResponse
from backend.app.services.extraction_service import ExtractionService

router = APIRouter(prefix="/watermarks", tags=["Extraction"])


@router.post("/extract", response_model=ExtractResponse)
async def extract_watermark(
    file: UploadFile = File(..., description="Watermarked image to analyze"),
    secret_key: str = Form(..., description="Confidential secret watermark key"),
    manifest: str = Form(..., description="JSON string of the recovery manifest"),
    ground_truth_message: Optional[str] = Form(None, description="Optional expected message for BER evaluation"),
    db: Session = Depends(get_db),
):
    """Blindly extracts and cryptographically verifies an embedded watermark."""
    if not secret_key.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Secret watermark key cannot be empty.",
        )

    try:
        manifest_dict = json.loads(manifest)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid recovery manifest JSON: {str(e)}",
        )

    try:
        content = await file.read()
        res = await ExtractionService.process_extract_job(
            image_bytes=content,
            secret_key=secret_key,
            manifest=manifest_dict,
            ground_truth=ground_truth_message,
            db=db,
        )
        return ExtractResponse(
            job_id=res["job_id"],
            status=res["status"],
            success=res["success"],
            recovered_message=res.get("message"),
            mean_confidence=res.get("mean_confidence"),
            fec_status=res.get("fec_status"),
            ber_percentage=res.get("ber_percentage"),
            nc=res.get("nc"),
            error=res.get("error"),
            execution_time_seconds=res.get("execution_time_seconds", 0.0),
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}",
        )

