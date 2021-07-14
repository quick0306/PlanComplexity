from typing import List, Dict

import numpy as np

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.Aperture import PyAperture
from ApertureMetric.ApertureCreator import AperturesFromBeamCreator


class LeafTravel(ComplexityMetric):
    """计算叶片运动范围平均值

    Reference:
        MASI, Laura, et al. Impact of plan parameters on the dosimetric accuracy of volumetric modulated arc therapy.
        Medical physics, 2013, 40.7: 071718. DOI: https://doi.org/10.1118/1.4810969
    """

    def CalculateForPlan(self, plan: Dict[str, str] = None):
        leaf_travel = []
        for i, beam in plan['beams'].items():
            leaf_travel.extend(self.CalculateForBeam(beam))

        return round(np.mean(np.array(leaf_travel)), 2)

    def CalculateForBeam(self, beam: Dict[str, str]) -> List[float]:
        apertures = AperturesFromBeamCreator().Create(beam)
        return self.CalculatePerAperture(apertures)

    def CalculatePerAperture(self, apertures: List[PyAperture]) -> List[float]:
        """计算Leaf Gap"""
        leaf_travel_track_left = {}
        leaf_travel_track_right = {}
        for aperture in apertures:
            n_pairs = int(len(aperture.LeafPairs))
            for i, lp in zip(range(n_pairs), aperture.LeafPairs):
                if not lp.IsOutsideJaw():
                    "记录叶片运动轨迹"
                    if i in leaf_travel_track_left:
                        leaf_travel_track_left[i].append(lp.Left)
                    else:
                        leaf_travel_track_left[i] = [lp.Left]

                    if i in leaf_travel_track_right:
                        leaf_travel_track_right[i].append(lp.Right)
                    else:
                        leaf_travel_track_right[i] = [lp.Right]

        leaf_travel_distance = []

        for i in leaf_travel_track_left:
            leaf_travel = np.array(leaf_travel_track_left[i])
            leaf_travel_distance.append(np.sum(abs(np.diff(leaf_travel))))
        for j in leaf_travel_track_right:
            leaf_travel = np.array(leaf_travel_track_right[j])
            leaf_travel_distance.append(np.sum(abs(np.diff(leaf_travel))))

        return leaf_travel_distance
