"""SQLAlchemy Models for Processing Jobs and Experiment Results."""

from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

from backend.app.models.database import Base


class WatermarkJob(Base):
    """Stores metadata and evaluation metrics for Watermarking and Extraction jobs."""

    __tablename__ = "watermark_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    operation_type = Column(String(32), nullable=False)  # 'embed' or 'extract'
    status = Column(String(32), nullable=False, default="pending")  # pending, processing, completed, failed
    
    # Image properties
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    image_format = Column(String(16), nullable=True)
    
    # Engine configuration
    algorithm_version = Column(String(32), default="1.0.0")
    processing_configuration = Column(JSON, nullable=True)
    
    # Manifest (non-secret extraction parameters)
    recovery_manifest = Column(JSON, nullable=True)
    
    # Result metrics & extracted info
    metrics = Column(JSON, nullable=True)
    extracted_message = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Storage paths (relative or UUID based)
    original_file_path = Column(String(255), nullable=True)
    output_file_path = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    experiments = relationship("ExperimentResult", back_populates="job", cascade="all, delete-orphan")


class ExperimentResult(Base):
    """Stores attack experiment evaluations associated with a watermarked job."""

    __tablename__ = "experiment_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("watermark_jobs.id"), nullable=False)
    
    attack_name = Column(String(64), nullable=False)
    attack_parameters = Column(JSON, nullable=True)
    
    # Image degradation
    psnr = Column(Float, nullable=True)
    ssim = Column(Float, nullable=True)
    
    # Forensic watermark recovery
    nc = Column(Float, nullable=True)
    ber = Column(Float, nullable=True)
    extraction_status = Column(String(32), nullable=False)
    execution_time = Column(Float, nullable=True)
    
    output_file_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    job = relationship("WatermarkJob", back_populates="experiments")
