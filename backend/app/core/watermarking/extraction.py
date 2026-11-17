"""Watermark Blind Extraction and Verification Engine.

Extraction Pipeline (Host-Free):
  Watermarked/Attacked Image -> Luminance Separation -> 8x8 Block Division
                            -> 2D DCT -> Middle-Band SVD -> QIM Singular-Value Decision
                            -> HMAC Pseudorandom Scheduled Bit Extraction
                            -> Majority Voting -> Reed-Solomon FEC Decoding
                            -> Framing & CRC-32 Verification -> Extracted Payload Message.
"""

from typing import Dict, Any, Union, Optional
import time
import numpy as np
from PIL import Image

from backend.app.core.watermarking.preprocessing import ImagePreprocessor
from backend.app.core.watermarking.dct_transform import BlockDCTTransformer
from backend.app.core.watermarking.svd_transform import SVDTransformer
from backend.app.core.watermarking.qim import QIMModulator
from backend.app.core.watermarking.key_management import KeyManager
from backend.app.core.watermarking.framing import PayloadFramer
from backend.app.core.watermarking.error_correction import ErrorCorrectionEngine


class WatermarkExtractor:
    """Performs blind extraction and forensic payload verification without host image."""

    @classmethod
    def extract(
        cls,
        image_input: Union[bytes, Image.Image],
        secret_key: str,
        manifest: Dict[str, Any],
        ground_truth_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Performs blind watermark extraction.

        Args:
            image_input: Watermarked (or attacked) image bytes or PIL Image.
            secret_key: The user's secret watermark key.
            manifest: Non-secret algorithm recovery manifest.
            ground_truth_message: Optional expected message for ground-truth BER calculation.

        Returns:
            result_dict: Extraction status, recovered message, confidence, BER, NC, diagnostics.
        """
        start_time = time.perf_counter()

        # 1. Manifest Validation
        required_keys = ["quantization_step", "repetition_factor", "codeword_bits_count", "total_embedded_bits"]
        for k in required_keys:
            if k not in manifest:
                return {
                    "status": "invalid_manifest",
                    "success": False,
                    "message": None,
                    "error": f"Missing required recovery parameter: '{k}' in manifest",
                    "execution_time_seconds": round(time.perf_counter() - start_time, 4),
                }

        delta = float(manifest["quantization_step"])
        repetition = int(manifest["repetition_factor"])
        codeword_bits_count = int(manifest["codeword_bits_count"])
        required_blocks = int(manifest["total_embedded_bits"])
        parity_bytes = int(manifest.get("parity_bytes", 32))

        # 2. Ingest and Decompose Image
        if isinstance(image_input, bytes):
            img = ImagePreprocessor.load_image(image_input)
        else:
            img = image_input

        lum, _, _, _, _ = ImagePreprocessor.decompose_channels(img)
        padded_lum, padded_shape = ImagePreprocessor.pad_to_block_multiple(lum, block_size=8)
        H_pad, W_pad = padded_shape
        total_blocks = (H_pad // 8) * (W_pad // 8)

        if total_blocks < required_blocks:
            return {
                "status": "dimension_mismatch",
                "success": False,
                "message": None,
                "error": f"Image has {total_blocks} blocks, but watermark manifest requires {required_blocks} blocks.",
                "execution_time_seconds": round(time.perf_counter() - start_time, 4),
            }

        # 3. Derive Key-Based Deterministic Block Selection
        try:
            selected_block_indices = KeyManager.select_blocks_for_embedding(
                secret_key=secret_key,
                total_blocks=total_blocks,
                required_blocks=required_blocks,
            )
        except Exception as e:
            return {
                "status": "key_error",
                "success": False,
                "message": None,
                "error": str(e),
                "execution_time_seconds": round(time.perf_counter() - start_time, 4),
            }

        # 4. 2D DCT on Blocks
        blocks, _ = BlockDCTTransformer.image_to_blocks(padded_lum)
        dct_blocks = BlockDCTTransformer.forward_dct_batch(blocks)

        # 5. Extract Middle Band & Compute SVD
        selected_bands = SVDTransformer.extract_middle_band_batch(dct_blocks[selected_block_indices])
        _, S, _ = SVDTransformer.decompose_batch(selected_bands)
        s1_candidates = S[:, 0]

        # 6. QIM Decision on Received Singular Values
        raw_bits, raw_confidences = QIMModulator.extract_batch(s1_candidates, delta)

        # 7. Majority Voting across Repetition Factor R
        # Reshape to (codeword_bits_count, repetition)
        repeated_groups = raw_bits.reshape(codeword_bits_count, repetition)
        # Sum votes for 1 in each group
        ones_votes = np.sum(repeated_groups, axis=1)
        majority_threshold = repetition / 2.0
        voted_bits = np.where(ones_votes > majority_threshold, 1, 0).astype(np.uint8)

        # Compute mean confidence
        mean_confidence = float(np.mean(np.abs(raw_confidences)))

        # 8. Reed-Solomon Forward Error Correction
        candidate_codeword_bytes = ErrorCorrectionEngine.bits_to_bytes(voted_bits)
        fec = ErrorCorrectionEngine(nsym=parity_bytes)
        fec_success, decoded_framed_bytes, fec_info = fec.decode(candidate_codeword_bytes)

        if not fec_success:
            return {
                "status": "corrupted",
                "success": False,
                "message": None,
                "error": f"Payload corrupted or incorrect key. {fec_info}",
                "mean_confidence": round(mean_confidence, 4),
                "fec_status": fec_info,
                "execution_time_seconds": round(time.perf_counter() - start_time, 4),
            }

        # 9. CRC-32 & Framing Verification
        frame_valid, message, frame_info = PayloadFramer.unframe_payload(decoded_framed_bytes)

        elapsed_time = time.perf_counter() - start_time

        if not frame_valid:
            return {
                "status": "corrupted",
                "success": False,
                "message": None,
                "error": f"Integrity check failed: {frame_info}",
                "mean_confidence": round(mean_confidence, 4),
                "fec_status": fec_info,
                "execution_time_seconds": round(elapsed_time, 4),
            }

        # 10. Optional Ground Truth Evaluation
        ber_value = None
        nc_value = None
        if ground_truth_message is not None:
            from backend.app.core.evaluation.ber import calculate_ber
            from backend.app.core.evaluation.nc import calculate_nc

            gt_framed = PayloadFramer.frame_payload(ground_truth_message)
            gt_codeword = fec.encode(gt_framed)
            gt_bits = ErrorCorrectionEngine.bytes_to_bits(gt_codeword)
            if len(gt_bits) == len(voted_bits):
                ber_value = round(calculate_ber(gt_bits, voted_bits), 2)
                nc_value = round(calculate_nc(gt_bits, voted_bits), 4)

        return {
            "status": "success",
            "success": True,
            "message": message,
            "error": None,
            "mean_confidence": round(mean_confidence, 4),
            "fec_status": fec_info,
            "ber_percentage": ber_value,
            "nc": nc_value,
            "execution_time_seconds": round(elapsed_time, 4),
        }

