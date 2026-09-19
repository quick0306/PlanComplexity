from typing import Dict, List, Tuple, Union

import numpy as np

from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.aperture_series_metrics import (
    active_leaf_pairs,
    mean_asymmetry_distance,
    weighted_mean,
)
from ComplexityMetric.complexity_metric import ComplexityMetric


PlanValue = Union[float, Tuple[float, float]]


class MeanAsymmetryDistance(ComplexityMetric):
    """MU-weighted mean distance between the aperture centre and CAX."""

    aggregation_mode = "mu"

    def calculate_for_plan(self, plan: Dict[str, str] = None) -> PlanValue:
        value, _ = self.calculate_for_plan_with_warnings(plan)
        return value

    def calculate_for_plan_with_warnings(
        self, plan: Dict[str, str]
    ) -> Tuple[PlanValue, List[str]]:
        dual_layer = "halcyon" in plan["machine_id"].lower() or "ethos" in plan[
            "machine_id"
        ].lower()
        layer_values: List[List[float]] = [[], []] if dual_layer else [[]]
        layer_weights: List[List[float]] = [[], []] if dual_layer else [[]]
        warnings: List[str] = []

        for beam in plan["beams"].values():
            if beam["TreatmentDeliveryType"] != "TREATMENT" or beam["MU"] <= 0.0:
                continue
            apertures = AperturesFromBeamCreator().create(beam)
            aperture_layers = [apertures[0::2], apertures[1::2]] if dual_layer else [apertures]
            cp_weights = self.get_weights_beam(beam)
            for layer_index, layer_apertures in enumerate(aperture_layers):
                if not any(active_leaf_pairs(aperture) for aperture in layer_apertures):
                    continue
                result = mean_asymmetry_distance(layer_apertures, cp_weights)
                if result.used_uniform_weights:
                    warnings.append(
                        "[METRIC_WEIGHT_FALLBACK] MAD used uniform control-point weights "
                        "because MU increments were missing or invalid."
                    )
                layer_values[layer_index].append(result.value)
                layer_weights[layer_index].append(float(beam["MU"]))

        results = []
        for values, weights in zip(layer_values, layer_weights):
            result = weighted_mean(values, weights)
            if result.used_uniform_weights:
                warnings.append(
                    "[METRIC_WEIGHT_FALLBACK] MAD used uniform beam weights because beam MU "
                    "values were missing or invalid."
                )
            results.append(self.format_result(result.value))
        return (tuple(results) if dual_layer else results[0]), list(dict.fromkeys(warnings))

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        return [self.calculate_mean_asymmetry_distance(aperture) for aperture in apertures]

    @staticmethod
    def calculate_mean_asymmetry_distance(aperture: PyAperture) -> float:
        distances = [
            abs((leaf_pair.left + leaf_pair.right) / 2.0)
            for leaf_pair in active_leaf_pairs(aperture)
        ]
        if not distances:
            return 0.0
        return float(np.mean(np.asarray(distances, dtype=float)))
