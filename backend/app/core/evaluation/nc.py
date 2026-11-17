"""Normalized Correlation (NC) between binary sequences.

Formula:
  NC = sum(w * w_hat) / (sqrt(sum(w^2)) * sqrt(sum(w_hat^2)))
Where w is original watermark sequence and w_hat is recovered watermark sequence.
Ranges from -1.0 to 1.0 (1.0 indicates exact correlation).
"""

import numpy as np


def calculate_nc(bits_true: np.ndarray, bits_test: np.ndarray) -> float:
    """Calculates Normalized Correlation between two binary bit arrays.

    Args:
        bits_true: Ground truth binary bits {0, 1}.
        bits_test: Recovered binary bits {0, 1}.

    Returns:
        nc: Normalized correlation in [0.0, 1.0].
    """
    if len(bits_true) != len(bits_test):
        raise ValueError(
            f"Length mismatch for NC: true={len(bits_true)} vs test={len(bits_test)}"
        )

    w = bits_true.astype(np.float64)
    w_hat = bits_test.astype(np.float64)

    numerator = np.sum(w * w_hat)
    denom = np.sqrt(np.sum(w ** 2)) * np.sqrt(np.sum(w_hat ** 2))

    if denom < 1e-12:
        # If both sequences are all zeros, correlation is defined as 1.0
        if np.all(w == 0) and np.all(w_hat == 0):
            return 1.0
        return 0.0

    nc = numerator / denom
    return float(np.clip(nc, -1.0, 1.0))

