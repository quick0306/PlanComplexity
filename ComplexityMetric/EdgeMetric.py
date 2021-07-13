from typing import List

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture
from DicomParse.utilities import DivisionOrDefault


class EdgeMetric(ComplexityMetric):
    """Edge Metric (EM） Reference 1；also CA，circumference/are, Reference 2

    Reference 1:
        Younge KC, et al. Penalization of aperture complexity in inversely planned volumetric modulated
        Arc therapy: Penalization of aperture complexity in inversely planned VMAT. Med Phys 2012;39: 7160–70.
        DOI: https://doi.org/10.1118/1.4762566
    Reference 2:
        GÖTSTEDT, et al. Development and evaluation of aperture‐based complexity metrics using film
        and EPID measurements of static MLC openings. Medical physics, 2015, 42.7: 3911-3921.
        DOI: https://doi.org/10.1118/1.4921733
    """

    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        return [self.CalculateApertureEdgeMetric(aperture) for aperture in apertures]

    def CalculateApertureEdgeMetric(self, aperture: PyAperture) -> float:
        """计算控制点Aperture Edge Metric"""
        C1 = 0     # Scaling factor, C1
        C2 = 1     # Scaling factor, C2
        side_perimeter = C1 * aperture.SidePerimeterVertical() + C2 * aperture.SidePerimeterHorizontal()
        return DivisionOrDefault(side_perimeter, aperture.Area())
