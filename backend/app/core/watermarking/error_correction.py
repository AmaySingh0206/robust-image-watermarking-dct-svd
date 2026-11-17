"""Reed-Solomon Forward Error Correction (FEC) and Bit/Byte Serialization.

Uses reedsolo with configurable parity symbols (default 32 parity bytes).
Provides byte-to-bit unpacking and bit-to-byte packing.
Detects and corrects byte-level corruptions caused by image compression and filtering.
"""

from typing import Tuple
import reedsolo
import numpy as np


class ErrorCorrectionEngine:
    """Manages Reed-Solomon FEC encoding, decoding, and bit conversions."""

    DEFAULT_PARITY_BYTES: int = 32

    def __init__(self, nsym: int = DEFAULT_PARITY_BYTES):
        self.nsym = nsym
        self.rsc = reedsolo.RSCodec(nsym)

    def encode(self, data: bytes) -> bytes:
        """Applies Reed-Solomon error correction to framed byte sequence.

        Args:
            data: Raw framed bytes.

        Returns:
            codeword_bytes: Encoded byte sequence with appended ECC parity symbols.
        """
        return bytes(self.rsc.encode(data))

    def decode(self, codeword: bytes) -> Tuple[bool, bytes, str]:
        """Attempts to correct errors and decode codeword bytes.

        Returns:
            (success, decoded_bytes, error_message)
        """
        try:
            decoded, decoded_full, errata_pos = self.rsc.decode(codeword)
            return True, bytes(decoded), f"Corrected {len(errata_pos)} byte error(s)."
        except reedsolo.ReedSolomonError as e:
            return False, b"", f"Reed-Solomon decoding failed: uncorrectable errors ({str(e)})."
        except Exception as e:
            return False, b"", f"FEC decoder exception: {str(e)}."

    @staticmethod
    def bytes_to_bits(data: bytes) -> np.ndarray:
        """Converts bytes to 1D numpy array of uint8 bits (0 or 1), MSB first."""
        byte_arr = np.frombuffer(data, dtype=np.uint8)
        # Unpack each byte into 8 bits: (N, 8) -> flatten to (N * 8,)
        return np.unpackbits(byte_arr)

    @staticmethod
    def bits_to_bytes(bits: np.ndarray) -> bytes:
        """Packs 1D numpy array of uint8 bits (0 or 1) back into bytes."""
        if len(bits) % 8 != 0:
            # Pad with zeros to nearest byte multiple
            pad_len = 8 - (len(bits) % 8)
            bits = np.pad(bits, (0, pad_len), mode="constant", constant_values=0)
        packed = np.packbits(bits)
        return bytes(packed.tobytes())

