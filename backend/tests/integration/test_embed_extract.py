import numpy as np
from PIL import Image

from backend.app.core.watermarking.embedding import WatermarkEmbedder
from backend.app.core.watermarking.extraction import WatermarkExtractor


def create_synthetic_test_image(height=512, width=512, mode="RGB"):
    """Creates a deterministic synthetic test image with natural texture variation."""
    np.random.seed(42)
    y, x = np.mgrid[0:height, 0:width]
    base = (np.sin(x / 15.0) * 0.5 + 0.5) * 100 + (np.cos(y / 20.0) * 0.5 + 0.5) * 100
    # Add texture noise
    texture = np.random.normal(0, 10, (height, width))
    base = np.clip(base + texture, 0, 255).astype(np.uint8)

    if mode == "RGB":
        r = base
        g = np.roll(base, 20, axis=1)
        b = np.roll(base, 40, axis=0)
        arr = np.dstack([r, g, b]).astype(np.uint8)
        return Image.fromarray(arr, mode="RGB")
    elif mode == "RGBA":
        r = base
        g = np.roll(base, 20, axis=1)
        b = np.roll(base, 40, axis=0)
        a = np.full((height, width), 255, dtype=np.uint8)
        arr = np.dstack([r, g, b, a]).astype(np.uint8)
        return Image.fromarray(arr, mode="RGBA")
    elif mode == "L":
        return Image.fromarray(base.astype(np.uint8), mode="L")
    else:
        raise ValueError(f"Unsupported test mode {mode}")


def test_full_embed_extract_rgb_cycle():
    """Verify that a watermark can be embedded and blindly extracted with 100% accuracy."""
    img = create_synthetic_test_image(512, 512, mode="RGB")
    message = "SPECTRAMARK (C) 2026 Asset ID: SM-99824"
    secret_key = "MySecureTopSecretKey"

    # Embed watermark
    watermarked_img, manifest, metrics = WatermarkEmbedder.embed(
        image_input=img,
        message=message,
        secret_key=secret_key,
        strength_profile="balanced",
        repetition=5,
    )

    assert metrics["psnr_db"] >= 38.0, f"PSNR too low: {metrics['psnr_db']} dB"
    assert metrics["ssim"] >= 0.98, f"SSIM too low: {metrics['ssim']}"

    # Blind Extraction (original host image is NOT passed!)
    res = WatermarkExtractor.extract(
        image_input=watermarked_img,
        secret_key=secret_key,
        manifest=manifest,
        ground_truth_message=message,
    )

    assert res["status"] == "success", f"Extraction failed: {res['error']}"
    assert res["message"] == message, f"Expected '{message}', got '{res['message']}'"
    assert res["ber_percentage"] == 0.0, f"BER should be 0% on lossless image, got {res['ber_percentage']}%"
    assert res["nc"] == 1.0, f"NC should be 1.0, got {res['nc']}"


def test_wrong_key_rejection():
    """Verify that an incorrect secret key fails to extract the payload."""
    img = create_synthetic_test_image(512, 512, mode="RGB")
    message = "Confidential Forensic Watermark"
    correct_key = "RealSecurityKey#2026"
    wrong_key = "AttackerGuessedWrongKey#999"

    watermarked_img, manifest, _ = WatermarkEmbedder.embed(
        image_input=img,
        message=message,
        secret_key=correct_key,
        strength_profile="high_quality",
        repetition=5,
    )

    # Attempt extraction with wrong key
    wrong_res = WatermarkExtractor.extract(
        image_input=watermarked_img,
        secret_key=wrong_key,
        manifest=manifest,
    )

    assert wrong_res["status"] in ("corrupted", "not_detected")
    assert wrong_res["message"] != message


def test_grayscale_embed_extract():
    """Verify watermarking on single-channel Grayscale images."""
    img = create_synthetic_test_image(512, 512, mode="L")
    message = "GRAYSCALE-WATERMARK-ID"
    key = "GraySecretKey"

    watermarked_img, manifest, metrics = WatermarkEmbedder.embed(
        image_input=img,
        message=message,
        secret_key=key,
        strength_profile="balanced",
        repetition=3,
    )

    assert metrics["psnr_db"] >= 38.0

    res = WatermarkExtractor.extract(
        image_input=watermarked_img,
        secret_key=key,
        manifest=manifest,
    )

    assert res["status"] == "success"
    assert res["message"] == message


def test_rgba_embed_extract_preserves_alpha():
    """Verify RGBA image embeds watermark and preserves the original alpha channel."""
    img = create_synthetic_test_image(512, 512, mode="RGBA")
    message = "RGBA-PROTECTION-TOKEN"
    key = "RgbaKey123"

    watermarked_img, manifest, metrics = WatermarkEmbedder.embed(
        image_input=img,
        message=message,
        secret_key=key,
        strength_profile="balanced",
        repetition=5,
    )

    assert watermarked_img.mode == "RGBA"
    # Ensure alpha channel is preserved
    orig_alpha = np.array(img.getchannel("A"))
    wm_alpha = np.array(watermarked_img.getchannel("A"))
    np.testing.assert_array_equal(orig_alpha, wm_alpha)

    res = WatermarkExtractor.extract(
        image_input=watermarked_img,
        secret_key=key,
        manifest=manifest,
    )
    assert res["status"] == "success"
    assert res["message"] == message
