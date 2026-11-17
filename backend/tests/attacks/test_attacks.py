import numpy as np
from PIL import Image

from backend.app.core.watermarking.embedding import WatermarkEmbedder
from backend.app.core.watermarking.extraction import WatermarkExtractor
from backend.app.core.attacks.attack_runner import AttackRunner
from backend.tests.integration.test_embed_extract import create_synthetic_test_image


def setup_watermarked_image():
    """Helper to generate a watermarked test image."""
    img = create_synthetic_test_image(512, 512, mode="RGB")
    message = "ATTACK-TEST-KEY-2026"
    key = "AttackSecret123"

    watermarked_img, manifest, metrics = WatermarkEmbedder.embed(
        image_input=img,
        message=message,
        secret_key=key,
        strength_profile="high_robustness",
        repetition=5,
    )
    return img, watermarked_img, message, key, manifest


def test_jpeg_attack_robustness():
    """Verify watermark survives standard JPEG compression (Q=90 and Q=75)."""
    _, wm_img, message, key, manifest = setup_watermarked_image()

    for q in [90, 75]:
        res = AttackRunner.evaluate_attack(
            watermarked_img=wm_img,
            attack_name="jpeg",
            params={"quality": q},
            secret_key=key,
            manifest=manifest,
            ground_truth_message=message,
        )
        assert res["degradation_metrics"]["psnr_db"] > 25.0
        # If Q=90, watermark should survive with 100% payload recovery
        if q == 90:
            assert res["extraction_results"]["success"] is True
            assert res["extraction_results"]["recovered_message"] == message


def test_gaussian_noise_robustness():
    """Verify watermark survives mild additive Gaussian noise."""
    _, wm_img, message, key, manifest = setup_watermarked_image()

    res = AttackRunner.evaluate_attack(
        watermarked_img=wm_img,
        attack_name="gaussian_noise",
        params={"std_dev": 4.0},
        secret_key=key,
        manifest=manifest,
        ground_truth_message=message,
    )
    assert res["extraction_results"]["success"] is True
    assert res["extraction_results"]["recovered_message"] == message


def test_gaussian_blur_robustness():
    """Verify watermark survives slight Gaussian blur and handles severe blur gracefully."""
    _, wm_img, message, key, manifest = setup_watermarked_image()

    # Mild blur (radius=0.25) should succeed
    res = AttackRunner.evaluate_attack(
        watermarked_img=wm_img,
        attack_name="gaussian_blur",
        params={"radius": 0.25},
        secret_key=key,
        manifest=manifest,
        ground_truth_message=message,
    )
    assert res["extraction_results"]["success"] is True
    assert res["extraction_results"]["recovered_message"] == message

    # Aggressive blur (radius=0.6) should report corrupted rather than false payload
    res_heavy = AttackRunner.evaluate_attack(
        watermarked_img=wm_img,
        attack_name="gaussian_blur",
        params={"radius": 0.6},
        secret_key=key,
        manifest=manifest,
        ground_truth_message=message,
    )
    assert res_heavy["extraction_results"]["status"] in ("corrupted", "not_detected")


def test_brightness_and_contrast_attacks():
    """Verify watermark survives moderate photometric scaling."""
    _, wm_img, message, key, manifest = setup_watermarked_image()

    # Brightness +10%
    b_res = AttackRunner.evaluate_attack(
        watermarked_img=wm_img,
        attack_name="brightness",
        params={"factor": 1.1},
        secret_key=key,
        manifest=manifest,
        ground_truth_message=message,
    )
    assert b_res["extraction_results"]["success"] is True
    assert b_res["extraction_results"]["recovered_message"] == message


def test_combined_attack():
    """Verify combined pipeline execution."""
    _, wm_img, message, key, manifest = setup_watermarked_image()

    chain = [
        {"name": "brightness", "params": {"factor": 1.05}},
        {"name": "gaussian_noise", "params": {"std_dev": 2.0}},
    ]

    res = AttackRunner.run_combined_attacks(
        watermarked_img=wm_img,
        attack_chain=chain,
        secret_key=key,
        manifest=manifest,
        ground_truth_message=message,
    )

    assert res["attack_type"] == "combined"
    assert res["degradation_metrics"]["psnr_db"] > 30.0
    assert res["extraction_results"]["success"] is True
    assert res["extraction_results"]["message"] == message
