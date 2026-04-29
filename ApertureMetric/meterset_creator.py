from typing import Dict

import numpy as np


class MetersetsFromMetersetWeightsCreator:
    """Calculate control point MU"""
    def create(self, beam: Dict[str, str]) -> np.ndarray:
        if beam["PrimaryDosimeterUnit"] != "MU":
            return None

        cached_values = beam.get("_cached_cp_metersets")
        if cached_values is not None:
            return cached_values

        meterset_weights = self.get_meterset_weights(beam["ControlPointSequence"])
        metersets = self.convert_meterset_weights_to_metersets(beam["MU"], meterset_weights)
        cp_values = self.undo_cumulative_sum(metersets)
        beam["_cached_cp_metersets"] = cp_values
        beam["_cached_cumulative_metersets"] = metersets
        return cp_values

    def get_cumulative_metersets(self, beam):
        cached_values = beam.get("_cached_cumulative_metersets")
        if cached_values is not None:
            return cached_values
        meterset_weights = self.get_meterset_weights(beam["ControlPointSequence"])
        metersets = self.convert_meterset_weights_to_metersets(beam["MU"], meterset_weights)
        beam["_cached_cumulative_metersets"] = metersets
        return metersets

    @staticmethod
    def get_meterset_weights(control_points):
        return np.array([cp.CumulativeMetersetWeight for cp in control_points], dtype=float)

    @staticmethod
    def convert_meterset_weights_to_metersets(beam_meterset, meterset_weights):
        return beam_meterset * meterset_weights / meterset_weights[-1]

    @staticmethod
    def undo_cumulative_sum(cumulative_sum):
        """Returns the values whose cumulative sum is ``cumulative_sum``."""
        values = np.zeros(len(cumulative_sum))
        delta_prev = 0.0
        for i in range(len(values) - 1):
            delta_curr = cumulative_sum[i + 1] - cumulative_sum[i]
            values[i] = 0.5 * delta_prev + 0.5 * delta_curr
            delta_prev = delta_curr

        values[-1] = 0.5 * delta_prev

        return values


