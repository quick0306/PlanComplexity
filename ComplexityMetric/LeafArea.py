from typing import List

import numpy as np

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture


class LeafArea(ComplexityMetric):
    """Calculate mean LeafArea = LeafWidth * LeafGap

    Reference:
        Nauta M, et al. Fractal analysis for assessing the level of modulation of IMRT fields.
        Med Phys 2011; 38: 5385–93. DOI: https://doi.org/10.1118/1.3633912
    """

    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        return [self.CalculateApertureLeafGapArea(aperture) for aperture in apertures]

    def CalculateApertureLeafGapArea(self, aperture: PyAperture) -> float:
        """Calculates the mean aperture area of all leaf pairs"""
        areas = np.array(aperture.LeafPairArea)
        return areas[np.nonzero(areas)].mean()
