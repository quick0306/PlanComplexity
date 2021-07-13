from typing import List

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture


class EdgeAreaMetric(ComplexityMetric):
    """计算Edge Area Metric

    Reference:
        GÖTSTEDT, et al. Development and evaluation of aperture‐based complexity metrics using film and EPID
        measurements of static MLC openings. Medical physics, 2015, 42.7: 3911-3921.
        DOI: https://doi.org/10.1118/1.4921733
    """

    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        """计算CAM"""
        return [self.CalculateEdgeAreaMetric(aperture) for aperture in apertures]

    def CalculateEdgeAreaMetric(self, aperture: PyAperture) -> float:
        perimeter = aperture.SidePerimeterVertical()
        r1 = perimeter * 10
        r2 = aperture.Area() - r1 / 2
        return r1 / (r1 + r2)
