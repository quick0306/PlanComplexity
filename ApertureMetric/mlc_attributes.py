import warnings

import numpy as np
import pandas as pd


class MLCAttributes:
    """Leaf motion attributes derived from consecutive control points."""

    MAX_GANTRY_SPEED_DEG_PER_S = {
        "trilogy": 4.8,
        "truebeam": 6.0,
        "edge": 6.0,
        "halcyon": 24.0,
        "ethos": 24.0,
    }

    def __init__(
        self,
        apertures,
        cumulative_mu,
        treatment_machine_name,
        dose_rate_set,
        gantry_rotation_angle,
    ) -> None:
        self.treatment_machine_name = treatment_machine_name or ""
        self.dose_rate_set = float(dose_rate_set) if dose_rate_set not in (None, "") else 0.0
        self.gantry_rotation_angle = float(gantry_rotation_angle) if gantry_rotation_angle not in (None, "") else 0.0
        self.apertures = apertures
        self.Ncp = len(self.apertures)

        gantry_angles = np.array([float(ap.gantry_angle) for ap in self.apertures], dtype=float)
        self.delta_mu_time = self.get_delta_mu_data(cumulative_mu, gantry_angles)

        self.mlc_positions = self.get_positions()
        self.mlc_speed = self._divide_by_interval(self.mlc_positions.diff().abs(), self.delta_mu_time["time"])
        self.mlc_speed_std = self.mlc_speed.std()

        self.mlc_acc = self._divide_by_interval(self.mlc_speed.diff().abs(), self.delta_mu_time["time"])
        self.mlc_acc_std = self.mlc_acc.std()

        self.gantry = pd.DataFrame({"gantry": gantry_angles})
        self.gantry["delta_gantry"] = self.delta_mu_time["delta_gantry"]
        self.gantry["gantry_speed"] = self._safe_series_divide(
            self.gantry["delta_gantry"], self.delta_mu_time["time"]
        )
        self.gantry["delta_gantry_speed"] = self.gantry["gantry_speed"].diff().abs()
        self.gantry["gantry_acc"] = self._safe_series_divide(
            self.gantry["delta_gantry_speed"], self.delta_mu_time["time"]
        )

        self.dose_rate = pd.DataFrame(
            {"DR": self._safe_series_divide(self.delta_mu_time["delta_mu"], self.delta_mu_time["time"])}
        )
        self.dose_rate["delta_dose_rate"] = self.dose_rate["DR"].diff().abs()

    def get_delta_mu_data(self, cumulative_mu, gantry_angles):
        tmp = pd.DataFrame({"MU": np.asarray(cumulative_mu, dtype=float)})
        tmp["delta_mu"] = tmp["MU"].diff().abs()
        tmp["delta_gantry"] = self._delta_gantry_series(gantry_angles)
        tmp["time"] = [
            self.calculate_time(delta_mu, delta_gantry)
            for delta_mu, delta_gantry in zip(tmp["delta_mu"], tmp["delta_gantry"])
        ]
        return tmp

    def calculate_time(self, delta_mu, delta_gantry):
        """Estimate delivery time between adjacent control points in seconds.

        For Eclipse/Varian plans the control-point interval is limited by the slower of:
        1. gantry rotation at the machine maximum speed
        2. dose delivery at the planned dose rate
        """
        if pd.isna(delta_mu) or pd.isna(delta_gantry):
            return np.nan

        gantry_limited_time = np.nan
        max_gantry_speed = self._get_max_gantry_speed()
        if max_gantry_speed and delta_gantry > 0:
            gantry_limited_time = float(delta_gantry) / max_gantry_speed

        dose_rate_limited_time = np.nan
        if self.dose_rate_set > 0:
            dose_rate_limited_time = float(delta_mu) / (self.dose_rate_set / 60.0)

        candidates = [value for value in (gantry_limited_time, dose_rate_limited_time) if np.isfinite(value)]
        if candidates:
            return max(candidates)

        warnings.warn(
            "Unable to derive control-point time from gantry speed or dose rate; leaf speed metrics may be NaN.",
            stacklevel=2,
        )
        return np.nan

    def get_positions(self):
        positions = []
        for aperture in self.apertures:
            cp_pos = [(lp.left, lp.right) for lp in aperture.leaf_pairs]
            positions.append(np.ravel(cp_pos))
        return pd.DataFrame(positions)

    def get_mlc_speed(self) -> pd.DataFrame:
        return self.mlc_speed

    def get_mlc_acc(self) -> pd.DataFrame:
        return self.mlc_acc

    def get_mlc_speed_avg(self) -> np.ndarray:
        mlc_speed_nonzero = self.mlc_speed.replace(0, np.nan)
        return np.mean(mlc_speed_nonzero.mean())

    def get_mlc_speed_std_avg(self) -> np.ndarray:
        mlc_speed_std_nonzero = self.mlc_speed_std.replace(0, np.nan)
        return np.mean(mlc_speed_std_nonzero.mean())

    def get_mlc_acc_avg(self) -> np.ndarray:
        mlc_acc_nonzero = self.mlc_acc.replace(0, np.nan)
        return np.mean(mlc_acc_nonzero.mean())

    def get_mlc_acc_std_avg(self) -> np.ndarray:
        mlc_acc_std_nonzero = self.mlc_acc_std.replace(0, np.nan)
        return np.mean(mlc_acc_std_nonzero.mean())

    def _get_max_gantry_speed(self):
        machine_name = self.treatment_machine_name.lower()
        for token, speed in self.MAX_GANTRY_SPEED_DEG_PER_S.items():
            if token in machine_name:
                return speed
        return None

    @staticmethod
    def _delta_gantry_series(gantry_angles):
        deltas = [np.nan]
        for current, previous in zip(gantry_angles[1:], gantry_angles[:-1]):
            phi = abs(float(current) - float(previous)) % 360.0
            deltas.append(360.0 - phi if phi > 180.0 else phi)
        return deltas

    @staticmethod
    def _safe_series_divide(numerator, denominator):
        numerator_series = pd.Series(numerator, dtype=float)
        denominator_series = pd.Series(denominator, dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            result = numerator_series / denominator_series
        return result.replace([np.inf, -np.inf], np.nan)

    def _divide_by_interval(self, dataframe, interval_series):
        denominator = pd.Series(interval_series, dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            result = dataframe.div(denominator, axis=0)
        return result.replace([np.inf, -np.inf], np.nan)


