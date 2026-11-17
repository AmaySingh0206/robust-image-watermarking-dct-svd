"""FastAPI routes for Robustness Testing and Benchmark Suite."""

import json
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.database import get_db
from backend.app.schemas.experiment_schema import AttackResultSchema, BenchmarkResponse
from backend.app.services.experiment_service import ExperimentService
from backend.app.core.evaluation.benchmark import BenchmarkSuite

router = APIRouter(prefix="/experiments", tags=["Robustness Laboratory"])


@router.post("/run", response_model=AttackResultSchema)
async def run_attack(
    file: UploadFile = File(..., description="Watermarked image to attack"),
    attack_name: str = Form(..., description="Name of attack (jpeg, gaussian_noise, blur, etc.)"),
    parameters: str = Form("{}", description="JSON string of attack parameters"),
    secret_key: str = Form(..., description="Confidential secret key for extraction"),
    manifest: str = Form(..., description="JSON string of recovery manifest"),
    job_id: Optional[str] = Form(None, description="Optional job ID to associate with"),
    ground_truth_message: Optional[str] = Form(None, description="Original watermark payload message"),
    db: Session = Depends(get_db),
):
    """Applies an image attack distortion and measures extraction robustness."""
    try:
        params_dict = json.loads(parameters)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameters JSON: {str(e)}")

    try:
        manifest_dict = json.loads(manifest)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid manifest JSON: {str(e)}")

    try:
        content = await file.read()
        res = await ExperimentService.run_attack_experiment(
            image_bytes=content,
            attack_name=attack_name,
            params=params_dict,
            secret_key=secret_key,
            manifest=manifest_dict,
            job_id=job_id,
            ground_truth=ground_truth_message,
            db=db,
        )
        return AttackResultSchema(**res)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attack experiment execution failed: {str(e)}")


@router.post("/benchmark", response_model=BenchmarkResponse)
async def run_automated_benchmark(
    image_type: str = Form("natural_texture", description="natural_texture, smooth_gradient, or high_frequency_grid"),
    payload_message: str = Form("SPECTRAMARK-BENCHMARK-PAYLOAD", description="Watermark string"),
    secret_key: str = Form("BenchmarkMasterSecretKey2026", description="Passphrase for benchmark"),
):
    """Executes an automated performance and robustness benchmark across strength profiles and attacks."""
    images = BenchmarkSuite.generate_benchmark_images()
    if image_type not in images:
        raise HTTPException(status_code=400, detail=f"Invalid image type. Choose from: {list(images.keys())}")

    test_img = images[image_type]

    # Profile benchmarks
    profile_results = BenchmarkSuite.run_profile_benchmark(
        test_image=test_img,
        message=payload_message,
        secret_key=secret_key,
    )

    # Attack benchmark using the balanced watermarked output
    from backend.app.core.watermarking.embedding import WatermarkEmbedder
    wm_img, manifest, _ = WatermarkEmbedder.embed(
        image_input=test_img,
        message=payload_message,
        secret_key=secret_key,
        strength_profile="balanced",
        repetition=5,
    )

    attack_results = BenchmarkSuite.run_attack_suite_benchmark(
        watermarked_img=wm_img,
        manifest=manifest,
        secret_key=secret_key,
        message=payload_message,
    )

    return BenchmarkResponse(
        benchmark_id=str(uuid.uuid4()),
        test_image_type=image_type,
        profile_results=profile_results,
        attack_results=attack_results,
        generated_at=datetime.utcnow().isoformat(),
    )

