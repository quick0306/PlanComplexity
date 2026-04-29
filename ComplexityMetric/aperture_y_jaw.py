from typing import List

from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.complexity_metric import ComplexityMetric


class ApertureYJaw(ComplexityMetric):
    """Y-jaw span."""

    aggregation_mode = "mu"

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        return [abs(aperture.jaw.top - aperture.jaw.bottom) for aperture in apertures]
