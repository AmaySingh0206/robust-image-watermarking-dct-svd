"""FastAPI routes for Watermark Job status and historical queries."""

from typing import List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.models.watermark_job import WatermarkJob

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("")
async def list_jobs(limit: int = 20, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Retrieves recent watermarking and extraction jobs."""
    jobs = db.query(WatermarkJob).order_by(WatermarkJob.created_at.desc()).limit(limit).all()
    results = []
    for j in jobs:
        results.append({
            "id": j.id,
            "operation_type": j.operation_type,
            "status": j.status,
            "image_width": j.image_width,
            "image_height": j.image_height,
            "image_format": j.image_format,
            "created_at": j.created_at.isoformat() if j.created_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None,
            "metrics": j.metrics,
            "extracted_message": j.extracted_message,
        })
    return results


@router.get("/{job_id}")
async def get_job(job_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Retrieves detailed processing metadata for a specific job."""
    job = db.query(WatermarkJob).filter(WatermarkJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' not found.")

    experiments = []
    for exp in job.experiments:
        experiments.append({
            "id": exp.id,
            "attack_name": exp.attack_name,
            "attack_parameters": exp.attack_parameters,
            "psnr": exp.psnr,
            "ssim": exp.ssim,
            "nc": exp.nc,
            "ber": exp.ber,
            "extraction_status": exp.extraction_status,
            "execution_time": exp.execution_time,
            "output_image_url": f"/static/processed/{Path(exp.output_file_path).name}" if exp.output_file_path else None,
        })

    return {
        "id": job.id,
        "operation_type": job.operation_type,
        "status": job.status,
        "image_width": job.image_width,
        "image_height": job.image_height,
        "image_format": job.image_format,
        "algorithm_version": job.algorithm_version,
        "processing_configuration": job.processing_configuration,
        "recovery_manifest": job.recovery_manifest,
        "metrics": job.metrics,
        "extracted_message": job.extracted_message,
        "error_message": job.error_message,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "experiments": experiments,
    }
