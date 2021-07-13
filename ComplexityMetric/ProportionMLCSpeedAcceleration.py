from typing import Dict, List
import warnings

import numpy as np

from ComplexityMetric.ComplexityMetric import ComplexityMetric
from ApertureMetric.ApertureCreator import AperturesFromBeamCreator
from ApertureMetric.MetersetCreator import MetersetsFromMetersetWeightsCreator
from ApertureMetric.MLCAttributes import MLCAttributes


class ProportionMLCSpeedAcceleration(ComplexityMetric):
    """根据MLC速度和加速度，计算特定范围内控制点所占比例

    考虑到Trilogy和TrueBeam，EDGE不一样速度范围：
        计算Trilogy MLC速度在（0，4），（4，8），（4，12）,(12，16)及（16，20）mm/s比例
        计算TrueBeam和EDGE MLC速度在（0，4），（4，8），（4，12）, (12，16)，（16，20）及（20，25）mm/s比例
    MLC加速度范围较大，但是99%在（0，60）mm/s2之间，因而统一考虑为（0，10），（10，20），（20，40）及（40，60）mm/s2

    注意：该复杂性指标需要控制点时间信息，当前只适应于Eclipse TPS（Varian设备？），而Elekta设备执行时剂量率
    和机架速度均在变化，由DICOM RT无法得到控制点时间
    Reference:
        Park JM, et al. The effect of MLC speed and acceleration on the plan delivery accuracy of VMAT.
        Br J Radiol 2015; 88(1049):20140698.
        DOI: https://doi.org/10.1259/bjr.20140698
    """

    def CalculateForPlan(self, plan: Dict[str, str]=None):
        speed_proportion = []
        acc_proportion = []
        speed_acc_avg_std = []

        for i, beam in plan['beams'].items():
            mlc_speed_proportion, mlc_acc_proportion, mlc_speed_acc_avg_std = self.CalculateForBeam(beam)

            speed_proportion.append(mlc_speed_proportion)
            acc_proportion.append(mlc_acc_proportion)
            speed_acc_avg_std.append(mlc_speed_acc_avg_std)

        # weights = self.GetWeightsPlan(plan)
        # speed_proportion_weight = self.WeightedSum(weights, speed_proportion)
        # acc_proportion_weight = self.WeightedSum(weights, acc_proportion)
        # speed_acc_avg_std_weight
        print(np.shape(speed_acc_avg_std))

        return np.mean(speed_proportion, axis=0), \
               np.mean(acc_proportion, axis=0), np.mean(speed_acc_avg_std, axis=0)

    def CalculateForBeam(self, beam: Dict[str, str]):
        apertures = AperturesFromBeamCreator().Create(beam)
        cumulative_metersets = MetersetsFromMetersetWeightsCreator().GetCumulativeMetersets(beam)

        mlc_attributes = MLCAttributes(apertures, cumulative_metersets, beam['TreatmentMachineName'],
                                   beam['DoseRateSet'], beam['GantryRotationAngle'])

        mlc_speed = mlc_attributes.MLCSpeed()
        mlc_acc = mlc_attributes.MLCAcc()

        # 计算MLC各档速度和加速度所占比重
        mlc_speed_proportion = self.CalculateForSpeedProportion(mlc_speed, beam['TreatmentMachineName'])
        mlc_acc_proportion = self.CalculateForAccProportion(mlc_acc)

        # 计算MLC速度和加速度平均值及标准差
        mlc_speed_avg = mlc_attributes.MLCSpeedAvg()
        mlc_acc_avg = mlc_attributes.MLCAccAvg()
        mlc_speed_std_avg = mlc_attributes.MLCSpeedStdAvg()
        mlc_acc_std_avg = mlc_attributes.MLCAccStdAvg()

        mlc_speed_acc_avg_std = [mlc_speed_avg, mlc_acc_avg, mlc_speed_std_avg, mlc_acc_std_avg]

        return mlc_speed_proportion, mlc_acc_proportion, mlc_speed_acc_avg_std

    def CalculateForSpeedProportion(self, mlc_speed, treatment_machine_name) -> List[float]:
        """计算各档MLC速度所占比例"""
        Ncp = mlc_speed.shape[0] * mlc_speed.shape[1]       # 计算MLC控制点总数

        # MLC速度分为5档（Trilogy），TrueBeam和EDGE为6档
        S_0_4 = np.sum(np.sum(np.logical_and(mlc_speed >= 0, mlc_speed < 4))) / Ncp
        S_4_8 = np.sum(np.sum(np.logical_and(mlc_speed >= 4, mlc_speed < 8))) / Ncp
        S_8_12 = np.sum(np.sum(np.logical_and(mlc_speed >= 8, mlc_speed < 12))) / Ncp
        S_12_16 = np.sum(np.sum(np.logical_and(mlc_speed >= 12, mlc_speed < 16))) / Ncp
        S_16_20 = np.sum(np.sum(np.logical_and(mlc_speed >= 16, mlc_speed < 20))) / Ncp

        if treatment_machine_name == 'TRILOGY-SN5602':
            return [S_0_4, S_4_8, S_8_12, S_12_16, S_16_20]
        elif treatment_machine_name == 'TrueBeamSN1352' or treatment_machine_name == 'TrueBeamSN2716':
            S_20_25 = np.sum(np.sum(np.logical_and(mlc_speed >= 20, mlc_speed < 25))) / Ncp
            return [S_0_4, S_4_8, S_8_12, S_12_16, S_16_20, S_20_25]
        else:
            warnings.warn("当前只有Varian机器可计算控制点时间，"
                          "Monaco控制点时间计算待确定，无法确定MLC速度和加速度？？？")

    def CalculateForAccProportion(self, mlc_acceleration) -> List[float]:
        """计算各档MLC加速度所占比例"""
        Ncp = mlc_acceleration.shape[0] * mlc_acceleration.shape[1]

        # MLC加速度分为4档
        A_0_10 = np.sum(np.sum(np.logical_and(mlc_acceleration >= 0, mlc_acceleration < 10))) / Ncp
        A_10_20 = np.sum(np.sum(np.logical_and(mlc_acceleration >= 10, mlc_acceleration < 20))) / Ncp
        A_20_40 = np.sum(np.sum(np.logical_and(mlc_acceleration >= 20, mlc_acceleration < 40))) / Ncp
        A_40_60 = np.sum(np.sum(np.logical_and(mlc_acceleration >= 40, mlc_acceleration < 60))) / Ncp

        return [A_0_10, A_10_20, A_20_40, A_40_60]

