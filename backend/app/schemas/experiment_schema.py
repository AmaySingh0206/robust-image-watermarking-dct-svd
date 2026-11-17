"""Pydantic schemas for Robustness Experiments and Attack Evaluations."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AttackRunRequest(BaseModel):
    attack_name: str
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    secret_key: str
    manifest: Dict[str, Any]
    ground_truth_message: Optional[str] = None


class AttackResultSchema(BaseModel):
    attack_name: str
    parameters: Dict[str, Any]
    attacked_image_url: str
    psnr_db: float
    ssim: float
    extraction_status: str
    extraction_success: bool
    recovered_message: Optional[str]
    mean_confidence: Optional[float]
    ber_percentage: Optional[float]
    nc: Optional[float]
    execution_time: float


class BenchmarkResponse(BaseModel):
    benchmark_id: str
    test_image_type: str
    profile_results: List[Dict[str, Any]]
    attack_results: List[Dict[str, Any]]
    generated_at: str

