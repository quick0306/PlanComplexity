from typing import Dict, Iterable, List, Sequence

import numpy as np

from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ApertureMetric.meterset_creator import MetersetsFromMetersetWeightsCreator
from ApertureMetric.mlc_attributes import MLCAttributes
from ComplexityMetric.complexity_metric import ComplexityMetric


class ProportionMLCSpeedAcceleration(ComplexityMetric):
    """MLC speed and acceleration proportions for VMAT delivery.

    Reference:
        Park JM, et al. The effect of MLC speed and acceleration on the plan delivery
        accuracy of VMAT. Br J Radiol. 2015;88(1049):20140698.
        DOI: 10.1259/bjr.20140698

    Notes:
        The paper reports speed bins in cm/s and acceleration bins in cm/s^2.
        This implementation works in mm/s and mm/s^2 because DICOM leaf positions
        are already expressed in mm.

        The bins are delivery-time dependent. An RTPLAN-only exact calculation is
        possible only when control-point time can be inferred from usable dose-rate
        and gantry-speed inputs. Elekta Monaco/Oncentra exports with absent/zero
        DoseRateSet and local-only machine IDs should remain NaN unless a validated
        site-specific timing model or delivery log is supplied.
    """

    SPEED_BINS_MM_PER_S = (
        (0.0, 4.0),
        (4.0, 8.0),
        (8.0, 12.0),
        (12.0, 16.0),
        (16.0, 20.0),
    )
    ACC_BINS_MM_PER_S2 = (
        (0.0, 40.0),
        (40.0, 80.0),
        (80.0, 120.0),
        (120.0, 160.0),
        (160.0, 200.0),
    )

    def calculate_for_plan(self, plan: Dict[str, str] = None):
        if "halcyon" in plan["machine_id"].lower() or "ethos" in plan["machine_id"].lower():
            mlcx1_speed = []
            mlcx1_acc = []
            mlcx1_summary = []
            mlcx2_speed = []
            mlcx2_acc = []
            mlcx2_summary = []
            weights = []

            for _, beam in plan["beams"].items():
                if beam["TreatmentDeliveryType"] != "TREATMENT" or beam["MU"] <= 0.0:
                    continue
                mlcx1, mlcx2 = self.calculate_for_beam(beam)
                beam_weight = max(len(beam.get("ControlPointSequence", [])) - 1, 1)
                weights.append(beam_weight)
                mlcx1_speed.append(mlcx1[0])
                mlcx1_acc.append(mlcx1[1])
                mlcx1_summary.append(mlcx1[2])
                mlcx2_speed.append(mlcx2[0])
                mlcx2_acc.append(mlcx2[1])
                mlcx2_summary.append(mlcx2[2])

            return (
                np.round(self._weighted_average(mlcx1_speed, weights), 4).tolist(),
                np.round(self._weighted_average(mlcx1_acc, weights), 4).tolist(),
                np.round(self._weighted_average(mlcx1_summary, weights), 4).tolist(),
                np.round(self._weighted_average(mlcx2_speed, weights), 4).tolist(),
                np.round(self._weighted_average(mlcx2_acc, weights), 4).tolist(),
                np.round(self._weighted_average(mlcx2_summary, weights), 4).tolist(),
            )

        speed_profiles = []
        acc_profiles = []
        summaries = []
        weights = []
        for _, beam in plan["beams"].items():
            if beam["TreatmentDeliveryType"] != "TREATMENT" or beam["MU"] <= 0.0:
                continue
            speed_profile, acc_profile, summary = self.calculate_for_beam(beam)
            speed_profiles.append(speed_profile)
            acc_profiles.append(acc_profile)
            summaries.append(summary)
            weights.append(max(len(beam.get("ControlPointSequence", [])) - 1, 1))

        return (
            np.round(self._weighted_average(speed_profiles, weights), 4).tolist(),
            np.round(self._weighted_average(acc_profiles, weights), 4).tolist(),
            np.round(self._weighted_average(summaries, weights), 4).tolist(),
        )

    def calculate_for_beam(self, beam: Dict[str, str]):
        cumulative_metersets = MetersetsFromMetersetWeightsCreator().get_cumulative_metersets(beam)
        apertures = AperturesFromBeamCreator().create(beam)
        if "halcyon" in beam["TreatmentMachineName"].lower() or "ethos" in beam["TreatmentMachineName"].lower():
            mlcx1_aperture = apertures[0::2]
            mlcx2_aperture = apertures[1::2]
            return (
                self.calculate_mlc_attribute(mlcx1_aperture, cumulative_metersets, beam),
                self.calculate_mlc_attribute(mlcx2_aperture, cumulative_metersets, beam),
            )
        return self.calculate_mlc_attribute(apertures, cumulative_metersets, beam)

    def calculate_mlc_attribute(self, apertures, cumulative_mu, beam):
        mlc_attributes = MLCAttributes(
            apertures,
            cumulative_mu,
            beam["TreatmentMachineName"],
            beam["DoseRateSet"],
            beam["GantryRotationAngle"],
        )

        mlc_speed_proportion = self.calculate_for_speed_proportion(mlc_attributes.get_mlc_speed())
        mlc_acc_proportion = self.calculate_for_acc_proportion(mlc_attributes.get_mlc_acc())
        mlc_speed_acc_avg_std = [
            mlc_attributes.get_mlc_speed_avg(),
            mlc_attributes.get_mlc_acc_avg(),
            mlc_attributes.get_mlc_speed_std_avg(),
            mlc_attributes.get_mlc_acc_std_avg(),
        ]

        return mlc_speed_proportion, mlc_acc_proportion, mlc_speed_acc_avg_std

    def calculate_for_speed_proportion(self, mlc_speed) -> List[float]:
        return self._calculate_leaf_average_proportions(mlc_speed, self.SPEED_BINS_MM_PER_S)

    def calculate_for_acc_proportion(self, mlc_acceleration) -> List[float]:
        return self._calculate_leaf_average_proportions(mlc_acceleration, self.ACC_BINS_MM_PER_S2)

    @staticmethod
    def _calculate_leaf_average_proportions(values, bins: Sequence[Sequence[float]]) -> List[float]:
        array = np.asarray(values, dtype=float)
        if array.ndim != 2 or array.shape[1] == 0:
            return [np.nan] * len(bins)

        per_leaf = []
        for leaf_index in range(array.shape[1]):
            leaf_values = array[:, leaf_index]
            leaf_values = leaf_values[np.isfinite(leaf_values)]
            if leaf_values.size == 0:
                continue
            proportions = []
            for lower, upper in bins[:-1]:
                # Park 2015 reports the proportion within each motion bin. We first
                # compute that proportion per leaf, then average over all leaves.
                proportions.append(np.mean((leaf_values >= lower) & (leaf_values < upper)))
            lower, upper = bins[-1]
            proportions.append(np.mean((leaf_values >= lower) & (leaf_values <= upper)))
            per_leaf.append(proportions)

        if not per_leaf:
            return [np.nan] * len(bins)
        return np.nanmean(np.asarray(per_leaf, dtype=float), axis=0).tolist()

    @staticmethod
    def _weighted_average(values: Iterable[Sequence[float]], weights: Sequence[float]):
        values = list(values)
        if not values:
            return np.asarray([])
        return np.average(np.asarray(values, dtype=float), axis=0, weights=np.asarray(weights, dtype=float))



