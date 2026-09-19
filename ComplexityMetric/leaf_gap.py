from typing import Dict, List, Tuple, Union

import numpy as np

from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ApertureMetric.aperture_geometry import PyAperture
from ComplexityMetric.aperture_series_metrics import (
    GapMoments,
    active_leaf_pairs,
    raw_leaf_gap,
    weighted_gap_moments,
    weighted_mean,
)
from ComplexityMetric.complexity_metric import ComplexityMetric


GapValue = Tuple[float, float]
PlanGapValue = Union[GapValue, Tuple[GapValue, GapValue]]


class LeafGap(ComplexityMetric):
    """MU-weighted gap mean and standard deviation for active leaf pairs."""

    round_digits = 2

    def calculate_for_plan(self, plan: Dict[str, str] = None) -> PlanGapValue:
        value, _ = self.calculate_for_plan_with_warnings(plan)
        return value

    def calculate_for_plan_with_warnings(
        self, plan: Dict[str, str]
    ) -> Tuple[PlanGapValue, List[str]]:
        dual_layer = "halcyon" in plan["machine_id"].lower() or "ethos" in plan[
            "machine_id"
        ].lower()
        layer_moments: List[List[GapMoments]] = [[], []] if dual_layer else [[]]
        layer_weights: List[List[float]] = [[], []] if dual_layer else [[]]
        warnings: List[str] = []

        for beam in plan["beams"].values():
            if beam["TreatmentDeliveryType"] != "TREATMENT" or beam["MU"] <= 0.0:
                continue
            apertures = AperturesFromBeamCreator().create(beam)
            aperture_layers = [apertures[0::2], apertures[1::2]] if dual_layer else [apertures]
            cp_weights = self.get_weights_beam(beam)
            for layer_index, layer_apertures in enumerate(aperture_layers):
                moments = weighted_gap_moments(layer_apertures, cp_weights)
                if not any(active_leaf_pairs(aperture) for aperture in layer_apertures):
                    continue
                if moments.used_uniform_weights:
                    warnings.append(
                        "[METRIC_WEIGHT_FALLBACK] LG used uniform control-point weights because "
                        "MU increments were missing or invalid."
                    )
                layer_moments[layer_index].append(moments)
                layer_weights[layer_index].append(float(beam["MU"]))

        results = []
        for moments, weights in zip(layer_moments, layer_weights):
            result, used_uniform = self._combine_moments(moments, weights)
            if used_uniform:
                warnings.append(
                    "[METRIC_WEIGHT_FALLBACK] LG used uniform beam weights because beam MU "
                    "values were missing or invalid."
                )
            results.append(result)
        return (tuple(results) if dual_layer else results[0]), list(dict.fromkeys(warnings))

    def get_beam_leaf_gaps(
        self, beam: Dict[str, str]
    ) -> Union[List[float], Tuple[List[float], List[float]]]:
        apertures = AperturesFromBeamCreator().create(beam)
        if "halcyon" in beam["TreatmentMachineName"].lower() or "ethos" in beam[
            "TreatmentMachineName"
        ].lower():
            return self.get_aperture_leaf_gaps(apertures[0::2]), self.get_aperture_leaf_gaps(
                apertures[1::2]
            )
        return self.get_aperture_leaf_gaps(apertures)

    @staticmethod
    def get_aperture_leaf_gaps(apertures: List[PyAperture]) -> List[float]:
        return [
            raw_leaf_gap(leaf_pair)
            for aperture in apertures
            for leaf_pair in active_leaf_pairs(aperture)
        ]

    def calculate_per_aperture(self, apertures: List[PyAperture]) -> List[float]:
        return [self.summarize(self.get_aperture_leaf_gaps([aperture]))[0] for aperture in apertures]

    def summarize(self, gaps: List[float]) -> GapValue:
        if not gaps:
            return 0.0, 0.0
        values = np.asarray(gaps, dtype=float)
        return self.format_result(float(np.mean(values))), self.format_result(float(np.std(values)))

    def _combine_moments(
        self, moments: List[GapMoments], weights: List[float]
    ) -> Tuple[GapValue, bool]:
        if not moments:
            return (0.0, 0.0), False
        mean_result = weighted_mean([item.mean for item in moments], weights)
        second_result = weighted_mean(
            [item.standard_deviation**2 + item.mean**2 for item in moments], weights
        )
        variance = max(second_result.value - mean_result.value**2, 0.0)
        return (
            self.format_result(mean_result.value),
            self.format_result(float(np.sqrt(variance))),
        ), mean_result.used_uniform_weights or second_result.used_uniform_weights
