from typing import Dict

import numpy as np


class MetersetsFromMetersetWeightsCreator:
    """Calculate control point MU"""
    def Create(self, beam: Dict[str, str]) -> np.ndarray:
        if beam["PrimaryDosimeterUnit"] != "MU":
            return None

        metersetWeights = self.GetMetersetWeights(beam["ControlPointSequence"])
        metersets = self.ConvertMetersetWeightsToMetersets(beam["MU"], metersetWeights)

        return self.UndoCummulativeSum(metersets)

    def GetCumulativeMetersets(self, beam):
        metersetWeights = self.GetMetersetWeights(beam["ControlPointSequence"])
        metersets = self.ConvertMetersetWeightsToMetersets(beam["MU"], metersetWeights)
        return metersets

    @staticmethod
    def GetMetersetWeights(ControlPoints):
        return np.array([cp.CumulativeMetersetWeight for cp in ControlPoints], dtype=float)

    @staticmethod
    def ConvertMetersetWeightsToMetersets(beamMeterset, metersetWeights):
        return beamMeterset * metersetWeights / metersetWeights[-1]

    @staticmethod
    def UndoCummulativeSum(cummulativeSum):
        """Returns the values whose cummulative sum is "cummulativeSum" """
        values = np.zeros(len(cummulativeSum))
        delta_prev = 0.0
        for i in range(len(values) - 1):
            delta_curr = cummulativeSum[i + 1] - cummulativeSum[i]
            values[i] = 0.5 * delta_prev + 0.5 * delta_curr
            delta_prev = delta_curr

        values[-1] = 0.5 * delta_prev

        return values
