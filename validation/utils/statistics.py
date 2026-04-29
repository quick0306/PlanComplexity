from __future__ import annotations

import math


def summarize_agreement(
    expected_values: list[float],
    observed_values: list[float],
) -> dict[str, float | int]:
    if len(expected_values) != len(observed_values):
        raise ValueError("Expected and observed value lists must have the same length.")
    if not expected_values:
        raise ValueError("At least one paired value is required.")

    diffs = [
        observed - expected
        for expected, observed in zip(expected_values, observed_values)
    ]
    mae = sum(abs(diff) for diff in diffs) / len(diffs)
    bias = sum(diffs) / len(diffs)
    rmse = math.sqrt(sum(diff * diff for diff in diffs) / len(diffs))
    return {
        "n": len(diffs),
        "mae": mae,
        "bias": bias,
        "rmse": rmse,
    }
