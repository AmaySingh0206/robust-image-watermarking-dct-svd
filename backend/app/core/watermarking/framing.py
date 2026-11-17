"""Binary Payload Framing and CRC-32 Integrity Verification.

Frame Structure:
  - MAGIC (4 bytes): b'SPEC'
  - VERSION (1 byte): 0x01
  - FLAGS (1 byte): 0x00 (Standard UTF-8 payload)
  - PAYLOAD_LEN (2 bytes): Big-endian unsigned 16-bit int
  - PAYLOAD (L bytes): UTF-8 message
  - CRC32 (4 bytes): CRC-32 computed over preceding fields
"""

from typing import Tuple
import struct
import zlib


class PayloadFramer:
    """Encapsulates payload creation, binary framing, and cryptographic integrity checks."""

    MAGIC: bytes = b"SPEC"
    VERSION: int = 1
    FLAG_UTF8: int = 0
    MAX_PAYLOAD_BYTES: int = 219  # Strict limit ensuring compatibility with Reed-Solomon (255 byte GF(2^8) symbol limit)

    @classmethod
    def frame_payload(cls, message: str) -> bytes:
        """Constructs framed binary byte sequence with CRC-32 checksum.

        Args:
            message: UTF-8 string payload.

        Returns:
            framed_bytes: Binary bytes containing Magic, Version, Flags, Length, Message, CRC32.
        """
        payload_bytes = message.encode("utf-8")
        if len(payload_bytes) > cls.MAX_PAYLOAD_BYTES:
            raise ValueError(
                f"Payload size ({len(payload_bytes)} bytes) exceeds maximum allowable limit "
                f"of {cls.MAX_PAYLOAD_BYTES} bytes."
            )

        length = len(payload_bytes)
        # Header: Magic(4s), Version(B), Flags(B), Length(H)
        header = struct.pack(">4sBBH", cls.MAGIC, cls.VERSION, cls.FLAG_UTF8, length)
        body = header + payload_bytes
        # CRC32 checksum over header + payload
        checksum = zlib.crc32(body) & 0xFFFFFFFF
        checksum_bytes = struct.pack(">I", checksum)

        return body + checksum_bytes

    @classmethod
    def unframe_payload(cls, framed_bytes: bytes) -> Tuple[bool, str, str]:
        """Validates framing, extracts payload, and verifies CRC-32 integrity.

        Returns:
            (is_valid, message, status_details)
        """
        if len(framed_bytes) < 12:  # Min length: 4 (magic) + 1 (ver) + 1 (flag) + 2 (len) + 0 (payload) + 4 (crc)
            return False, "", "Corrupted frame: bytes too short."

        magic, version, flags, length = struct.unpack(">4sBBH", framed_bytes[:8])
        if magic != cls.MAGIC:
            return False, "", f"Invalid magic header: expected {cls.MAGIC!r}, got {magic!r} (wrong key or no watermark)."

        if version != cls.VERSION:
            return False, "", f"Unsupported protocol version: {version}."

        expected_total_len = 8 + length + 4
        if len(framed_bytes) < expected_total_len:
            return False, "", f"Truncated frame: expected {expected_total_len} bytes, got {len(framed_bytes)}."

        body = framed_bytes[: 8 + length]
        received_crc = struct.unpack(">I", framed_bytes[8 + length : 8 + length + 4])[0]
        calculated_crc = zlib.crc32(body) & 0xFFFFFFFF

        if received_crc != calculated_crc:
            return False, "", f"CRC32 mismatch: expected {hex(calculated_crc)}, received {hex(received_crc)} (payload corrupted)."

        try:
            payload_str = body[8:].decode("utf-8")
            return True, payload_str, "Payload successfully extracted and verified."
        except UnicodeDecodeError as e:
            return False, "", f"UTF-8 decoding failed: {str(e)}."

