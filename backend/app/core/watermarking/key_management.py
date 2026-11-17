"""Cryptographic Key Management and Deterministic Block Permutation.

Uses HMAC-SHA256 to derive a deterministic pseudorandom permutation of block indices
from a user secret key.
Strict security rules:
- Keys are never logged, persisted, or returned in manifests.
- Permutation is completely deterministic given the same key and block count.
- Wrong keys produce uncorrelated permutations resulting in failed checksums.
"""

from typing import List
import hashlib
import hmac
import numpy as np


class KeyManager:
    """Manages secret-key expansion and deterministic block scheduling."""

    DOMAIN_SEPARATOR = b"SPECTRAMARK-DETERMINISTIC-BLOCK-SCHEDULE-v1"

    @classmethod
    def derive_seed_from_key(cls, secret_key: str) -> int:
        """Derives a 64-bit integer seed from a user secret key via HMAC-SHA256."""
        if not secret_key:
            raise ValueError("Secret key cannot be empty")

        key_bytes = secret_key.encode("utf-8")
        h = hmac.new(key_bytes, cls.DOMAIN_SEPARATOR, hashlib.sha256).digest()
        # Take the first 8 bytes as an unsigned 64-bit integer
        seed = int.from_bytes(h[:8], byteorder="big", signed=False)
        return seed

    @classmethod
    def get_block_permutation(cls, secret_key: str, total_blocks: int) -> np.ndarray:
        """Generates a pseudorandom permutation of block indices [0 ... total_blocks - 1].

        Args:
            secret_key: The user's confidential passphrase.
            total_blocks: Total number of 8x8 blocks available in the image.

        Returns:
            permutation: 1D numpy array of length total_blocks containing unique indices.
        """
        if total_blocks <= 0:
            raise ValueError(f"Total blocks must be positive, got {total_blocks}")

        seed = cls.derive_seed_from_key(secret_key)
        # Use PCG64 PRNG seeded with cryptographic HMAC output
        rng = np.random.Generator(np.random.PCG64(seed))
        permutation = rng.permutation(total_blocks)
        return permutation

    @classmethod
    def select_blocks_for_embedding(
        cls, secret_key: str, total_blocks: int, required_blocks: int
    ) -> np.ndarray:
        """Selects a subset of required_blocks using the deterministic key sequence.

        Raises:
            ValueError if required_blocks exceeds total_blocks (insufficient capacity).
        """
        if required_blocks > total_blocks:
            raise ValueError(
                f"Image capacity exceeded: requires {required_blocks} blocks, "
                f"but image only has {total_blocks} blocks."
            )

        permutation = cls.get_block_permutation(secret_key, total_blocks)
        return permutation[:required_blocks]

