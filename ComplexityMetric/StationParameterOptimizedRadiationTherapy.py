from typing import Dict, List

import numpy as np

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.ApertureCreator import AperturesFromBeamCreator
from ApertureMetric.MetersetCreator import MetersetsFromMetersetWeightsCreator
from ApertureMetric.Aperture import PyAperture


class StationParameterOptimizedRadiationTherapy(ComplexityMetric):
    """计算站参数优化（VMAT）

    Reference:
        LI, Ruijiang; XING, Lei. An adaptive planning strategy for station parameter optimized radiation therapy
        (SPORT): Segmentally boosted VMAT. Medical physics, 2013, 40.5: 050701. DOI: https://doi.org/10.1118/1.4802748
    """
    def CalculateForBeam(self, beam: Dict[str, str]) -> float:
        """Returns the complexity metric of a beam, calculated as the weighted sum of the individual metrics
        for each control point"""
        weights = self.GetWeightsBeam(beam)

        metersets = MetersetsFromMetersetWeightsCreator().GetCumulativeMetersets(beam)
        values = self.GetMetricsBeam(beam, metersets)

        return self.WeightedSum(weights, values)

    def GetMetricsBeam(self, beam: Dict[str, str], metersets: List[float]) -> List[float]:
        """Returns the unweighted metrics of a beam's control points"""
        apertures = AperturesFromBeamCreator().Create(beam)
        return self.CalculatePerAperture(apertures, metersets)

    def CalculatePerAperture(self, apertures: List[PyAperture], metersets: List[float]) -> List[float]:
        """计算SPORT"""
        K = 10  # The neighboring 2K station control points are used to calculate the MI of a station point

        iteration_k = list(range(-K, K+1, 1))
        iteration_k.remove(0)

        MI = np.zeros((len(apertures), len(iteration_k)), dtype=float)
        for i in range(len(apertures)):
            for j in range(len(iteration_k)):
                if i + iteration_k[j] >= 0 and (i + iteration_k[j] < len(apertures)):
                    factor = abs((metersets[i] - metersets[i + iteration_k[j]]) /
                                 (apertures[i].gantry_angle - apertures[i + iteration_k[j]].gantry_angle))
                    mlc_sum = 0
                    for lp, lp_k in zip(apertures[i].leaf_pairs, apertures[i + iteration_k[j]].leaf_pairs):
                        mlc_sum += abs(lp.Left - lp_k.Left) + abs(lp.Right - lp_k.Right)
                    MI[i, j] = mlc_sum * factor
                else:
                    MI[i, j] = 0

        MI_SPORT_K = np.sum(MI, 1)
        return list(MI_SPORT_K)