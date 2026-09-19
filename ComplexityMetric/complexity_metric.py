from typing import Dict, List, Tuple, Union, Optional
import math

import numpy as np

from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ApertureMetric.meterset_creator import MetersetsFromMetersetWeightsCreator
from ApertureMetric.aperture_geometry import PyAperture


class ComplexityMetric:
    aggregation_mode = "uniform"
    round_digits = 2

    def __init__(self, *, full_precision: bool = False):
        self.full_precision = full_precision

    def format_result(self, value, digits=None):
        """Round final presentation values only; validation keeps the float result."""
        digits = self.round_digits if digits is None else digits
        if isinstance(value, (list, tuple, np.ndarray)):
            values = np.asarray(value, dtype=float)
            return values if self.full_precision else np.round(values, digits)
        return float(value) if self.full_precision else round(value, digits)

    def calculate_for_plan(self, plan: Dict[str, str] = None) -> Union[Tuple[float, float], float]:
        """Return the plan metric aggregated according to the metric definition."""
        weights = self.get_plan_aggregation_weights(plan)
        metrics = self.get_metrics_plan(plan)
        if 'halcyon' in plan['machine_id'].lower() or 'ethos' in plan['machine_id'].lower():
            mlcx1_metrics = [metric[0] for metric in metrics]
            mlcx2_metrics = [metric[1] for metric in metrics]
            return (
                self.format_result(self.weighted_sum(weights, mlcx1_metrics)),
                self.format_result(self.weighted_sum(weights, mlcx2_metrics)),
            )
        else:
            return self.format_result(self.weighted_sum(weights, metrics))

    def get_weights_plan(self, plan: Dict[str, str]) -> List[float]:
        """Returns beam MU weights for backwards-compatible callers."""
        metersets = []
        for k, beam in plan["beams"].items():
            if "MU" in beam:
                if beam["MU"] > 0:
                    metersets.append(float(beam["MU"]))
        return metersets

    def get_plan_aggregation_weights(self, plan: Dict[str, str]) -> List[float]:
        weights = []
        for _, beam in plan["beams"].items():
            if beam["TreatmentDeliveryType"] != "TREATMENT" or beam["MU"] <= 0.0:
                continue
            if self.aggregation_mode == "mu":
                weights.append(float(beam["MU"]))
            else:
                weights.append(float(self.get_active_control_arc_count(beam)))
        return weights

    def get_metrics_plan(self, plan: Dict[str, str]) -> List[Union[Tuple[float, float], float]]:
        """Returns the unweighted metrics of a plan's beams"""
        values = []
        for k, beam in plan["beams"].items():
            # check if treatment beam
            if beam["TreatmentDeliveryType"] == "TREATMENT":
                if beam["MU"] > 0.:
                    v = self.calculate_for_beam(beam)
                    values.append(v)
        return values

    def calculate_for_beam(self, beam: Dict[str, str]) -> Union[Tuple[float, float], float]:
        """Returns the complexity metric of a beam aggregated over its active control arcs."""
        if 'halcyon' in beam['TreatmentMachineName'].lower() or 'ethos' in beam['TreatmentMachineName'].lower():
            MLCX1_values, MLCX2_values = self.get_metrics_beam(beam)
            weights = self.get_beam_aggregation_weights(beam, MLCX1_values)
            return self.weighted_sum(weights, MLCX1_values), self.weighted_sum(weights, MLCX2_values)
        else:
            values = self.get_metrics_beam(beam)
            weights = self.get_beam_aggregation_weights(beam, values)
            return self.weighted_sum(weights, values)

    def get_weights_beam(self, beam: Dict[str, str]) -> np.ndarray:
        """Returns the weights of a beam's control points, the weights are the meterset values per control point"""
        return MetersetsFromMetersetWeightsCreator().create(beam)

    def get_control_arc_weights(self, beam: Dict[str, str]) -> np.ndarray:
        cumulative = MetersetsFromMetersetWeightsCreator().get_cumulative_metersets(beam)
        if cumulative is None or len(cumulative) < 2:
            return np.array([])
        return np.diff(cumulative)

    def get_metrics_beam(self, beam: Dict[str, str]) -> Union[Tuple[List[float], List[float]], List[float]]:
        """Returns the unweighted metrics of a beam's control points"""
        if 'halcyon' in beam['TreatmentMachineName'].lower() or 'ethos' in beam['TreatmentMachineName'].lower():
            apertures = AperturesFromBeamCreator().create(beam)
            mlcx1_apertures = apertures[0::2]
            mlcx2_apertures = apertures[1::2]
            return self.calculate_per_aperture(mlcx1_apertures), self.calculate_per_aperture(mlcx2_apertures)
        else:
            apertures = AperturesFromBeamCreator().create(beam)
            return self.calculate_per_aperture(apertures)

    def get_gantry_angle_beam(self, beam: Dict[str, str]) -> List[float]:
        """Return the angle of the beam every cp gantry"""
        angles = []

        for cp in beam["ControlPointSequence"]:
            gantry_angle = float(cp.GantryAngle) if "GantryAngle" in cp else beam["GantryAngle"]
            angles.append(gantry_angle)
        return angles

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        """Override method"""
        pass

    def calculate_per_control_point_weighted(self, beam) -> List[float]:
        """Returns the weighted metrics of a beam's control points"""
        return self.weighted_values(self.get_beam_aggregation_weights(beam, self.get_metrics_beam(beam)), self.get_metrics_beam(beam))

    def calculate_per_control_point_unweighted(self, beam) -> List[float]:
        """Returns the unweighted metrics of a beam's control points"""
        return self.get_metrics_beam(beam)

    def calculate_per_control_point_weights_only(self, beam) -> np.ndarray:
        """Returns the weights of a beam's control points"""
        return self.get_weights_beam(beam)

    def weighted_sum(self, weights, values) -> float:
        """Returns the weighted sum of the given values and weights"""
        return sum(self.weighted_values(weights, values))

    def get_beam_aggregation_weights(self, beam: Dict[str, str], values: List[float]) -> np.ndarray:
        if self.aggregation_mode == "mu":
            return self.get_weights_beam(beam)
        return np.ones(len(values))

    @staticmethod
    def get_active_control_arc_count(beam: Dict[str, str]) -> int:
        return max(len(beam.get("ControlPointSequence", [])), 1)

    @staticmethod
    def weighted_values(weights, values) -> List[float]:
        weight_sum = sum(weights)
        result = []
        for i in range(len(values)):
            v = (weights[i] / weight_sum) * values[i]
            if not math.isnan(v):
                result.append(v)
        return result




