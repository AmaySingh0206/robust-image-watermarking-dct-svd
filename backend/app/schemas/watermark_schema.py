"""Pydantic schemas for Watermark Embedding requests and responses."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class CapacityRequest(BaseModel):
    width: int = Field(..., ge=16, le=8192)
    height: int = Field(..., ge=16, le=8192)
    repetition_factor: int = Field(default=5, ge=1, le=15)
    parity_bytes: int = Field(default=32, ge=8, le=64)


class CapacityResponse(BaseModel):
    image_dimensions: list[int]
    total_blocks: int
    repetition_factor: int
    overhead_bytes: int
    overhead_blocks: int
    max_payload_bytes: int
    is_feasible: bool
    recommended_min_dimension: int


class EmbedResponse(BaseModel):
    job_id: str
    status: str
    watermarked_image_url: str
    recovery_manifest: Dict[str, Any]
    metrics: Dict[str, Any]
    image_info: Dict[str, Any]

