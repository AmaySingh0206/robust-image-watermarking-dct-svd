"""Spatial Filtering Attacks: Gaussian Blur and Median Filtering."""

from PIL import Image, ImageFilter


def apply_gaussian_blur(img: Image.Image, radius: float = 1.0) -> Image.Image:
    """Applies Gaussian spatial low-pass filtering.

    Args:
        img: Input PIL Image.
        radius: Blur radius in pixels (approx std_dev).

    Returns:
        attacked_img: Blurred PIL Image.
    """
    radius = max(0.1, float(radius))
    return img.filter(ImageFilter.GaussianBlur(radius=radius))


def apply_median_filter(img: Image.Image, size: int = 3) -> Image.Image:
    """Applies non-linear median filtering to remove impulsive noise.

    Args:
        img: Input PIL Image.
        size: Kernel size (must be odd, e.g. 3 or 5).

    Returns:
        attacked_img: Filtered PIL Image.
    """
    size = int(size)
    if size % 2 == 0:
        size += 1
    size = max(3, min(9, size))
    return img.filter(ImageFilter.MedianFilter(size=size))

