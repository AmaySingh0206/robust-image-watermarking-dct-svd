"""FastAPI routes for Forensic Report generation and PDF downloads."""

from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.models.watermark_job import WatermarkJob
from backend.app.schemas.report_schema import ReportMetadataResponse
from backend.app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/{job_id}", response_model=ReportMetadataResponse)
async def get_report_metadata(job_id: str, db: Session = Depends(get_db)):
    """Retrieves forensic report metadata and download link."""
    job = db.query(WatermarkJob).filter(WatermarkJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' not found.")

    return ReportMetadataResponse(
        report_id=f"REP-{job.id[:8].upper()}",
        job_id=job.id,
        operation_type=job.operation_type,
        image_dimensions=[job.image_width or 0, job.image_height or 0],
        image_format=job.image_format or "PNG",
        algorithm=job.algorithm_version,
        created_at=job.created_at.isoformat() if job.created_at else "",
        metrics=job.metrics or {},
        manifest=job.recovery_manifest,
        experiments_count=len(job.experiments),
        pdf_download_url=f"/api/v1/reports/{job.id}/download",
    )


@router.get("/{job_id}/download")
async def download_report_pdf(job_id: str, db: Session = Depends(get_db)):
    """Generates and serves a publication-grade forensic PDF report."""
    job = db.query(WatermarkJob).filter(WatermarkJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' not found.")

    # Convert job & experiments to dict
    job_dict = {
        "id": job.id,
        "operation_type": job.operation_type,
        "status": job.status,
        "image_width": job.image_width,
        "image_height": job.image_height,
        "image_format": job.image_format,
        "recovery_manifest": job.recovery_manifest,
        "metrics": job.metrics,
    }

    experiments_list = []
    for exp in job.experiments:
        experiments_list.append({
            "attack_name": exp.attack_name,
            "attack_parameters": exp.attack_parameters,
            "psnr": exp.psnr,
            "ssim": exp.ssim,
            "nc": exp.nc,
            "ber": exp.ber,
            "extraction_status": exp.extraction_status,
        })

    pdf_filename = f"spectramark_audit_{job.id[:8]}.pdf"
    pdf_path = ReportService.generate_pdf_report(
        job_data=job_dict,
        experiments_data=experiments_list,
        output_filename=pdf_filename,
    )

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_filename,
    )

