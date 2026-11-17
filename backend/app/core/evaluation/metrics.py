"""Unified Evaluation Metrics Accumulator for SPECTRAMARK."""

from typing import Dict, Any, Optional
from PIL import Image
import numpy as np

from backend.app.core.evaluation.psnr import calculate_psnr
from backend.app.core.evaluation.ssim import calculate_ssim
from backend.app.core.evaluation.nc import calculate_nc
from backend.app.core.evaluation.ber import calculate_ber


def evaluate_watermark_fidelity(
    img_orig: Image.Image,
    img_watermarked: Image.Image,
    execution_time: float = 0.0,
) -> Dict[str, Any]:
    """Evaluates visual fidelity of watermarked image relative to original host."""
    psnr = calculate_psnr(img_orig, img_watermarked)
    ssim_val = calculate_ssim(img_orig, img_watermarked)

    return {
        "psnr_db": round(psnr, 2),
        "ssim": round(ssim_val, 4),
        "execution_time_seconds": round(execution_time, 4),
        "visual_fidelity_passed": psnr >= 38.0 and ssim_val >= 0.98,
    }


def evaluate_extraction_metrics(
    bits_orig: Optional[np.ndarray],
    bits_extracted: np.ndarray,
    success: bool,
    confidence: float,
    execution_time: float = 0.0,
) -> Dict[str, Any]:
    """Evaluates extraction robustness and bit fidelity."""
    res = {
        "watermark_detected": success,
        "payload_recovered": success,
        "mean_confidence": round(confidence, 4),
        "execution_time_seconds": round(execution_time, 4),
    }

    if bits_orig is not None and len(bits_orig) == len(bits_extracted):
        res["nc"] = round(calculate_nc(bits_orig, bits_extracted), 4)
        res["ber_percentage"] = round(calculate_ber(bits_orig, bits_extracted), 2)
    else:
        res["nc"] = None
        res["ber_percentage"] = None

    return res

