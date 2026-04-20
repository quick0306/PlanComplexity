from typing import List

from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.complexity_metric import ComplexityMetric
from DicomParse.utilities import divide_or_default


class EdgeMetric(ComplexityMetric):
    """Edge Metric (EM).

    Reference 1:
        Younge KC, et al. Penalization of aperture complexity in inversely planned volumetric
        modulated arc therapy. Medical Physics, 2012.
        DOI: 10.1118/1.4762566

    Reference 2:
        Gotstedt J, et al. Development and evaluation of aperture-based complexity metrics using
        film and EPID measurements of static MLC openings. Medical Physics, 2015.
        DOI: 10.1118/1.4921733
    """

    aggregation_mode = "mu"

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        return [self.calculate_aperture_edge_metric(aperture) for aperture in apertures]

    def calculate_aperture_edge_metric(self, aperture: PyAperture) -> float:
        # VCoMX/UCoMX uses the Younge et al. EM with C1 = 0 and C2 = 1.
        c1 = 0
        c2 = 1
        side_perimeter = c1 * aperture.side_perimeter_vertical() + c2 * aperture.side_perimeter_horizontal()
        return divide_or_default(side_perimeter, aperture.area())




