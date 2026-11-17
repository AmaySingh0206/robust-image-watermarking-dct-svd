"""Additive Gaussian Noise and Salt-and-Pepper Impulse Noise Attacks."""

import numpy as np
from PIL import Image


def apply_gaussian_noise(img: Image.Image, mean: float = 0.0, std_dev: float = 10.0) -> Image.Image:
    """Adds zero-mean additive Gaussian noise to the image.

    Args:
        img: Input PIL Image.
        mean: Gaussian mean (default 0.0).
        std_dev: Gaussian standard deviation (intensity).

    Returns:
        attacked_img: Noisy PIL Image.
    """
    arr = np.array(img, dtype=np.float64)

    if img.mode == "RGBA":
        # Apply noise to RGB only, preserving alpha
        noise = np.random.normal(mean, std_dev, arr[:, :, :3].shape)
        arr[:, :, :3] += noise
        arr[:, :, :3] = np.clip(arr[:, :, :3], 0, 255)
    else:
        noise = np.random.normal(mean, std_dev, arr.shape)
        arr += noise
        arr = np.clip(arr, 0, 255)

    return Image.fromarray(arr.astype(np.uint8), mode=img.mode)


def apply_salt_and_pepper_noise(img: Image.Image, density: float = 0.01) -> Image.Image:
    """Adds impulse salt-and-pepper noise to the image.

    Args:
        img: Input PIL Image.
        density: Proportion of pixels corrupted by noise in [0.0, 1.0].

    Returns:
        attacked_img: Noisy PIL Image.
    """
    density = max(0.0, min(1.0, float(density)))
    arr = np.array(img).copy()

    H, W = arr.shape[:2]
    num_noisy = int(density * H * W)
    if num_noisy == 0:
        return img

    # Half salt (255), half pepper (0)
    num_salt = num_noisy // 2
    num_pepper = num_noisy - num_salt

    # Salt
    salt_y = np.random.randint(0, H, num_salt)
    salt_x = np.random.randint(0, W, num_salt)
    if arr.ndim == 3:
        arr[salt_y, salt_x, :3] = 255
    else:
        arr[salt_y, salt_x] = 255

    # Pepper
    pep_y = np.random.randint(0, H, num_pepper)
    pep_x = np.random.randint(0, W, num_pepper)
    if arr.ndim == 3:
        arr[pep_y, pep_x, :3] = 0
    else:
        arr[pep_y, pep_x] = 0

    return Image.fromarray(arr, mode=img.mode)

