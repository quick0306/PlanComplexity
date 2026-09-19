from typing import Dict, List, Tuple, Union

from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.aperture_series_metrics import (
    active_leaf_pairs,
    raw_leaf_gap,
    small_aperture_score,
    weighted_mean,
)
from ComplexityMetric.complexity_metric import ComplexityMetric


PlanValue = Union[float, Tuple[float, float]]


class SmallApertureScore(ComplexityMetric):
    """MU-weighted fraction of active gaps strictly smaller than a threshold."""

    def calculate_for_plan(self, plan: Dict[str, str] = None, x=5) -> PlanValue:
        value, _ = self.calculate_for_plan_with_warnings(plan, x=x)
        return value

    def calculate_for_plan_with_warnings(
        self, plan: Dict[str, str], x=5
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
                result = small_aperture_score(layer_apertures, cp_weights, float(x))
                if result.used_uniform_weights:
                    warnings.append(
                        "[METRIC_WEIGHT_FALLBACK] SAS used uniform control-point weights because "
                        "MU increments were missing or invalid."
                    )
                layer_values[layer_index].append(result.value)
                layer_weights[layer_index].append(float(beam["MU"]))

        results = []
        for values, weights in zip(layer_values, layer_weights):
            result = weighted_mean(values, weights)
            if result.used_uniform_weights:
                warnings.append(
                    "[METRIC_WEIGHT_FALLBACK] SAS used uniform beam weights because beam MU "
                    "values were missing or invalid."
                )
            results.append(self.format_result(result.value))
        return (tuple(results) if dual_layer else results[0]), list(dict.fromkeys(warnings))

    def count_beam_leaf_gaps(
        self, beam: Dict[str, str], x=5
    ) -> Union[Tuple[int, int], Tuple[Tuple[int, int], Tuple[int, int]]]:
        apertures = AperturesFromBeamCreator().create(beam)
        if "halcyon" in beam["TreatmentMachineName"].lower() or "ethos" in beam[
            "TreatmentMachineName"
        ].lower():
            return self.count_aperture_leaf_gaps(apertures[0::2], x), self.count_aperture_leaf_gaps(
                apertures[1::2], x
            )
        return self.count_aperture_leaf_gaps(apertures, x)

    @staticmethod
    def count_aperture_leaf_gaps(apertures: List[PyAperture], x=5) -> Tuple[int, int]:
        small_count = 0
        total_count = 0
        for aperture in apertures:
            active_pairs = active_leaf_pairs(aperture)
            total_count += len(active_pairs)
            small_count += sum(raw_leaf_gap(leaf_pair) < x for leaf_pair in active_pairs)
        return small_count, total_count
