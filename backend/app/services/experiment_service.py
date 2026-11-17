"""Robustness Experiment and Attack Service."""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.models.watermark_job import ExperimentResult, WatermarkJob
from backend.app.services.storage_service import StorageService
from backend.app.services.watermark_service import executor
from backend.app.core.attacks.attack_runner import AttackRunner


class ExperimentService:
    """Manages attack simulation execution and persists experiment records."""

    @classmethod
    async def run_attack_experiment(
        cls,
        image_bytes: bytes,
        attack_name: str,
        params: Dict[str, Any],
        secret_key: str,
        manifest: Dict[str, Any],
        job_id: Optional[str],
        ground_truth: Optional[str],
        db: Session,
    ) -> Dict[str, Any]:
        """Applies attack, extracts watermark, saves attacked image, and records experiment in DB."""
        img, fmt, (w, h) = StorageService.validate_image_bytes(image_bytes)

        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(
            executor,
            AttackRunner.evaluate_attack,
            img,
            attack_name,
            params,
            secret_key,
            manifest,
            ground_truth,
        )

        # Save attacked image to processed dir for visual comparison in frontend
        out_id, out_path = StorageService.save_processed_image(res["attacked_image"], format="PNG")

        exp_record = None
        if job_id:
            existing_job = db.query(WatermarkJob).filter(WatermarkJob.id == job_id).first()
            if existing_job:
                exp_record = ExperimentResult(
                    job_id=job_id,
                    attack_name=attack_name,
                    attack_parameters=params,
                    psnr=res["degradation_metrics"]["psnr_db"],
                    ssim=res["degradation_metrics"]["ssim"],
                    nc=res["extraction_results"].get("nc"),
                    ber=res["extraction_results"].get("ber_percentage"),
                    extraction_status=res["extraction_results"]["status"],
                    execution_time=res["total_execution_time"],
                    output_file_path=str(out_path),
                )
                db.add(exp_record)
                db.commit()
                db.refresh(exp_record)

        return {
            "experiment_id": exp_record.id if exp_record else out_id,
            "attack_name": attack_name,
            "parameters": params,
            "attacked_image_url": f"/static/processed/{out_path.name}",
            "psnr_db": res["degradation_metrics"]["psnr_db"],
            "ssim": res["degradation_metrics"]["ssim"],
            "extraction_status": res["extraction_results"]["status"],
            "extraction_success": res["extraction_results"]["success"],
            "recovered_message": res["extraction_results"]["recovered_message"],
            "mean_confidence": res["extraction_results"].get("mean_confidence"),
            "ber_percentage": res["extraction_results"].get("ber_percentage"),
            "nc": res["extraction_results"].get("nc"),
            "execution_time": res["total_execution_time"],
        }

