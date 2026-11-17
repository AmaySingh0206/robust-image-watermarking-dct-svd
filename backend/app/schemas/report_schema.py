"""Pydantic schemas for Forensic Reports."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ReportMetadataResponse(BaseModel):
    report_id: str
    job_id: str
    operation_type: str
    image_dimensions: List[int]
    image_format: str
    algorithm: str
    created_at: str
    metrics: Dict[str, Any]
    manifest: Optional[Dict[str, Any]]
    experiments_count: int
    pdf_download_url: str

