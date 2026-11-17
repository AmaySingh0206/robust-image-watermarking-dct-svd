"""Structural Similarity Index Measure (SSIM) calculation.

Uses scikit-image's structural_similarity across all spatial channels.
Returns float in [-1.0, 1.0], where 1.0 denotes identical structural fidelity.
"""

from typing import Union
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim


def calculate_ssim(
    img_true: Union[Image.Image, np.ndarray],
    img_test: Union[Image.Image, np.ndarray],
) -> float:
    """Calculates Structural Similarity Index Measure (SSIM).

    Args:
        img_true: Original reference image.
        img_test: Modified or watermarked image.

    Returns:
        ssim_score: SSIM value in [-1, 1].
    """
    if isinstance(img_true, Image.Image):
        arr_true = np.array(img_true)
    else:
        arr_true = img_true

    if isinstance(img_test, Image.Image):
        arr_test = np.array(img_test)
    else:
        arr_test = img_test

    if arr_true.shape != arr_test.shape:
        raise ValueError(
            f"Shape mismatch for SSIM calculation: {arr_true.shape} vs {arr_test.shape}"
        )

    # Determine channel configuration
    if arr_true.ndim == 2:
        # Grayscale
        score = ssim(arr_true, arr_test, data_range=255)
    elif arr_true.ndim == 3:
        # Multichannel RGB/RGBA
        score = ssim(arr_true, arr_test, channel_axis=2, data_range=255)
    else:
        raise ValueError(f"Unsupported array dimension: {arr_true.ndim}")

    return float(score)

