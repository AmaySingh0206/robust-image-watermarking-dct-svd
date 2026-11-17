"""File storage service for safe uploads and processed artifacts.

Security controls:
- UUIDv4 based filenames.
- Verification of image file signatures.
- Rejection of oversized files (>25 MB) and decompression bombs (>67M pixels).
- Strictly separated directories outside frontend public access.
"""

from typing import Tuple
from pathlib import Path
import uuid
import io
from PIL import Image

from backend.app.config import settings


class StorageService:
    """Manages file storage operations."""

    ALLOWED_FORMATS = {"PNG", "JPEG", "JPG", "WEBP", "TIFF"}

    @classmethod
    def validate_image_bytes(cls, data: bytes) -> Tuple[Image.Image, str, Tuple[int, int]]:
        """Inspects and validates uploaded raw image bytes."""
        if len(data) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise ValueError(f"File exceeds maximum upload size limit of {settings.MAX_UPLOAD_SIZE_MB} MB")

        try:
            img = Image.open(io.BytesIO(data))
            img.verify()
        except Exception as e:
            raise ValueError(f"Uploaded file is not a valid image: {str(e)}")

        # Re-open for actual processing (verify closes stream in PIL)
        img = Image.open(io.BytesIO(data))
        fmt = (img.format or "PNG").upper()
        if fmt not in cls.ALLOWED_FORMATS:
            raise ValueError(f"Unsupported image format '{fmt}'. Allowed: {list(cls.ALLOWED_FORMATS)}")

        w, h = img.size
        if w * h > settings.MAX_IMAGE_PIXELS:
            raise ValueError(
                f"Image resolution {w}x{h} ({w*h} pixels) exceeds safety limit of {settings.MAX_IMAGE_PIXELS} pixels"
            )

        return img, fmt, (w, h)

    @classmethod
    def save_upload(cls, data: bytes, ext: str = "png") -> Tuple[str, Path]:
        """Saves uploaded raw bytes into UPLOAD_DIR with random UUID."""
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.{ext.lower()}"
        dest = settings.UPLOAD_DIR / filename
        dest.write_bytes(data)
        return file_id, dest

    @classmethod
    def save_processed_image(cls, img: Image.Image, format: str = "PNG") -> Tuple[str, Path]:
        """Saves processed PIL image into PROCESSED_DIR with random UUID."""
        file_id = str(uuid.uuid4())
        ext = "png" if format.upper() == "PNG" else "jpg"
        filename = f"{file_id}.{ext}"
        dest = settings.PROCESSED_DIR / filename
        img.save(dest, format=format)
        return file_id, dest

    @classmethod
    def get_processed_path(cls, filename: str) -> Path:
        """Returns Path for a processed image filename."""
        return settings.PROCESSED_DIR / filename

