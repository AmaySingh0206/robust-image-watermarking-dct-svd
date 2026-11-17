"""Unified Attack Orchestrator and Robustness Testing Laboratory Engine.

Coordinates application of single and combined attacks, measures degradation metrics
(PSNR, SSIM), and evaluates watermark extraction robustness (BER, NC, Status).
"""

from typing import Dict, Any, List, Optional
import time
from PIL import Image

from backend.app.core.attacks.jpeg_attack import apply_jpeg_compression
from backend.app.core.attacks.noise_attacks import apply_gaussian_noise, apply_salt_and_pepper_noise
from backend.app.core.attacks.filter_attacks import apply_gaussian_blur, apply_median_filter
from backend.app.core.attacks.geometric_attacks import (
    apply_resizing_attack,
    apply_cropping_attack,
    apply_rotation_attack,
)
from backend.app.core.attacks.photometric_attacks import (
    apply_brightness_attack,
    apply_contrast_attack,
    apply_gamma_attack,
)
from backend.app.core.evaluation.psnr import calculate_psnr
from backend.app.core.evaluation.ssim import calculate_ssim
from backend.app.core.watermarking.extraction import WatermarkExtractor


class AttackRunner:
    """Dispatches individual attacks and coordinates composite robustness evaluations."""

    ATTACK_REGISTRY = {
        "jpeg": apply_jpeg_compression,
        "gaussian_noise": apply_gaussian_noise,
        "salt_and_pepper": apply_salt_and_pepper_noise,
        "gaussian_blur": apply_gaussian_blur,
        "median_filter": apply_median_filter,
        "resizing": apply_resizing_attack,
        "cropping": apply_cropping_attack,
        "rotation": apply_rotation_attack,
        "brightness": apply_brightness_attack,
        "contrast": apply_contrast_attack,
        "gamma": apply_gamma_attack,
    }

    @classmethod
    def apply_single_attack(
        cls, img: Image.Image, attack_name: str, params: Optional[Dict[str, Any]] = None
    ) -> Image.Image:
        """Applies a single registered attack to an image with given parameters."""
        name = attack_name.lower().strip()
        if name not in cls.ATTACK_REGISTRY:
            raise ValueError(f"Unknown attack '{attack_name}'. Registered: {list(cls.ATTACK_REGISTRY.keys())}")

        func = cls.ATTACK_REGISTRY[name]
        params = params or {}
        return func(img, **params)

    @classmethod
    def evaluate_attack(
        cls,
        watermarked_img: Image.Image,
        attack_name: str,
        params: Optional[Dict[str, Any]],
        secret_key: str,
        manifest: Dict[str, Any],
        ground_truth_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Applies an attack, measures image degradation (PSNR/SSIM), and evaluates blind extraction.

        Returns:
            dict containing attack configuration, attacked image, metrics, and extraction results.
        """
        start_time = time.perf_counter()
        params = params or {}

        # 1. Apply attack distortion
        attacked_img = cls.apply_single_attack(watermarked_img, attack_name, params)
        attack_time = time.perf_counter() - start_time

        # 2. Measure degradation from watermarked host
        psnr_val = calculate_psnr(watermarked_img, attacked_img)
        ssim_val = calculate_ssim(watermarked_img, attacked_img)

        # 3. Blind extraction from the attacked image
        ext_start = time.perf_counter()
        ext_result = WatermarkExtractor.extract(
            image_input=attacked_img,
            secret_key=secret_key,
            manifest=manifest,
            ground_truth_message=ground_truth_message,
        )
        ext_time = time.perf_counter() - ext_start

        return {
            "attack_name": attack_name,
            "parameters": params,
            "attacked_image": attacked_img,
            "degradation_metrics": {
                "psnr_db": round(psnr_val, 2),
                "ssim": round(ssim_val, 4),
                "attack_execution_time": round(attack_time, 4),
            },
            "extraction_results": {
                "status": ext_result["status"],
                "success": ext_result["success"],
                "recovered_message": ext_result["message"],
                "mean_confidence": ext_result.get("mean_confidence"),
                "fec_status": ext_result.get("fec_status"),
                "ber_percentage": ext_result.get("ber_percentage"),
                "nc": ext_result.get("nc"),
                "extraction_time": round(ext_time, 4),
            },
            "total_execution_time": round(time.perf_counter() - start_time, 4),
        }

    @classmethod
    def run_combined_attacks(
        cls,
        watermarked_img: Image.Image,
        attack_chain: List[Dict[str, Any]],
        secret_key: str,
        manifest: Dict[str, Any],
        ground_truth_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Applies a sequential series of attacks and evaluates the final extracted watermark."""
        current_img = watermarked_img
        chain_log = []

        start_time = time.perf_counter()
        for step in attack_chain:
            att_name = step.get("name")
            params = step.get("params", {})
            current_img = cls.apply_single_attack(current_img, att_name, params)
            chain_log.append({"attack": att_name, "params": params})

        # Measure cumulative degradation
        psnr_val = calculate_psnr(watermarked_img, current_img)
        ssim_val = calculate_ssim(watermarked_img, current_img)

        # Blind extraction from combined distorted output
        ext_result = WatermarkExtractor.extract(
            image_input=current_img,
            secret_key=secret_key,
            manifest=manifest,
            ground_truth_message=ground_truth_message,
        )

        return {
            "attack_type": "combined",
            "chain": chain_log,
            "attacked_image": current_img,
            "degradation_metrics": {
                "psnr_db": round(psnr_val, 2),
                "ssim": round(ssim_val, 4),
            },
            "extraction_results": ext_result,
            "total_execution_time": round(time.perf_counter() - start_time, 4),
        }

