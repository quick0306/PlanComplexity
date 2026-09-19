from typing import List

import numpy as np

from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.complexity_metric import ComplexityMetric
from DicomParse.utilities import divide_or_default


class PlanIrregularity(ComplexityMetric):
    """Plan irregularity (PI).

    Reference:
        Du W, et al. Quantification of beam complexity in intensity-modulated radiation therapy
        treatment plans. Medical Physics, 2014.
        DOI: 10.1118/1.4861821
    """

    aggregation_mode = "mu"

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        return [self.calculate_aperture_irregularity(aperture) for aperture in apertures]

    def calculate_aperture_irregularity(self, aperture: PyAperture) -> float:
        # PI is defined as P^2 / (4*pi*A) in Du et al.
        area = aperture.area()
        perimeter = aperture.perimeter()
        return divide_or_default(perimeter ** 2, 4 * np.pi * area)




