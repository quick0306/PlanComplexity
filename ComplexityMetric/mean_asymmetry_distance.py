from typing import List

import numpy as np

from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.complexity_metric import ComplexityMetric


class MeanAsymmetryDistance(ComplexityMetric):
    """Mean asymmetry distance (MAD)."""

    aggregation_mode = "mu"

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        return [self.calculate_mean_asymmetry_distance(aperture) for aperture in apertures]

    @staticmethod
    def calculate_mean_asymmetry_distance(aperture: PyAperture) -> float:
        distances = []
        for leaf_pair in aperture.leaf_pairs:
            if leaf_pair.field_size() > 0:
                distances.append((abs(leaf_pair.left) + abs(leaf_pair.right)) / 2.0)
        if not distances:
            return 0.0
        return float(np.mean(np.asarray(distances, dtype=float)))
