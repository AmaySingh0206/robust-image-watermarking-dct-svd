"""Capacity estimation and feasibility analysis for DCT-SVD-QIM watermarking.

Evaluates how many bits and payload characters an image of dimensions (H, W)
can accommodate given block size (8x8), Reed-Solomon parity symbols, and repetition factor.
"""

from typing import Dict, Any, Tuple
import math


class CapacityEstimator:
    """Calculates embedding capacity and verifies message feasibility."""

    BLOCK_SIZE: int = 8
    HEADER_BYTES: int = 8      # Magic(4) + Version(1) + Flags(1) + Length(2)
    CRC_BYTES: int = 4         # CRC-32
    DEFAULT_PARITY_BYTES: int = 32
    MAX_PAYLOAD_LIMIT: int = 219

    @classmethod
    def get_total_blocks(cls, height: int, width: int) -> int:
        """Returns total non-overlapping 8x8 blocks available in the image."""
        return (height // cls.BLOCK_SIZE) * (width // cls.BLOCK_SIZE)

    @classmethod
    def calculate_required_blocks(
        cls, payload_len_bytes: int, repetition: int = 5, parity_bytes: int = DEFAULT_PARITY_BYTES
    ) -> int:
        """Calculates total 8x8 blocks required to embed a payload of given byte length."""
        total_codeword_bytes = cls.HEADER_BYTES + payload_len_bytes + cls.CRC_BYTES + parity_bytes
        total_bits = total_codeword_bytes * 8
        total_blocks = total_bits * repetition
        return total_blocks

    @classmethod
    def analyze_capacity(
        cls, height: int, width: int, repetition: int = 5, parity_bytes: int = DEFAULT_PARITY_BYTES
    ) -> Dict[str, Any]:
        """Provides a complete capacity report for an image at given repetition setting."""
        total_blocks = cls.get_total_blocks(height, width)
        overhead_bytes = cls.HEADER_BYTES + cls.CRC_BYTES + parity_bytes
        overhead_blocks = overhead_bytes * 8 * repetition

        if total_blocks < overhead_blocks:
            max_payload_bytes = 0
            feasible = False
        else:
            avail_blocks = total_blocks - overhead_blocks
            avail_bytes = avail_blocks // (8 * repetition)
            max_payload_bytes = min(cls.MAX_PAYLOAD_LIMIT, avail_bytes)
            feasible = max_payload_bytes > 0

        return {
            "image_dimensions": (height, width),
            "total_blocks": total_blocks,
            "repetition_factor": repetition,
            "overhead_bytes": overhead_bytes,
            "overhead_blocks": overhead_blocks,
            "max_payload_bytes": max_payload_bytes,
            "is_feasible": feasible,
            "recommended_min_dimension": math.ceil(math.sqrt(overhead_blocks * 64)),
        }

    @classmethod
    def validate_message_fit(
        cls, height: int, width: int, message: str, repetition: int = 5
    ) -> Tuple[bool, int, int]:
        """Checks if a UTF-8 message fits into the image.

        Returns:
            (fits, required_blocks, available_blocks)
        """
        payload_bytes = len(message.encode("utf-8"))
        if payload_bytes > cls.MAX_PAYLOAD_LIMIT:
            return False, 0, cls.get_total_blocks(height, width)

        req_blocks = cls.calculate_required_blocks(payload_bytes, repetition)
        avail_blocks = cls.get_total_blocks(height, width)
        return req_blocks <= avail_blocks, req_blocks, avail_blocks

