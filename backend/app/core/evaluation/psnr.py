"""Peak Signal-to-Noise Ratio (PSNR) calculation.

Formula:
  MSE = (1 / (H * W * C)) * sum((I - K)^2)
  PSNR = 10 * log10(MAX^2 / MSE)
where MAX = 255 for 8-bit images.
"""

from typing import Union
import numpy as np
from PIL import Image


def calculate_psnr(
    img_true: Union[Image.Image, np.ndarray],
    img_test: Union[Image.Image, np.ndarray],
) -> float:
    """Calculates Peak Signal-to-Noise Ratio (PSNR) in decibels (dB).

    Args:
        img_true: Original reference image (PIL Image or numpy array).
        img_test: Modified/watermarked image.

    Returns:
        psnr_db: PSNR in dB. Returns 100.0 if images are mathematically identical.
    """
    if isinstance(img_true, Image.Image):
        arr_true = np.array(img_true, dtype=np.float64)
    else:
        arr_true = img_true.astype(np.float64)

    if isinstance(img_test, Image.Image):
        arr_test = np.array(img_test, dtype=np.float64)
    else:
        arr_test = img_test.astype(np.float64)

    if arr_true.shape != arr_test.shape:
        raise ValueError(
            f"Shape mismatch for PSNR calculation: {arr_true.shape} vs {arr_test.shape}"
        )

    # Compute Mean Squared Error
    mse = np.mean((arr_true - arr_test) ** 2)
    if mse < 1e-12:
        return 100.0  # Identical images

    max_val = 255.0
    psnr = 10.0 * np.log10((max_val ** 2) / mse)
    return float(psnr)

