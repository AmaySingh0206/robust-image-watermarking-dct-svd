"""Vectorized 2D Discrete Cosine Transform (DCT) and Inverse DCT (IDCT) on 8x8 blocks.

Implements block-based orthogonal DCT-II:
- Divides luminance matrix into non-overlapping 8x8 blocks.
- Vectorized computation across all blocks simultaneously using scipy.fft.dctn / idctn.
- DC coefficient C(0, 0) represents average block luminance.
- Middle-frequency submatrix C[2:6, 2:6] isolates robust frequencies.
"""

from typing import Tuple
import numpy as np
from scipy.fft import dctn, idctn


class BlockDCTTransformer:
    """Performs vectorized 2D DCT and IDCT on non-overlapping 8x8 spatial blocks."""

    BLOCK_SIZE = 8

    @classmethod
    def image_to_blocks(cls, image_2d: np.ndarray) -> Tuple[np.ndarray, Tuple[int, int]]:
        """Deconstructs a 2D image (H, W) into an array of (N_blocks, 8, 8) blocks.

        Args:
            image_2d: 2D numpy array of shape (H, W) where H and W are multiples of 8.

        Returns:
            blocks: numpy array of shape (N_blocks, 8, 8)
            grid_shape: (num_blocks_h, num_blocks_w)
        """
        H, W = image_2d.shape
        if H % cls.BLOCK_SIZE != 0 or W % cls.BLOCK_SIZE != 0:
            raise ValueError(f"Dimensions ({H}, {W}) must be divisible by {cls.BLOCK_SIZE}")

        Nh = H // cls.BLOCK_SIZE
        Nw = W // cls.BLOCK_SIZE

        # Reshape to (Nh, 8, Nw, 8) -> transpose to (Nh, Nw, 8, 8) -> reshape to (Nh * Nw, 8, 8)
        blocks = (
            image_2d.reshape(Nh, cls.BLOCK_SIZE, Nw, cls.BLOCK_SIZE)
            .transpose(0, 2, 1, 3)
            .reshape(Nh * Nw, cls.BLOCK_SIZE, cls.BLOCK_SIZE)
        )
        return blocks, (Nh, Nw)

    @classmethod
    def blocks_to_image(cls, blocks: np.ndarray, grid_shape: Tuple[int, int]) -> np.ndarray:
        """Reconstructs 2D image array of shape (H, W) from (N_blocks, 8, 8) blocks."""
        Nh, Nw = grid_shape
        N_blocks = Nh * Nw
        if blocks.shape[0] != N_blocks:
            raise ValueError(f"Expected {N_blocks} blocks for grid {grid_shape}, got {blocks.shape[0]}")

        # Reshape to (Nh, Nw, 8, 8) -> transpose to (Nh, 8, Nw, 8) -> reshape to (Nh*8, Nw*8)
        image_2d = (
            blocks.reshape(Nh, Nw, cls.BLOCK_SIZE, cls.BLOCK_SIZE)
            .transpose(0, 2, 1, 3)
            .reshape(Nh * cls.BLOCK_SIZE, Nw * cls.BLOCK_SIZE)
        )
        return image_2d

    @classmethod
    def forward_dct_batch(cls, blocks: np.ndarray) -> np.ndarray:
        """Computes orthonormal 2D DCT-II on a batch of 8x8 blocks (N_blocks, 8, 8).

        Returns:
            dct_blocks: shape (N_blocks, 8, 8) with float64 precision.
        """
        # Vectorized DCT on the last two dimensions
        return dctn(blocks, axes=(-2, -1), norm="ortho")

    @classmethod
    def inverse_dct_batch(cls, dct_blocks: np.ndarray) -> np.ndarray:
        """Computes orthonormal 2D IDCT-II on a batch of 8x8 blocks (N_blocks, 8, 8).

        Returns:
            spatial_blocks: shape (N_blocks, 8, 8) with float64 precision.
        """
        # Vectorized IDCT on the last two dimensions
        return idctn(dct_blocks, axes=(-2, -1), norm="ortho")

