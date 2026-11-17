"""Quantization Index Modulation (QIM) for Scalar Singular-Value Embedding and Blind Extraction.

Mathematical lattices for positive singular values (sigma >= 0):
  Lambda_0 = { 2 * n * Delta | n >= 1 }       = { 2*Delta, 4*Delta, 6*Delta, ... } for bit 0 (even multiples)
  Lambda_1 = { (2 * n + 1) * Delta | n >= 0 } = { 1*Delta, 3*Delta, 5*Delta, ... } for bit 1 (odd multiples)

Properties:
  - Preserves positive singular values without rank collapse.
  - Uniform Euclidean decision margin (Delta / 2) between adjacent lattice points.
  - Vectorized embedding on batches of singular values.
  - Blind extraction with Euclidean distance decision.
  - Soft confidence calculation.
"""

from typing import Tuple, Dict
import numpy as np


class QIMModulator:
    """Implements scalar Quantization Index Modulation for singular value features."""

    PROFILES: Dict[str, float] = {
        "high_quality": 10.0,      # PSNR >= 50 dB, SSIM >= 0.995
        "balanced": 14.0,          # PSNR >= 46 dB, SSIM >= 0.990
        "high_robustness": 22.0,   # PSNR >= 40 dB, SSIM >= 0.980
    }

    @classmethod
    def get_delta_for_profile(cls, profile: str) -> float:
        """Retrieves quantization step size Delta for a given profile name."""
        return cls.PROFILES.get(profile.lower(), cls.PROFILES["balanced"])

    @classmethod
    def embed_bit(cls, s_val: float, bit: int, delta: float) -> float:
        """Embeds single binary bit (0 or 1) into singular value s_val via positive QIM."""
        if bit not in (0, 1):
            raise ValueError(f"Bit must be 0 or 1, got {bit}")

        if bit == 0:
            q = np.round(s_val / (2.0 * delta)) * (2.0 * delta)
            q = max(q, 2.0 * delta)
        else:
            q = np.round((s_val - delta) / (2.0 * delta)) * (2.0 * delta) + delta
            q = max(q, 1.0 * delta)

        return float(q)

    @classmethod
    def embed_batch(cls, s_vals: np.ndarray, bits: np.ndarray, delta: float) -> np.ndarray:
        """Vectorized embedding of binary bits into an array of principal singular values.

        Args:
            s_vals: 1D array of shape (N,) containing singular values sigma_1.
            bits: 1D array of shape (N,) containing bits in {0, 1}.
            delta: quantization step size Delta > 0.

        Returns:
            s_modified: 1D array of shape (N,)
        """
        if len(s_vals) != len(bits):
            raise ValueError(f"Length mismatch: {len(s_vals)} values vs {len(bits)} bits")

        # Bit 0 -> even multiples >= 2*delta
        q0 = np.round(s_vals / (2.0 * delta)) * (2.0 * delta)
        q0 = np.maximum(q0, 2.0 * delta)

        # Bit 1 -> odd multiples >= 1*delta
        q1 = np.round((s_vals - delta) / (2.0 * delta)) * (2.0 * delta) + delta
        q1 = np.maximum(q1, 1.0 * delta)

        s_modified = np.where(bits == 0, q0, q1)
        return s_modified

    @classmethod
    def extract_bit(cls, s_val: float, delta: float) -> Tuple[int, float]:
        """Extracts bit from singular value feature without original image.

        Returns:
            bit: 0 or 1
            confidence: float in [-1, 1] where >0 favors 0, <0 favors 1
        """
        q0 = max(np.round(s_val / (2.0 * delta)) * (2.0 * delta), 2.0 * delta)
        d0 = abs(s_val - q0)

        q1 = max(np.round((s_val - delta) / (2.0 * delta)) * (2.0 * delta) + delta, 1.0 * delta)
        d1 = abs(s_val - q1)

        bit = 0 if d0 <= d1 else 1
        confidence = (d1 - d0) / delta
        return bit, float(confidence)

    @classmethod
    def extract_batch(cls, s_vals: np.ndarray, delta: float) -> Tuple[np.ndarray, np.ndarray]:
        """Vectorized blind extraction of bits and confidence scores from an array of singular values.

        Args:
            s_vals: 1D array of shape (N,) containing candidate singular values.
            delta: quantization step size Delta > 0.

        Returns:
            bits: 1D array of shape (N,) with elements in {0, 1}.
            confidences: 1D array of shape (N,) with normalized decision margins.
        """
        q0 = np.maximum(np.round(s_vals / (2.0 * delta)) * (2.0 * delta), 2.0 * delta)
        d0 = np.abs(s_vals - q0)

        q1 = np.maximum(
            np.round((s_vals - delta) / (2.0 * delta)) * (2.0 * delta) + delta, 1.0 * delta
        )
        d1 = np.abs(s_vals - q1)

        bits = np.where(d0 <= d1, 0, 1).astype(np.uint8)
        confidences = (d1 - d0) / delta
        return bits, confidences
