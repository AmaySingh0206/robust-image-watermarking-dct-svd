"""Photometric Distortions: Brightness, Contrast, and Gamma Adjustments."""

from PIL import Image, ImageEnhance
import numpy as np


def apply_brightness_attack(img: Image.Image, factor: float = 1.1) -> Image.Image:
    """Adjusts image brightness.

    Args:
        img: Input PIL Image.
        factor: Brightness multiplier (1.0 = original, 1.2 = +20% brighter, 0.8 = 20% darker).

    Returns:
        attacked_img: Brightness adjusted PIL Image.
    """
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(max(0.1, float(factor)))


def apply_contrast_attack(img: Image.Image, factor: float = 1.1) -> Image.Image:
    """Adjusts image contrast.

    Args:
        img: Input PIL Image.
        factor: Contrast multiplier (1.0 = original, 1.3 = +30% contrast, 0.7 = reduced contrast).

    Returns:
        attacked_img: Contrast adjusted PIL Image.
    """
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(max(0.1, float(factor)))


def apply_gamma_attack(img: Image.Image, gamma: float = 1.1) -> Image.Image:
    """Applies non-linear gamma tone mapping: Output = 255 * (Input / 255)^gamma."""
    gamma = max(0.2, min(5.0, float(gamma)))
    arr = np.array(img, dtype=np.float64)

    if img.mode == "RGBA":
        rgb = arr[:, :, :3]
        corrected_rgb = 255.0 * ((rgb / 255.0) ** gamma)
        arr[:, :, :3] = np.clip(corrected_rgb, 0, 255)
    else:
        corrected = 255.0 * ((arr / 255.0) ** gamma)
        arr = np.clip(corrected, 0, 255)

    return Image.fromarray(arr.astype(np.uint8), mode=img.mode)

