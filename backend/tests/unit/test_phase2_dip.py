import numpy as np
from PIL import Image

from backend.app.core.watermarking.preprocessing import ImagePreprocessor
from backend.app.core.watermarking.dct_transform import BlockDCTTransformer
from backend.app.core.watermarking.svd_transform import SVDTransformer
from backend.app.core.watermarking.qim import QIMModulator
from backend.app.core.watermarking.key_management import KeyManager


def test_dct_idct_numerical_precision():
    """Verify that DCT followed by IDCT reconstructs original block with machine precision."""
    np.random.seed(42)
    # Generate 16 random 8x8 blocks with spatial values in [0, 255]
    original_blocks = np.random.uniform(0.0, 255.0, size=(16, 8, 8))

    dct_blocks = BlockDCTTransformer.forward_dct_batch(original_blocks)
    reconstructed_blocks = BlockDCTTransformer.inverse_dct_batch(dct_blocks)

    max_abs_error = np.max(np.abs(original_blocks - reconstructed_blocks))
    assert max_abs_error < 1e-10, f"DCT-IDCT reconstruction error too high: {max_abs_error}"


def test_svd_reconstruction_precision():
    """Verify that SVD decomposition and matrix reconstruction preserves 4x4 submatrix."""
    np.random.seed(123)
    bands = np.random.uniform(-50.0, 50.0, size=(20, 4, 4))

    U, S, Vt = SVDTransformer.decompose_batch(bands)
    reconstructed = SVDTransformer.reconstruct_batch(U, S, Vt)

    max_abs_error = np.max(np.abs(bands - reconstructed))
    assert max_abs_error < 1e-10, f"SVD reconstruction error too high: {max_abs_error}"


def test_qim_embedding_and_blind_extraction():
    """Verify QIM correctly embeds and blinds extracts binary bits without original host."""
    delta = 25.0
    s_values = np.array([12.4, 45.8, 103.2, 8.5, 76.1, 220.9])
    target_bits = np.array([0, 1, 0, 1, 1, 0], dtype=np.uint8)

    # Embed bits into singular values
    s_modified = QIMModulator.embed_batch(s_values, target_bits, delta)

    # Blind extraction
    extracted_bits, confidences = QIMModulator.extract_batch(s_modified, delta)

    np.testing.assert_array_equal(extracted_bits, target_bits)
    assert np.all(s_modified > 0), "All modified singular values must be strictly positive"


def test_qim_noise_tolerance_boundary():
    """Verify that QIM survives perturbation up to Delta / 2."""
    delta = 30.0
    s_val = 150.0

    for bit in (0, 1):
        s_emb = QIMModulator.embed_bit(s_val, bit, delta)
        # Add noise strictly smaller than Delta / 2 (e.g. Delta * 0.4)
        noise = (delta * 0.4) * (1 if bit == 0 else -1)
        s_noisy = s_emb + noise
        extracted_bit, _ = QIMModulator.extract_bit(s_noisy, delta)
        assert extracted_bit == bit, f"Expected bit {bit} to survive noise {noise}"


def test_key_manager_deterministic_permutation():
    """Verify HMAC block permutation is reproducible and key-sensitive."""
    key = "TestSecretPassword123"
    total_blocks = 500

    perm1 = KeyManager.get_block_permutation(key, total_blocks)
    perm2 = KeyManager.get_block_permutation(key, total_blocks)

    # Must be strictly identical
    np.testing.assert_array_equal(perm1, perm2)

    # Different key must yield completely different permutation
    diff_perm = KeyManager.get_block_permutation("DifferentPassword456", total_blocks)
    assert not np.array_equal(perm1, diff_perm)
    assert len(np.unique(perm1)) == total_blocks


def test_image_preprocessing_roundtrip():
    """Verify color conversion and padding roundtrip preserves visual image."""
    # Create test RGB image of dimension 67 x 73 (not divisible by 8)
    W, H = 73, 67
    img_data = np.random.randint(0, 256, (H, W, 3), dtype=np.uint8)
    img = Image.fromarray(img_data, mode="RGB")

    y, cbcr, alpha, mode, orig_shape = ImagePreprocessor.decompose_channels(img)
    assert mode == "RGB"
    assert orig_shape == (H, W)

    padded_y, _ = ImagePreprocessor.pad_to_block_multiple(y, block_size=8)
    assert padded_y.shape[0] % 8 == 0
    assert padded_y.shape[1] % 8 == 0

    reconstructed_img = ImagePreprocessor.reconstruct_image(
        padded_y, cbcr, alpha, mode, orig_shape
    )
    rec_arr = np.array(reconstructed_img)

    # RGB roundtrip error should be within rounding precision (+/- 2 intensity levels)
    max_diff = np.max(np.abs(img_data.astype(int) - rec_arr.astype(int)))
    assert max_diff <= 2, f"Color roundtrip discrepancy too high: {max_diff}"

