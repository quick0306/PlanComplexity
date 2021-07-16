from typing import List, Dict

import numpy as np

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture
from ApertureMetric.ApertureCreator import AperturesFromBeamCreator


class LeafGap(ComplexityMetric):
    """计算叶片Leaf Gap平均值与标准差

    Reference:
        Nauta M, Villarreal-Barajas JE, Tambasco M. Fractal analysis for assessing the level of
        modulation of IMRT fields. Med Phys 2011; 38: 5385–93. DOI: https://doi.org/10.1118/1.3633912
    """

    def CalculateForPlan(self, plan: Dict[str, str] = None):
        leaf_gaps = []
        for i, beam in plan['beams'].items():
            leaf_gaps.extend(self.CalculateForBeam(beam))
        leaf_gaps = np.array(leaf_gaps)
        return round(np.mean(leaf_gaps), 2), round(np.std(leaf_gaps), 2)

    def CalculateForBeam(self, beam: Dict[str, str]) -> List[float]:
        apertures = AperturesFromBeamCreator().Create(beam)
        return self.CalculatePerAperture(apertures)

    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        """计算Leaf Gap"""
        leaf_gaps = []
        for aperture in apertures:
            for lp in aperture.LeafPairs:
                if not lp.IsOutsideJaw():
                    leaf_gaps.append(lp.FieldSize())

        return leaf_gaps
