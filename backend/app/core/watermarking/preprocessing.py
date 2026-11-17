"""Image preprocessing, color space conversion, channel handling, and block padding.

Strictly classical Digital Image Processing:
- Reads and validates images (PNG, JPEG, TIFF, WebP).
- Corrects EXIF orientation.
- Separates and preserves Alpha channel if present.
- Converts RGB to YCbCr (ITU-R BT.601) for luminance-channel embedding.
- Handles Grayscale natively.
- Performs dimension padding to multiples of 8x8 non-overlapping blocks.
- Crops reconstructed luminance back to exact original dimensions.
"""

from typing import Tuple, Optional
import io
import numpy as np
from PIL import Image, ImageOps


class ImagePreprocessor:
    """Handles image ingestion, color transformation, and spatial block alignment."""

    # ITU-R BT.601 conversion matrices
    RGB_TO_YCBCR = np.array([
        [0.299000,  0.587000,  0.114000],
        [-0.168736, -0.331264,  0.500000],
        [0.500000, -0.418688, -0.081312]
    ], dtype=np.float64)

    YCBCR_TO_RGB = np.linalg.inv(RGB_TO_YCBCR)

    YCBCR_OFFSET = np.array([0.0, 128.0, 128.0], dtype=np.float64)

    @classmethod
    def load_image(cls, image_bytes: bytes) -> Image.Image:
        """Loads and validates an image from raw bytes with EXIF transposition."""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            # Transpose based on EXIF tag if present
            img = ImageOps.exif_transpose(img)
            return img
        except Exception as e:
            raise ValueError(f"Failed to decode image: {str(e)}")

    @classmethod
    def decompose_channels(
        cls, img: Image.Image
    ) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray], str, Tuple[int, int]]:
        """Decomposes an image into (luminance_Y, chrominance_CbCr, alpha_channel, mode, original_shape).

        Returns:
            luminance: 2D float64 array of shape (H, W) in [0, 255]
            chrominance: 3D float64 array (H, W, 2) for Cb and Cr, or None for grayscale
            alpha: 2D uint8 array (H, W) if present, else None
            mode: 'RGB', 'RGBA', or 'L'
            original_shape: (H, W)
        """
        raw_mode = img.mode
        alpha = None

        if raw_mode == "RGBA":
            alpha = np.array(img.getchannel("A"), dtype=np.uint8)
            rgb_img = img.convert("RGB")
            mode = "RGBA"
        elif raw_mode == "RGB":
            rgb_img = img
            mode = "RGB"
        elif raw_mode in ("L", "1"):
            gray_img = img.convert("L")
            mode = "L"
            arr = np.array(gray_img, dtype=np.float64)
            return arr, None, None, mode, arr.shape
        elif raw_mode == "P":
            # Palette image
            converted = img.convert("RGBA" if "transparency" in img.info else "RGB")
            return cls.decompose_channels(converted)
        else:
            rgb_img = img.convert("RGB")
            mode = "RGB"

        rgb_arr = np.array(rgb_img, dtype=np.float64)
        H, W, _ = rgb_arr.shape

        # Convert RGB to YCbCr using vectorized dot product
        # ycbcr = rgb @ RGB_TO_YCBCR.T + YCBCR_OFFSET
        ycbcr = np.dot(rgb_arr, cls.RGB_TO_YCBCR.T) + cls.YCBCR_OFFSET

        luminance = ycbcr[:, :, 0]
        chrominance = ycbcr[:, :, 1:3]  # Cb, Cr

        return luminance, chrominance, alpha, mode, (H, W)

    @classmethod
    def reconstruct_image(
        cls,
        luminance: np.ndarray,
        chrominance: Optional[np.ndarray],
        alpha: Optional[np.ndarray],
        mode: str,
        target_shape: Tuple[int, int]
    ) -> Image.Image:
        """Reconstructs a PIL Image from modified luminance and original chrominance/alpha."""
        H, W = target_shape
        # Unpad / crop back to exact target dimensions
        y = luminance[:H, :W]

        if mode == "L" or chrominance is None:
            clipped_y = np.clip(np.round(y), 0, 255).astype(np.uint8)
            return Image.fromarray(clipped_y, mode="L")

        cb_cr = chrominance[:H, :W, :]
        ycbcr = np.zeros((H, W, 3), dtype=np.float64)
        ycbcr[:, :, 0] = y
        ycbcr[:, :, 1:3] = cb_cr

        # Inverse color transform to RGB: (ycbcr - offset) @ YCBCR_TO_RGB.T
        rgb_arr = np.dot(ycbcr - cls.YCBCR_OFFSET, cls.YCBCR_TO_RGB.T)
        rgb_clipped = np.clip(np.round(rgb_arr), 0, 255).astype(np.uint8)

        if mode == "RGBA" and alpha is not None:
            a_cropped = alpha[:H, :W]
            rgba_arr = np.dstack([rgb_clipped, a_cropped])
            return Image.fromarray(rgba_arr, mode="RGBA")

        return Image.fromarray(rgb_clipped, mode="RGB")

    @classmethod
    def pad_to_block_multiple(
        cls, channel: np.ndarray, block_size: int = 8
    ) -> Tuple[np.ndarray, Tuple[int, int]]:
        """Pads a 2D channel symmetrically so its dimensions are divisible by block_size."""
        H, W = channel.shape
        pad_h = (block_size - (H % block_size)) % block_size
        pad_w = (block_size - (W % block_size)) % block_size

        if pad_h == 0 and pad_w == 0:
            return channel, (H, W)

        # Pad bottom and right symmetrically
        padded = np.pad(channel, ((0, pad_h), (0, pad_w)), mode="reflect")
        return padded, (H, W)

    @classmethod
    def unpad(cls, channel: np.ndarray, original_shape: Tuple[int, int]) -> np.ndarray:
        """Crops padded 2D channel back to original dimensions."""
        H, W = original_shape
        return channel[:H, :W]

