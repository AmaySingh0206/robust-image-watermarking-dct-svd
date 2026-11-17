"""Bit Error Rate (BER) evaluation.

Formula:
  BER = (Incorrectly Recovered Bits / Total Bits) * 100%
Returns percentage in [0.0%, 100.0%].
"""

import numpy as np


def calculate_ber(bits_true: np.ndarray, bits_test: np.ndarray) -> float:
    """Calculates Bit Error Rate (BER) as a percentage.

    Args:
        bits_true: Ground truth binary bits {0, 1}.
        bits_test: Recovered binary bits {0, 1}.

    Returns:
        ber_pct: Bit Error Rate percentage in [0.0, 100.0].
    """
    if len(bits_true) != len(bits_test):
        raise ValueError(
            f"Length mismatch for BER: true={len(bits_true)} vs test={len(bits_test)}"
        )

    if len(bits_true) == 0:
        return 0.0

    errors = np.sum(bits_true != bits_test)
    ber_pct = (errors / len(bits_true)) * 100.0
    return float(ber_pct)

