from typing import List

import numpy as np

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture
from DicomParse.utilities import DivisionOrDefault


class PlanIrregularity(ComplexityMetric):
    """Plan Irregularity Metrics

    Reference :
        Du W, et al. Quantification of beam complexity in intensity-modulated radiation therapy treatment plans.
        Med Phys 2014;41:21716. DOI: http://dx.doi.org/10.1118/1.4861821.
    """
    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        return [self.CalculateApertureIrregularity(aperture) for aperture in apertures]

    def CalculateApertureIrregularity(self, aperture: PyAperture) -> float:
        aa = aperture.Area()
        ap = aperture.SidePerimeterHorizontal() + aperture.SidePerimeterVertical()
        return DivisionOrDefault(ap ** 2, 4 * np.pi * aa)