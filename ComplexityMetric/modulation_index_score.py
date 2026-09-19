import numpy as np

from ApertureMetric.aperture_creator import AperturesFromBeamCreator
from ApertureMetric.meterset_creator import MetersetsFromMetersetWeightsCreator
from ApertureMetric.mlc_attributes import MLCAttributes
from ComplexityMetric.complexity_metric import ComplexityMetric


class ModulationIndexScore(ComplexityMetric):
    """Modulation indices for VMAT delivery dynamics.

    Reference:
        Park JM, et al. Modulation indices for volumetric modulated Arc therapy.
        Phys Med Biol. 2014;59(23):7315-7340.
        DOI: 10.1088/0031-9155/59/23/7315
    """

    def calculate_for_plan(self, plan=None, k=0.02):
        weights = self.get_weights_plan(plan)
        mi = []
        for _, beam in plan["beams"].items():
            mi.append(self.calculate_for_beam(beam, k))

        if "halcyon" in plan["machine_id"].lower() or "ethos" in plan["machine_id"].lower():
            mlcx1_mi = [m[0] for m in mi]
            mlcx2_mi = [m[1] for m in mi]

            mlcx1_mi_weight = []
            mlcx2_mi_weight = []

            for tmp in np.array(mlcx1_mi).T:
                mlcx1_mi_weight.append(self.weighted_sum(weights, tmp))
            for tmp in np.array(mlcx2_mi).T:
                mlcx2_mi_weight.append(self.weighted_sum(weights, tmp))
            return self.format_result(mlcx1_mi_weight), self.format_result(mlcx2_mi_weight)

        mi_weight = []
        for tmp in np.array(mi).T:
            mi_weight.append(self.weighted_sum(weights, tmp))
        return self.format_result(mi_weight)

    def calculate_for_beam(self, beam, k=0.02):
        cumulative_metersets = MetersetsFromMetersetWeightsCreator().get_cumulative_metersets(beam)

        if "halcyon" in beam["TreatmentMachineName"].lower() or "ethos" in beam["TreatmentMachineName"].lower():
            apertures = AperturesFromBeamCreator().create(beam)
            mlcx1_aperture = apertures[0::2]
            mlcx2_aperture = apertures[1::2]
            mlcx1_mid = ModulationIndexTotal(
                mlcx1_aperture,
                cumulative_metersets,
                beam["TreatmentMachineName"],
                beam["DoseRateSet"],
                beam["GantryRotationAngle"],
            )
            mlcx2_mid = ModulationIndexTotal(
                mlcx2_aperture,
                cumulative_metersets,
                beam["TreatmentMachineName"],
                beam["DoseRateSet"],
                beam["GantryRotationAngle"],
            )
            return mlcx1_mid.calculate_integrate(k=k), mlcx2_mid.calculate_integrate(k=k)

        apertures = AperturesFromBeamCreator().create(beam)
        mid = ModulationIndexTotal(
            apertures,
            cumulative_metersets,
            beam["TreatmentMachineName"],
            beam["DoseRateSet"],
            beam["GantryRotationAngle"],
        )
        return mid.calculate_integrate(k=k)


