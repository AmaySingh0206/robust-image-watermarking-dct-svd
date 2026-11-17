"""Singular Value Decomposition (SVD) on Middle-Frequency DCT Submatrices.

Extracts middle-frequency band M = C[2:6, 2:6] from each 8x8 DCT block.
Performs SVD: M = U * S * Vt.
Modifies designated singular value feature (principal singular value s1).
Reconstructs M' = U * S' * Vt.
Reinserts into DCT block preserving DC and unaffected frequencies.
"""

from typing import Tuple
import numpy as np


class SVDTransformer:
    """Manages SVD operations on selected middle-frequency DCT coefficient submatrices."""

    ROW_START = 2
    ROW_END = 6
    COL_START = 2
    COL_END = 6

    @classmethod
    def extract_middle_band(cls, dct_block: np.ndarray) -> np.ndarray:
        """Extracts 4x4 middle-frequency submatrix from single 8x8 DCT block."""
        return dct_block[cls.ROW_START:cls.ROW_END, cls.COL_START:cls.COL_END].copy()

    @classmethod
    def extract_middle_band_batch(cls, dct_blocks: np.ndarray) -> np.ndarray:
        """Extracts 4x4 middle-frequency submatrices from batch of blocks (N, 8, 8).

        Returns:
            submatrices: shape (N, 4, 4)
        """
        return dct_blocks[:, cls.ROW_START:cls.ROW_END, cls.COL_START:cls.COL_END].copy()

    @classmethod
    def reinsert_middle_band(cls, dct_block: np.ndarray, modified_band: np.ndarray) -> np.ndarray:
        """Reinserts 4x4 modified middle-frequency submatrix back into 8x8 DCT block."""
        reconstructed = dct_block.copy()
        reconstructed[cls.ROW_START:cls.ROW_END, cls.COL_START:cls.COL_END] = modified_band
        return reconstructed

    @classmethod
    def reinsert_middle_band_batch(
        cls, dct_blocks: np.ndarray, modified_bands: np.ndarray
    ) -> np.ndarray:
        """Reinserts (N, 4, 4) modified middle-frequency submatrices into (N, 8, 8) DCT blocks."""
        reconstructed = dct_blocks.copy()
        reconstructed[:, cls.ROW_START:cls.ROW_END, cls.COL_START:cls.COL_END] = modified_bands
        return reconstructed

    @classmethod
    def decompose_batch(cls, bands: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Decomposes batch of 4x4 submatrices into U, S, Vt using vectorized SVD.

        Args:
            bands: shape (N, 4, 4)

        Returns:
            U: shape (N, 4, 4)
            S: shape (N, 4) singular values in descending order
            Vt: shape (N, 4, 4)
        """
        U, S, Vt = np.linalg.svd(bands, full_matrices=True)
        return U, S, Vt

    @classmethod
    def reconstruct_batch(cls, U: np.ndarray, S_modified: np.ndarray, Vt: np.ndarray) -> np.ndarray:
        """Reconstructs batch of 4x4 submatrices from U, modified S, and Vt.

        Args:
            U: shape (N, 4, 4)
            S_modified: shape (N, 4) modified singular values
            Vt: shape (N, 4, 4)

        Returns:
            bands_reconstructed: shape (N, 4, 4)
        """
        # Vectorized matrix product: U @ diag(S) @ Vt
        # Equivalent to: (U * S_modified[:, None, :]) @ Vt
        return np.matmul(U * S_modified[:, np.newaxis, :], Vt)

