"""Watermark Embedding Job Service."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.models.watermark_job import WatermarkJob
from backend.app.services.storage_service import StorageService
from backend.app.core.watermarking.embedding import WatermarkEmbedder

executor = ThreadPoolExecutor(max_workers=settings.MAX_WORKER_THREADS)


class WatermarkService:
    """Manages asynchronous embedding job execution and database persistence."""

    @classmethod
    async def process_embed_job(
        cls,
        image_bytes: bytes,
        payload_message: str,
        secret_key: str,
        strength_profile: str,
        repetition: int,
        db: Session,
    ) -> Dict[str, Any]:
        """Validates input, runs embedding in threadpool, and stores metadata in DB."""
        # 1. Image validation
        img, fmt, (w, h) = StorageService.validate_image_bytes(image_bytes)

        # 2. Save original upload
        orig_id, orig_path = StorageService.save_upload(image_bytes, ext=fmt.lower())

        # 3. Create initial job record in DB
        job = WatermarkJob(
            operation_type="embed",
            status="processing",
            image_width=w,
            image_height=h,
            image_format=fmt,
            original_file_path=str(orig_path),
            processing_configuration={
                "strength_profile": strength_profile,
                "repetition_factor": repetition,
                "payload_bytes": len(payload_message.encode("utf-8")),
            },
        )
        db.add(job)
        db.commit()
        db.refresh(job)

        # 4. Run CPU-intensive embedding in worker thread
        loop = asyncio.get_running_loop()
        try:
            watermarked_img, manifest, metrics = await loop.run_in_executor(
                executor,
                WatermarkEmbedder.embed,
                img,
                payload_message,
                secret_key,
                strength_profile,
                repetition,
                32,
            )

            # 5. Save watermarked output image (PNG by default for lossless preservation)
            out_id, out_path = StorageService.save_processed_image(watermarked_img, format="PNG")

            # 6. Update Job Record in DB
            job.status = "completed"
            job.output_file_path = str(out_path)
            job.recovery_manifest = manifest
            job.metrics = metrics
            job.completed_at = datetime.now(timezone.utc)
            db.commit()

            return {
                "job_id": job.id,
                "status": "completed",
                "watermarked_image_url": f"/static/processed/{out_path.name}",
                "recovery_manifest": manifest,
                "metrics": metrics,
                "image_info": {
                    "width": w,
                    "height": h,
                    "format": fmt,
                },
            }

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            raise e
