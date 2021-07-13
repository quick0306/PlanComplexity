import warnings

import numpy as np
import pandas as pd


class MLCAttributes:
    def __init__(self, apertures, cumulative_mu, treatment_machine_name, dose_rate_set,
                 gantry_rotation_angle) -> None:
        # beam data
        self.treatment_machine_name = treatment_machine_name
        self.dose_rate_set = dose_rate_set
        self.gantry_rotation_angle = gantry_rotation_angle
        self.apertures = apertures
        self.Ncp = len(self.apertures)

        # meterset data
        self.delta_mu_time = self.get_delta_mu_data(cumulative_mu)

        # MLC position data
        self.mlc_positions = self.get_positions()
        self.mlc_speed = (self.mlc_positions.diff().abs().T / self.delta_mu_time['time']).T
        self.mlc_speed_std = self.mlc_speed.std()

        self.mlc_acc = (self.mlc_speed.diff().abs().T / self.delta_mu_time['time']).T
        self.mlc_acc_std = self.mlc_acc.std()

        # gantry data
        gantry_angles = np.array([ap.GantryAngle for ap in self.apertures])
        self.gantry = pd.DataFrame(gantry_angles, columns=['gantry'])
        self.gantry['delta_gantry'] = self.rolling_apply(self.delta_gantry, gantry_angles)
        self.gantry['gantry_speed'] = self.gantry['delta_gantry'] / self.delta_mu_time['time']
        self.gantry['delta_gantry_speed'] = self.gantry['gantry_speed'].diff().abs()
        self.gantry['gantry_acc'] = self.gantry['delta_gantry_speed'] / self.delta_mu_time['time']

        # dose rate data
        self.dose_rate = pd.DataFrame(
            self.delta_mu_time['delta_mu'] / self.delta_mu_time['time'], columns=['DR'])
        self.dose_rate['delta_dose_rate'] = self.dose_rate.diff().abs()

    def get_delta_mu_data(self, cumulative_mu):
        # meterset data
        tmp = pd.DataFrame(cumulative_mu, columns=['MU'])
        tmp['delta_mu'] = tmp.diff().abs()
        tmp['time'] = tmp['delta_mu'].apply(self.calculate_time)
        return tmp

    def calculate_time(self, delta_mu):
        """计算控制点时间（Calculate time between control points in seconds）
        :param delta_mu:
        :return: time in seconds
        """
        # 当前方法Trilogy, dose rate为600 MU/min
        if self.treatment_machine_name == 'TRILOGY-SN5602':
            # Gantry最大速度匀速旋转条件下，单位控制点MU为delta,当前控制点MU大于delta说明机架有降速
            delta = ((self.gantry_rotation_angle / self.Ncp) / 4.8) * (self.dose_rate_set / 60)
            if delta_mu <= delta:
                return (self.gantry_rotation_angle / self.Ncp) / 4.8
            elif delta_mu > delta:
                return delta_mu / (self.dose_rate_set / 60)
        elif self.treatment_machine_name == 'TrueBeamSN1352' \
                or self.treatment_machine_name == 'TrueBeamSN2716':
            delta = ((self.gantry_rotation_angle / self.Ncp) / 6.0) * (self.dose_rate_set / 60)
            if delta_mu <= delta:
                return (self.gantry_rotation_angle / self.Ncp) / 6.0
            elif delta_mu > delta:
                return delta_mu / (self.dose_rate_set / 60)
        else:
            warnings.warn("当前只有Varian机器可计算控制点时间，Monaco控制点时间计算待确定？？？")

    def get_positions(self):
        pos = []
        for aperture in self.apertures:
            cp_pos = [(lp.Left, lp.Right) for lp in aperture.LeafPairs]
            arr = np.ravel(cp_pos)  # 返回一个扁平数组
            pos.append(arr)

        return pd.DataFrame(pos)

    @staticmethod
    def delta_gantry(param):
        alpha, beta = param
        phi = abs(beta - alpha) % 360
        return 360 - phi if phi > 180 else phi

    @staticmethod
    def rolling_apply(fun, a, w=2):
        r = np.empty(a.shape)
        r.fill(np.nan)
        for i in range(w - 1, a.shape[0]):
            r[i] = fun(a[(i - w + 1):i + 1])
        return r

    def MLCSpeed(self) -> pd.DataFrame:
        return self.mlc_speed

    def MLCAcc(self) -> pd.DataFrame:
        return self.mlc_acc

    def MLCSpeedAvg(self) -> float:
        # 排除MLC速度为0叶片，其显著影响平均值计算
        mlc_speed_nonzero = self.mlc_speed.replace(0, np.NaN)
        mlc_speed_avg = np.mean(mlc_speed_nonzero.mean())
        return mlc_speed_avg

    def MLCSpeedStdAvg(self) -> float:
        # 排除MLC速度标准差为0叶片，其显著影响平均值计算
        mlc_speed_std_nonzero = self.mlc_speed_std.replace(0, np.NaN)
        mlc_speed_std_avg = np.mean(mlc_speed_std_nonzero.mean())
        return mlc_speed_std_avg

    def MLCAccAvg(self):
        # 排除MLC加速度为0叶片，其显著影响平均值计算
        mlc_acc_nonzero = self.mlc_acc.replace(0, np.NaN)
        mlc_acc_avg = np.mean(mlc_acc_nonzero.mean())
        return mlc_acc_avg

    def MLCAccStdAvg(self) -> float:
        # 排除MLC加速度标准差为0叶片，其显著影响平均值计算
        mlc_acc_std_nonzero = self.mlc_acc_std.replace(0, np.NaN)
        mlc_acc_std_avg = np.mean(mlc_acc_std_nonzero.mean())
        return mlc_acc_std_avg
