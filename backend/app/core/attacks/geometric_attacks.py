"""Geometric Distortions: Resizing, Cropping, and Rotation Attacks."""

from typing import Tuple
import numpy as np
from PIL import Image


def apply_resizing_attack(
    img: Image.Image, scale_factor: float = 0.75, restore_dimensions: bool = True
) -> Image.Image:
    """Scales image down/up and resamples back to original dimensions.

    Args:
        img: Input PIL Image.
        scale_factor: Scaling multiplier (e.g. 0.75 for 75%, 1.25 for 125%).
        restore_dimensions: If True, bicubic resamples back to host dimensions for block alignment.

    Returns:
        attacked_img: Resampled PIL Image.
    """
    orig_w, orig_h = img.size
    new_w = max(8, int(orig_w * scale_factor))
    new_h = max(8, int(orig_h * scale_factor))

    # Downscale/upscale
    resized = img.resize((new_w, new_h), resample=Image.Resampling.BICUBIC)

    if restore_dimensions:
        # Restore original spatial dimensions to maintain block grid synchronization
        return resized.resize((orig_w, orig_h), resample=Image.Resampling.BICUBIC)

    return resized


def apply_cropping_attack(
    img: Image.Image, crop_percentage: float = 10.0, zero_fill: bool = True
) -> Image.Image:
    """Crops a percentage of the image borders and pads back to original size.

    Args:
        img: Input PIL Image.
        crop_percentage: Percentage of width/height to crop from edges (e.g. 5.0, 10.0).
        zero_fill: If True, pads cropped region with black pixels to maintain dimensions.

    Returns:
        attacked_img: Cropped & padded PIL Image.
    """
    crop_pct = max(0.0, min(45.0, float(crop_percentage))) / 100.0
    w, h = img.size

    pad_left = int(w * crop_pct / 2.0)
    pad_top = int(h * crop_pct / 2.0)
    crop_w = w - (2 * pad_left)
    crop_h = h - (2 * pad_top)

    # Crop central region
    box = (pad_left, pad_top, pad_left + crop_w, pad_top + crop_h)
    cropped_center = img.crop(box)

    if zero_fill:
        # Create blank canvas of original dimensions and paste cropped center
        canvas = Image.new(img.mode, (w, h), color=0)
        canvas.paste(cropped_center, (pad_left, pad_top))
        return canvas

    return cropped_center


def apply_rotation_attack(
    img: Image.Image, angle_degrees: float = 1.0, counter_rotate: bool = False
) -> Image.Image:
    """Rotates image by a small angle.

    Args:
        img: Input PIL Image.
        angle_degrees: Rotation angle in degrees (e.g. 0.5, 1.0, 2.0).
        counter_rotate: If True, applies reverse rotation to test post-synchronization recovery.

    Returns:
        attacked_img: Rotated PIL Image.
    """
    rotated = img.rotate(angle_degrees, resample=Image.Resampling.BILINEAR, expand=False)
    if counter_rotate:
        return rotated.rotate(-angle_degrees, resample=Image.Resampling.BILINEAR, expand=False)
    return rotated

