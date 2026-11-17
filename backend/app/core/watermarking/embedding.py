"""Watermark Embedding Engine using DCT, SVD, and QIM.

Complete blind invisible watermarking pipeline:
  Host Image -> Color Decomp (YCbCr) -> 8x8 Block Division -> Vectorized 2D DCT
             -> Middle-Band SVD -> QIM Singular Value Embedding (HMAC Scheduled)
             -> Vectorized SVD Reconstruction -> Vectorized 2D IDCT -> Color Reassembly
             -> Watermarked Image + Non-Secret Recovery Manifest.
"""

from typing import Tuple, Dict, Any, Union
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
from backend.app.core.watermarking.capacity import CapacityEstimator


class WatermarkEmbedder:
    """Orchestrates mathematical DCT-SVD-QIM watermark embedding."""

    @classmethod
    def embed(
        cls,
        image_input: Union[bytes, Image.Image],
        message: str,
        secret_key: str,
        strength_profile: str = "balanced",
        repetition: int = 5,
        parity_bytes: int = 32,
    ) -> Tuple[Image.Image, Dict[str, Any], Dict[str, Any]]:
        """Embeds an invisible digital watermark into the host image.

        Args:
            image_input: Image bytes or PIL Image.
            message: Copyright ownership message or digital asset identifier.
            secret_key: Confidential passphrase for HMAC block permutation.
            strength_profile: 'high_quality', 'balanced', or 'high_robustness'.
            repetition: Repetition factor (3, 5, or 7). Default is 5.
            parity_bytes: Reed-Solomon parity symbols. Default is 32.

        Returns:
            watermarked_image: PIL Image object.
            recovery_manifest: Non-secret dictionary containing extraction parameters.
            metrics: Execution metrics including processing time, PSNR, SSIM.
        """
        start_time = time.perf_counter()

        # 1. Image Ingestion
        if isinstance(image_input, bytes):
            img = ImagePreprocessor.load_image(image_input)
        else:
            img = image_input

        # 2. Decompose channels (luminance Y, chrominance CbCr, alpha)
        lum_orig, cbcr, alpha, mode, orig_shape = ImagePreprocessor.decompose_channels(img)
        H_orig, W_orig = orig_shape

        # 3. Framing & Reed-Solomon Error Correction
        framed_data = PayloadFramer.frame_payload(message)
        fec = ErrorCorrectionEngine(nsym=parity_bytes)
        codeword_bytes = fec.encode(framed_data)
        codeword_bits = ErrorCorrectionEngine.bytes_to_bits(codeword_bytes)
        num_codeword_bits = len(codeword_bits)

        # 4. Repetition Expansion: repeat each bit R times
        # Shape: (num_codeword_bits, repetition) -> flatten to (num_codeword_bits * repetition,)
        repeated_bits = np.repeat(codeword_bits, repetition)
        required_blocks = len(repeated_bits)

        # 5. Capacity Verification
        padded_lum, padded_shape = ImagePreprocessor.pad_to_block_multiple(lum_orig, block_size=8)
        H_pad, W_pad = padded_shape
        total_blocks = (H_pad // 8) * (W_pad // 8)

        if required_blocks > total_blocks:
            raise ValueError(
                f"Image capacity exceeded: image has {total_blocks} blocks, but watermark payload "
                f"requires {required_blocks} blocks (repetition={repetition}). Please reduce message "
                f"length or choose a lower repetition factor."
            )

        # 6. Key-Based Deterministic Block Selection
        selected_block_indices = KeyManager.select_blocks_for_embedding(
            secret_key=secret_key,
            total_blocks=total_blocks,
            required_blocks=required_blocks,
        )

        # 7. Vectorized 2D DCT on all 8x8 spatial blocks
        blocks, grid_shape = BlockDCTTransformer.image_to_blocks(padded_lum)
        dct_blocks = BlockDCTTransformer.forward_dct_batch(blocks)

        # 8. SVD on Middle-Frequency Submatrices of Selected Blocks
        selected_bands = SVDTransformer.extract_middle_band_batch(dct_blocks[selected_block_indices])
        U, S, Vt = SVDTransformer.decompose_batch(selected_bands)

        # 9. QIM Modulation on Principal Singular Value (sigma_1)
        delta = QIMModulator.get_delta_for_profile(strength_profile)
        s1_original = S[:, 0]
        s1_modified = QIMModulator.embed_batch(s1_original, repeated_bits, delta)

        # Replace s1 in singular value matrix
        S_modified = S.copy()
        S_modified[:, 0] = s1_modified

        # 10. Vectorized SVD Reconstruction
        modified_bands = SVDTransformer.reconstruct_batch(U, S_modified, Vt)
        dct_blocks[selected_block_indices] = SVDTransformer.reinsert_middle_band_batch(
            dct_blocks[selected_block_indices], modified_bands
        )

        # 11. Vectorized 2D Inverse DCT
        reconstructed_blocks = BlockDCTTransformer.inverse_dct_batch(dct_blocks)
        reconstructed_lum_padded = BlockDCTTransformer.blocks_to_image(reconstructed_blocks, grid_shape)

        # 12. Reconstruct Color Image
        watermarked_img = ImagePreprocessor.reconstruct_image(
            reconstructed_lum_padded, cbcr, alpha, mode, orig_shape
        )

        elapsed_time = time.perf_counter() - start_time

        # 13. Generate Non-Secret Recovery Manifest (NEVER includes secret_key)
        recovery_manifest = {
            "algorithm": "SPECTRAMARK-DCT-SVD-QIM",
            "version": 1,
            "block_size": 8,
            "middle_band": [2, 6, 2, 6],
            "strength_profile": strength_profile,
            "quantization_step": delta,
            "repetition_factor": repetition,
            "parity_bytes": parity_bytes,
            "codeword_bits_count": num_codeword_bits,
            "total_embedded_bits": required_blocks,
            "original_dimensions": [H_orig, W_orig],
            "padded_dimensions": [H_pad, W_pad],
            "image_mode": mode,
            "has_alpha": alpha is not None,
        }

        # 14. Calculate Quality Metrics
        from backend.app.core.evaluation.psnr import calculate_psnr
        from backend.app.core.evaluation.ssim import calculate_ssim

        psnr_val = calculate_psnr(img, watermarked_img)
        ssim_val = calculate_ssim(img, watermarked_img)

        metrics = {
            "execution_time_seconds": round(elapsed_time, 4),
            "psnr_db": round(psnr_val, 2),
            "ssim": round(ssim_val, 4),
            "total_blocks": total_blocks,
            "utilized_blocks": required_blocks,
            "utilization_percentage": round((required_blocks / total_blocks) * 100.0, 2),
            "codeword_bytes": len(codeword_bytes),
            "payload_bytes": len(message.encode("utf-8")),
        }

        return watermarked_img, recovery_manifest, metrics

