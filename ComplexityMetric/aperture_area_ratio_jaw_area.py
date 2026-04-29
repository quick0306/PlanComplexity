from typing import List

from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.complexity_metric import ComplexityMetric


class ApertureAreaRatioJawArea(ComplexityMetric):
    """Ratio of aperture area to jaw-defined area."""

    aggregation_mode = "mu"

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        """Calculate the aperture-area to jaw-area ratio for each control point."""
        return [self.calculate_aperture_area_ratio_jaw_area(aperture) for aperture in apertures]

    def calculate_aperture_area_ratio_jaw_area(self, aperture: PyAperture) -> float:
        aperture_area = aperture.area()
        jaws = aperture.jaw
        jaw_area = abs(jaws.right - jaws.left) * abs(jaws.top - jaws.bottom)
        return aperture_area / jaw_area