class ModulationIndexTotal(MLCAttributes):
    """Closed-form implementation of Park 2014 MI metrics."""

    def calc_mi_speed(self, mlc_speed, speed_std, k=1.0):
        thresholds = _ratio_thresholds(mlc_speed, speed_std)
        contributions = np.minimum(thresholds, k)
        return float(np.nansum(contributions) / max(self.Ncp - 1, 1))

    def calc_mi_acceleration(self, mlc_speed, speed_std, mlc_acc, mlc_acc_std, k=1.0, alpha=1.0):
        speed_thresholds = _ratio_thresholds(mlc_speed, speed_std)
        acc_thresholds = _ratio_thresholds(mlc_acc, alpha * mlc_acc_std)
        contributions = np.minimum(np.maximum(speed_thresholds, acc_thresholds), k)
        return float(np.nansum(contributions) / max(self.Ncp - 2, 1))

    def calc_mi_total(self, mlc_speed, speed_std, mlc_acc, mlc_acc_std, k=1.0, alpha=1.0, WGA=None, WMU=None):
        speed_thresholds = _ratio_thresholds(mlc_speed, speed_std)
        acc_thresholds = _ratio_thresholds(mlc_acc, alpha * mlc_acc_std)
        thresholds = np.minimum(np.maximum(speed_thresholds, acc_thresholds), k)

        row_sums = np.nansum(thresholds, axis=1)
        weights = np.asarray(WGA, dtype=float) * np.asarray(WMU, dtype=float)
        usable = min(len(row_sums), len(weights))
        if usable == 0:
            return 0.0
        return float(np.nansum(row_sums[:usable] * weights[:usable]) / max(self.Ncp - 2, 1))

    def calculate_integrate(self, k=1.0, beta=2.0, alpha=2.0):
        mlc_speed = np.nan_to_num(np.asarray(self.mlc_speed, dtype=float), nan=0.0)
        mlc_acc = np.nan_to_num(np.asarray(self.mlc_acc, dtype=float), nan=0.0)
        speed_std = np.asarray(self.mlc_speed_std.values, dtype=float)
        acc_std = np.asarray(self.mlc_acc_std.values, dtype=float)

        mis = self.calc_mi_speed(mlc_speed, speed_std, k)

        mean_time = np.nanmean(np.asarray(self.delta_mu_time["time"], dtype=float))
        alpha_acc = 0.0 if not np.isfinite(mean_time) or mean_time <= 0 else 1.0 / mean_time
        mia = self.calc_mi_acceleration(mlc_speed, speed_std, mlc_acc, acc_std, k=k, alpha=alpha_acc)

        gantry_acc = np.asarray(self.gantry["gantry_acc"].values, dtype=float)
        WGA = beta / (1 + (beta - 1) * np.exp(-gantry_acc / alpha))

        delta_dose_rate = np.asarray(self.dose_rate["delta_dose_rate"].values, dtype=float)
        WMU = beta / (1 + (beta - 1) * np.exp(-delta_dose_rate / alpha))
        mit = self.calc_mi_total(
            mlc_speed,
            speed_std,
            mlc_acc,
            acc_std,
            k=k,
            alpha=alpha_acc,
            WGA=WGA,
            WMU=WMU,
        )

        return mis, mia, mit

    def calculate_split(self, f=1.0, beta=2.0, alpha=2.0):
        mask_speed_std = self.mlc_speed > f * self.mlc_speed_std
        Ns = mask_speed_std.sum().sum()
        z_speed = 1 / (self.Ncp - 1) * Ns

        alpha_acc = 1.0 / self.delta_mu_time["time"].mean()
        mask_acc_std = self.mlc_acc > alpha_acc * f * self.mlc_acc_std

        mask_acc_mi = np.logical_or(mask_speed_std, mask_acc_std)
        Nacc = mask_acc_mi.sum().sum()
        z_acc = 1 / (self.Ncp - 2) * Nacc

        gantry_acc = self.gantry["gantry_acc"]
        WGA = beta / (1 + (beta - 1) * np.exp(-gantry_acc / alpha))

        delta_dose_rate = self.dose_rate["delta_dose_rate"]
        WMU = beta / (1 + (beta - 1) * np.exp(-delta_dose_rate / alpha))

        tmp = mask_acc_mi.multiply(WGA, axis="index").multiply(WMU, axis="index")
        Mti = tmp.sum().sum() / (self.Ncp - 2)

        return z_speed, z_acc, Mti


def _ratio_thresholds(values, scales):
    values_arr = np.asarray(values, dtype=float)
    scales_arr = np.asarray(scales, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        # The original MI integrals reduce to integrating an indicator function
        # over f in [0, k]. That area is just min(value / scale, k) per element.
        thresholds = values_arr / scales_arr
    thresholds = np.where((scales_arr == 0) & (values_arr > 0), np.inf, thresholds)
    thresholds = np.where((scales_arr == 0) & (values_arr <= 0), 0.0, thresholds)
    thresholds = np.where(np.isnan(thresholds), 0.0, thresholds)
    thresholds = np.where(thresholds < 0.0, 0.0, thresholds)
    return thresholds



