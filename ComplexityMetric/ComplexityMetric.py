from typing import Dict, List
import math

import numpy as np

from ApertureMetric.ApertureCreator import AperturesFromBeamCreator
from ApertureMetric.MetersetCreator import MetersetsFromMetersetWeightsCreator
from ApertureMetric.Aperture import PyAperture


class ComplexityMetric:

    def CalculateForPlan(self, plan: Dict[str, str]=None) -> float:
        """Returns the complexity metric of a plan, calculated as the weighted sum of the individual metrics
        for each beam"""
        weights = self.GetWeightsPlan(plan)
        metrics = self.GetMetricsPlan(plan)

        return round(self.WeightedSum(weights, metrics), 2)

    def GetWeightsPlan(self, plan: Dict[str, str]) -> List[float]:
        """Returns the weights of a plan's beams by default, the weights are the meterset values per beam"""
        metersets = []
        for k, beam in plan["beams"].items():
            if "MU" in beam:
                if beam["MU"] > 0:
                    metersets.append(float(beam["MU"]))
        return metersets

    def GetMetricsPlan(self, plan: Dict[str, str]) -> List[float]:
        """Returns the unweighted metrics of a plan's beams"""
        values = []
        for k, beam in plan["beams"].items():
            # check if treatment beam
            if beam["TreatmentDeliveryType"] == "TREATMENT":
                if beam["MU"] > 0.:
                    v = self.CalculateForBeam(beam)
                    values.append(v)
        return values

    def CalculateForBeam(self, beam: Dict[str, str]) -> float:
        """Returns the complexity metric of a beam, calculated as the weighted sum of the individual metrics
        for each control point"""
        weights = self.GetWeightsBeam(beam)
        values = self.GetMetricsBeam(beam)

        return self.WeightedSum(weights, values)

    def GetWeightsBeam(self, beam: Dict[str, str]) -> np.ndarray:
        """Returns the weights of a beam's control points, the weights are the meterset values per control point"""
        return MetersetsFromMetersetWeightsCreator().Create(beam)

    def GetMetricsBeam(self, beam: Dict[str, str]) -> List[float]:
        """Returns the unweighted metrics of a beam's control points"""
        apertures = AperturesFromBeamCreator().Create(beam)
        return self.CalculatePerAperture(apertures)

    def GetGantryAngleBeam(self, beam: Dict[str, str]) -> List[float]:
        """Return the angle of the beam every cp gantry"""
        angles = []

        for cp in beam["ControlPointSequence"]:
            gantry_angle = float(cp.GantryAngle) if "GantryAngle" in cp else beam["GantryAngle"]
            angles.append(gantry_angle)
        return angles

    def CalculatePerAperture(self, apertures: List[PyAperture]):
        """Override method"""
        pass

    def CalculatePerControlPointWeighted(self, beam) -> List[float]:
        """Returns the weighted metrics of a beam's control points"""
        return self.WeightedValues(self.GetWeightsBeam(beam), self.GetMetricsBeam(beam))

    def CalculatePerControlPointUnweighted(self, beam) -> List[float]:
        """Returns the unweighted metrics of a beam's control points"""
        return self.GetMetricsBeam(beam)

    def CalculatePerControlPointWeightsOnly(self, beam) -> np.ndarray:
        """Returns the weights of a beam's control points"""
        return self.GetWeightsBeam(beam)

    def WeightedSum(self, weights, values) -> float:
        """Returns the weighted sum of the given values and weights"""
        return sum(self.WeightedValues(weights, values))

    @staticmethod
    def WeightedValues(weights, values) -> List[float]:
        weightSum = sum(weights)
        result = []
        for i in range(len(values)):
            v = (weights[i] / weightSum) * values[i]
            if not math.isnan(v):
                result.append(v)
        return result
