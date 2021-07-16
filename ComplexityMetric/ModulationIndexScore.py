import numpy as np
from scipy import integrate

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.ApertureCreator import AperturesFromBeamCreator
from ApertureMetric.MetersetCreator import MetersetsFromMetersetWeightsCreator
from ApertureMetric.MLCAttributes import MLCAttributes


class ModulationIndexScore(ComplexityMetric):
    """计算VMAT计划MLC速度、加速度、机架加速度和剂量率变化调制指数（Modulation Index for Speed
    and Acceleration of MLC, Gantry Acceleration and Dose Rate Variation, MIs, MIa, MIt）

    注意：该复杂性指标需要控制点时间信息，当前只适应于Eclipse TPS VAMT（Varian设备？），而Elekta
    设备执行时剂量率和机架速度均在变化，由DICOM RT无法得到控制点时间
    Reference:
        Park JM, et al. Modulation indices for volumetric modulated Arc therapy. Phys Med Biol 2014; 59: 7315–40.
        DOI: https://doi.org/10.1088/0031-9155/59/23/7315
    """

    def CalculateForPlan(self, plan=None, k=0.02):
        mi = []
        for i, beam in plan['beams'].items():
            mi.append(self.CalculateForBeam(beam, k))

        mi_weight = []
        weights = self.GetWeightsPlan(plan)
        for tmp in np.array(mi).T:      # 转置后每一行分别代表mis, mia和mit
            mi_weight.append(self.WeightedSum(weights, tmp))

        return np.round(mi_weight, 2)

    def CalculateForBeam(self, beam, k=0.02):
        apertures = AperturesFromBeamCreator().Create(beam)
        cumulative_metersets = MetersetsFromMetersetWeightsCreator().GetCumulativeMetersets(beam)
        mid = ModulationIndexTotal(apertures, cumulative_metersets, beam['TreatmentMachineName'],
                                   beam['DoseRateSet'], beam['GantryRotationAngle'])
        return mid.calculate_integrate(k=k)


class ModulationIndexTotal(MLCAttributes):
    """Modulation index total"""
    def __init__(self, apertures, cumulative_mu, treatment_machine_name,
                 dose_rate_set, gantry_rotation_angle) -> None:
        # beam data
        super().__init__(apertures, cumulative_mu, treatment_machine_name,
                         dose_rate_set, gantry_rotation_angle)

    def calc_mi_speed(self, mlc_speed, speed_std, k=1.0):

        calc_z = lambda f: 1 / (self.Ncp - 1) * np.sum(np.sum(mlc_speed > f * speed_std))
        res = integrate.quad(calc_z, 0, k, full_output=1)
        return res[0]

    def calc_mi_acceleration(self, mlc_speed, speed_std, mlc_acc, mlc_acc_std, k=1.0, alpha=1.0):

        z_acc = lambda f: (1 / (self.Ncp - 2)) * np.nansum(np.nansum(np.logical_or(mlc_speed > f * speed_std,
                                                                                   mlc_acc > alpha * f * mlc_acc_std)))
        res = integrate.quad(z_acc, 0, k, full_output=1)
        return res[0]

    def calc_mi_total(self, mlc_speed, speed_std, mlc_acc, mlc_acc_std, k=1.0, alpha=1.0, WGA=None, WMU=None):

        z_total = lambda f: (1 / (self.Ncp - 2)) * \
                            np.nansum(np.nansum(np.logical_or(mlc_speed > f * speed_std,
                                                              mlc_acc > alpha * f * mlc_acc_std), axis=1) * WGA * WMU)

        res = integrate.quad(z_total, 0, k, full_output=1)
        return res[0]

    def calculate_integrate(self, k=1.0, beta=2.0, alpha=2.0):

        # fill NAN
        mlc_speed = np.nan_to_num(self.mlc_speed)
        mlc_acc = np.nan_to_num(self.mlc_acc)

        mis = self.calc_mi_speed(mlc_speed, self.mlc_speed_std.values, k)

        alpha_acc = 1.0 / self.delta_mu_time['time'].mean()
        mia = self.calc_mi_acceleration(mlc_speed, self.mlc_speed_std.values,
                                        mlc_acc, self.mlc_acc_std.values,
                                        k=k, alpha=alpha_acc)

        gantry_acc = self.gantry['gantry_acc'].values
        WGA = beta / (1 + (beta - 1) * np.exp(-gantry_acc / alpha))
        # Wmu
        delta_dose_rate = self.dose_rate['delta_dose_rate'].values
        WMU = beta / (1 + (beta - 1) * np.exp(-delta_dose_rate / alpha))
        mit = self.calc_mi_total(mlc_speed,
                                 self.mlc_speed_std.values,
                                 mlc_acc,
                                 self.mlc_acc_std.values,
                                 k=k, alpha=alpha_acc, WGA=WGA, WMU=WMU)

        return mis, mia, mit

    def calculate_split(self, f=1.0, beta=2.0, alpha=2.0):

        # speed MI
        mask_speed_std = self.mlc_speed > f * self.mlc_speed_std
        Ns = mask_speed_std.sum().sum()
        z_speed = 1 / (self.Ncp - 1) * Ns

        # acc MI
        alpha_acc = 1.0 / self.delta_mu_time['time'].mean()
        mask_acc_std = self.mlc_acc > alpha_acc * f * self.mlc_acc_std

        mask_acc_mi = np.logical_or(mask_speed_std, mask_acc_std)
        Nacc = mask_acc_mi.sum().sum()
        z_acc = 1 / (self.Ncp - 2) * Nacc

        # Total MI
        gantry_acc = self.gantry['gantry_acc']
        WGA = beta / (1 + (beta - 1) * np.exp(-gantry_acc / alpha))

        # Wmu
        delta_dose_rate = self.dose_rate['delta_dose_rate']
        WMU = beta / (1 + (beta - 1) * np.exp(-delta_dose_rate / alpha))

        tmp = mask_acc_mi.multiply(WGA, axis='index').multiply(WMU, axis='index')
        Mti = tmp.sum().sum() / (self.Ncp - 2)

        return z_speed, z_acc, Mti
