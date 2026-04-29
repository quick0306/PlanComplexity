from typing import List

from ComplexityMetric.complexity_metric import ComplexityMetric
from ApertureMetric.aperture_geometry import PyAperture


class EdgeAreaMetric(ComplexityMetric):
    """璁＄畻Edge Area Metric

    Reference:
        G脰TSTEDT, et al. Development and evaluation of aperture鈥恇ased complexity metrics using film and EPID
        measurements of static MLC openings. Medical physics, 2015, 42.7: 3911-3921.
        DOI: https://doi.org/10.1118/1.4921733
    """

    aggregation_mode = "mu"

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        """璁＄畻CAM"""
        return [self.calculate_edge_area_metric(aperture) for aperture in apertures]

    def calculate_edge_area_metric(self, aperture: PyAperture) -> float:
        perimeter = aperture.side_perimeter_vertical()
        r1 = perimeter * 10
        r2 = aperture.area() - r1 / 2
        return r1 / (r1 + r2)




