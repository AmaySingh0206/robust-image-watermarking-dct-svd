"""Watermark Blind Extraction Service."""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.models.watermark_job import WatermarkJob
from backend.app.services.storage_service import StorageService
from backend.app.services.watermark_service import executor
from backend.app.core.watermarking.extraction import WatermarkExtractor


class ExtractionService:
    """Manages asynchronous blind extraction and verification jobs."""

    @classmethod
    async def process_extract_job(
        cls,
        image_bytes: bytes,
        secret_key: str,
        manifest: Dict[str, Any],
        ground_truth: Optional[str],
        db: Session,
    ) -> Dict[str, Any]:
        """Runs blind extraction in worker thread and stores results in DB."""
        img, fmt, (w, h) = StorageService.validate_image_bytes(image_bytes)
        upload_id, upload_path = StorageService.save_upload(image_bytes, ext=fmt.lower())

        job = WatermarkJob(
            operation_type="extract",
            status="processing",
            image_width=w,
            image_height=h,
            image_format=fmt,
            original_file_path=str(upload_path),
            recovery_manifest=manifest,
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(
                executor,
                WatermarkExtractor.extract,
                img,
                secret_key,
                manifest,
                ground_truth,
            )

            job.status = "completed" if result["success"] else "failed"
            job.extracted_message = result.get("message")
            job.error_message = result.get("error")
            job.metrics = {
                "mean_confidence": result.get("mean_confidence"),
                "ber_percentage": result.get("ber_percentage"),
                "nc": result.get("nc"),
                "fec_status": result.get("fec_status"),
                "execution_time_seconds": result.get("execution_time_seconds"),
            }
            job.completed_at = datetime.now(timezone.utc)
            db.commit()

            return {
                "job_id": job.id,
                **result,
            }

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            raise e
