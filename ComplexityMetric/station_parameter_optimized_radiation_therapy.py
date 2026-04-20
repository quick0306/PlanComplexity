from typing import Dict, List, Tuple, Union

import numpy as np

from ApertureMetric.aperture_geometry import PyAperture
from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ApertureMetric.meterset_creator import MetersetsFromMetersetWeightsCreator
from ComplexityMetric.complexity_metric import ComplexityMetric


class StationParameterOptimizedRadiationTherapy(ComplexityMetric):
    """SPORT complexity metric.

    Reference:
        Li R, Xing L. An adaptive planning strategy for station parameter optimized
        radiation therapy (SPORT): segmentally boosted VMAT. Med Phys. 2013;40(5):050701.
        DOI: 10.1118/1.4802748

    Notes:
        The paper defines the station-wise modulation index MI(s). This class keeps
        that station formula and then uses the framework's beam/plan aggregation to
        produce a single summary value for reporting.
    """

    aggregation_mode = "mu"
    NEIGHBORHOOD = 10

    def calculate_for_beam(self, beam: Dict[str, str]) -> Union[Tuple[float, float], float]:
        weights = self.get_weights_beam(beam)
        if "halcyon" in beam["TreatmentMachineName"].lower() or "ethos" in beam["TreatmentMachineName"].lower():
            mlcx1_values, mlcx2_values = self.get_metrics_beam(beam)
            return (
                self._weighted_station_average(weights, mlcx1_values),
                self._weighted_station_average(weights, mlcx2_values),
            )
        values = self.get_metrics_beam(beam)
        return self._weighted_station_average(weights, values)

    def get_metrics_beam(self, beam: Dict[str, str]) -> Union[Tuple[List[float], List[float]], List[float]]:
        cumulative_mu = MetersetsFromMetersetWeightsCreator().get_cumulative_metersets(beam)
        apertures = AperturesFromBeamCreator().create(beam)
        if "halcyon" in beam["TreatmentMachineName"].lower() or "ethos" in beam["TreatmentMachineName"].lower():
            mlcx1_aperture = apertures[0::2]
            mlcx2_aperture = apertures[1::2]
            return (
                self.calculate_per_aperture(mlcx1_aperture, cumulative_mu),
                self.calculate_per_aperture(mlcx2_aperture, cumulative_mu),
            )
        return self.calculate_per_aperture(apertures, cumulative_mu)

    def calculate_per_aperture(self, apertures: List[PyAperture], cumulative_mu: List[float]) -> List[float]:
        """Calculate the SPORT station-wise MI(s) from the paper."""
        station_count = len(apertures)
        if station_count == 0:
            return []

        mi_sport = np.zeros(station_count, dtype=float)
        cumulative_mu = np.asarray(cumulative_mu, dtype=float)

        for station_index in range(station_count):
            station_sum = 0.0
            for offset in range(-self.NEIGHBORHOOD, self.NEIGHBORHOOD + 1):
                if offset == 0:
                    continue
                neighbor_index = station_index + offset
                if neighbor_index < 0 or neighbor_index >= station_count:
                    continue

                delta_angle = self._shortest_gantry_distance(
                    apertures[station_index].gantry_angle,
                    apertures[neighbor_index].gantry_angle,
                )
                if delta_angle <= 0:
                    continue

                delta_mu = abs(cumulative_mu[station_index] - cumulative_mu[neighbor_index])
                mlc_motion = self._leaf_motion_distance(apertures[station_index], apertures[neighbor_index])
                station_sum += mlc_motion * (delta_mu / delta_angle)

            mi_sport[station_index] = station_sum

        return mi_sport.tolist()

    @staticmethod
    def _leaf_motion_distance(aperture_a: PyAperture, aperture_b: PyAperture) -> float:
        total = 0.0
        for leaf_pair_a, leaf_pair_b in zip(aperture_a.leaf_pairs, aperture_b.leaf_pairs):
            total += abs(leaf_pair_a.left - leaf_pair_b.left) + abs(leaf_pair_a.right - leaf_pair_b.right)
        return total

    @staticmethod
    def _shortest_gantry_distance(angle_a: float, angle_b: float) -> float:
        phi = abs(float(angle_a) - float(angle_b)) % 360.0
        return 360.0 - phi if phi > 180.0 else phi

    @staticmethod
    def _weighted_station_average(weights, values) -> float:
        values = np.asarray(values, dtype=float)
        if values.size == 0:
            return 0.0

        weights = np.asarray(weights, dtype=float)
        if weights.size != values.size:
            usable = min(weights.size, values.size)
            weights = weights[:usable]
            values = values[:usable]

        if weights.size == 0 or np.allclose(weights.sum(), 0.0):
            return float(np.nanmean(values))
        return float(np.average(values, weights=weights))




