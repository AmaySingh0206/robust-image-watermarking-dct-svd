"""Reproducible Benchmark Framework for SPECTRAMARK.

Executes automated benchmarks across test images, strength profiles, repetition factors,
and attack conditions. Evaluates PSNR, SSIM, NC, BER, and processing speed using actual
mathematical execution (no fabricated metrics).
"""

from typing import Dict, Any, List
import time
import numpy as np
from PIL import Image

from backend.app.core.watermarking.embedding import WatermarkEmbedder
from backend.app.core.watermarking.extraction import WatermarkExtractor
from backend.app.core.attacks.attack_runner import AttackRunner


class BenchmarkSuite:
    """Automates performance and robustness benchmarking."""

    @classmethod
    def generate_benchmark_images(cls) -> Dict[str, Image.Image]:
        """Generates standard legal test images representing diverse textures and edge frequencies."""
        images = {}
        H, W = 512, 512

        # 1. Natural Texture Synthetic (Simulating landscape texture)
        np.random.seed(101)
        x = np.linspace(0, 12, W)
        y = np.linspace(0, 12, H)
        xx, yy = np.meshgrid(x, y)
        base = (np.sin(xx) * np.cos(yy) * 60 + 128).astype(np.uint8)
        texture = np.random.normal(0, 12, (H, W)).astype(np.int32)
        tex_ch = np.clip(base.astype(np.int32) + texture, 0, 255).astype(np.uint8)
        images["natural_texture"] = Image.fromarray(
            np.dstack([tex_ch, np.roll(tex_ch, 20, axis=1), np.roll(tex_ch, 40, axis=0)]), mode="RGB"
        )

        # 2. Smooth Gradient Synthetic (Simulating sky/studio portrait)
        np.random.seed(102)
        grad = np.tile(np.linspace(20, 235, W, dtype=np.uint8), (H, 1))
        images["smooth_gradient"] = Image.fromarray(
            np.dstack([grad, np.rot90(grad), np.fliplr(grad)]), mode="RGB"
        )

        # 3. High-Frequency Geometric Patterns (Simulating architecture/text)
        np.random.seed(103)
        grid = np.zeros((H, W), dtype=np.uint8)
        grid[::16, :] = 255
        grid[:, ::16] = 255
        images["high_frequency_grid"] = Image.fromarray(
            np.dstack([grid, np.roll(grid, 8, axis=0), np.roll(grid, 8, axis=1)]), mode="RGB"
        )

        return images

    @classmethod
    def run_profile_benchmark(
        cls, test_image: Image.Image, message: str = "BENCHMARK-PAYLOAD-2026", secret_key: str = "BenchKey999"
    ) -> List[Dict[str, Any]]:
        """Evaluates embedding fidelity across all three strength profiles."""
        results = []
        profiles = ["high_quality", "balanced", "high_robustness"]

        for prof in profiles:
            start_time = time.perf_counter()
            wm_img, manifest, metrics = WatermarkEmbedder.embed(
                image_input=test_image,
                message=message,
                secret_key=secret_key,
                strength_profile=prof,
                repetition=5,
            )

            # Blind extraction on pristine watermarked image
            ext = WatermarkExtractor.extract(
                image_input=wm_img,
                secret_key=secret_key,
                manifest=manifest,
                ground_truth_message=message,
            )

            results.append({
                "profile": prof,
                "quantization_step": manifest["quantization_step"],
                "psnr_db": metrics["psnr_db"],
                "ssim": metrics["ssim"],
                "embedding_time": metrics["execution_time_seconds"],
                "extraction_time": ext["execution_time_seconds"],
                "extraction_status": ext["status"],
                "ber_percentage": ext.get("ber_percentage", 0.0),
                "nc": ext.get("nc", 1.0),
            })

        return results

    @classmethod
    def run_attack_suite_benchmark(
        cls,
        watermarked_img: Image.Image,
        manifest: Dict[str, Any],
        secret_key: str,
        message: str = "BENCHMARK-PAYLOAD-2026",
    ) -> List[Dict[str, Any]]:
        """Evaluates watermark robustness across standard attack regimes."""
        attacks_to_test = [
            ("jpeg", {"quality": 95}),
            ("jpeg", {"quality": 85}),
            ("jpeg", {"quality": 75}),
            ("jpeg", {"quality": 60}),
            ("gaussian_noise", {"std_dev": 2.0}),
            ("gaussian_noise", {"std_dev": 5.0}),
            ("salt_and_pepper", {"density": 0.005}),
            ("gaussian_blur", {"radius": 0.25}),
            ("median_filter", {"size": 3}),
            ("resizing", {"scale_factor": 0.75, "restore_dimensions": True}),
            ("resizing", {"scale_factor": 1.25, "restore_dimensions": True}),
            ("brightness", {"factor": 1.1}),
            ("contrast", {"factor": 1.1}),
        ]

        results = []
        for name, params in attacks_to_test:
            res = AttackRunner.evaluate_attack(
                watermarked_img=watermarked_img,
                attack_name=name,
                params=params,
                secret_key=secret_key,
                manifest=manifest,
                ground_truth_message=message,
            )
            results.append({
                "attack": name,
                "parameters": params,
                "degradation_psnr": res["degradation_metrics"]["psnr_db"],
                "degradation_ssim": res["degradation_metrics"]["ssim"],
                "extraction_status": res["extraction_results"]["status"],
                "extraction_success": res["extraction_results"]["success"],
                "ber_percentage": res["extraction_results"].get("ber_percentage"),
                "nc": res["extraction_results"].get("nc"),
                "confidence": res["extraction_results"].get("mean_confidence"),
            })

        return results

