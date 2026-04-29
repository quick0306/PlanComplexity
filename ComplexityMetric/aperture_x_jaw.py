from typing import List

from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.complexity_metric import ComplexityMetric


class ApertureXJaw(ComplexityMetric):
    """X-jaw span."""

    aggregation_mode = "mu"

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        return [abs(aperture.jaw.right - aperture.jaw.left) for aperture in apertures]
