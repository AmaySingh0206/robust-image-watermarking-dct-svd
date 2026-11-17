"""JPEG Compression Attack Simulation.

Simulates lossy DCT quantization artifacts at configurable quality factors (95, 85, 75, 60, 40).
Saves to in-memory byte buffer and re-reads back into PIL Image.
"""

import io
from PIL import Image


def apply_jpeg_compression(img: Image.Image, quality: int = 85) -> Image.Image:
    """Applies JPEG compression to an image.

    Args:
        img: Input PIL Image.
        quality: JPEG compression quality factor in [1, 100].

    Returns:
        attacked_img: JPEG-compressed PIL Image.
    """
    quality = max(1, min(100, int(quality)))

    # JPEG does not support alpha channel directly
    if img.mode == "RGBA":
        r, g, b, a = img.split()
        rgb_img = Image.merge("RGB", (r, g, b))
        buffer = io.BytesIO()
        rgb_img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        attacked_rgb = Image.open(buffer)
        attacked_rgb.load()
        # Re-attach original alpha
        r2, g2, b2 = attacked_rgb.split()
        return Image.merge("RGBA", (r2, g2, b2, a))
    elif img.mode == "L":
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        attacked_img = Image.open(buffer)
        attacked_img.load()
        return attacked_img
    else:
        rgb_img = img.convert("RGB")
        buffer = io.BytesIO()
        rgb_img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        attacked_img = Image.open(buffer)
        attacked_img.load()
        return attacked_img

