"""Pydantic schemas for Watermark Extraction requests and responses."""

from typing import Dict, Any, Optional
from pydantic import BaseModel


class ExtractResponse(BaseModel):
    job_id: str
    status: str
    success: bool
    recovered_message: Optional[str] = None
    mean_confidence: Optional[float] = None
    fec_status: Optional[str] = None
    ber_percentage: Optional[float] = None
    nc: Optional[float] = None
    error: Optional[str] = None
    execution_time_seconds: float

