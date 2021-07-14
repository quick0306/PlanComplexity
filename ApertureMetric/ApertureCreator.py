from typing import List, Dict
import numpy as np

from pydicom.dataset import Dataset

from ApertureMetric.Aperture import PyAperture


class AperturesFromBeamCreator:
    """计算控制点子野（Apertures）信息"""

    def Create(self, beam: Dict[str, str]) -> List[PyAperture]:
        apertures = []

        # BeamLimitingDeviceSequence LeafPositionBoundaries
        leafWidths = self.GetLeafWidths(beam)

        for controlPoint in beam["ControlPointSequence"]:
            gantry_angle = float(controlPoint.GantryAngle) if "GantryAngle" in controlPoint else beam["GantryAngle"]
            leafPositions = self.GetLeafPositions(controlPoint)
            jaw = self.GetJawPositions(beam, controlPoint)  # Jaw Tracking
            if leafPositions is not None:
                apertures.append(PyAperture(leafPositions, leafWidths, jaw, gantry_angle))

        return apertures

    def GetJawPositions(self, beam: dict, control_point: Dataset) -> List[float]:
        """得到每个控制点Jaw位置，铅门跟随方式每个控制点Jaw位置在变化"""
        left, right, top, bottom = -200.0, 200.0, -200.0, 200.0
        BeamLimitingDeviceType = []
        if "BeamLimitingDevicePositionSequence" in control_point:
            for bl in control_point.BeamLimitingDevicePositionSequence:
                BeamLimitingDeviceType.append(bl.RTBeamLimitingDeviceType)
                if bl.RTBeamLimitingDeviceType == "ASYMX":
                    left = float(bl.LeafJawPositions[0])
                    right = float(bl.LeafJawPositions[1])
                if bl.RTBeamLimitingDeviceType == "ASYMY":
                    top = float(bl.LeafJawPositions[0])
                    bottom = float(bl.LeafJawPositions[1])

        if "ASYMX" not in BeamLimitingDeviceType and "ASYMX" in beam:
            left = float(beam['ASYMX'][0])
            right = float(beam['ASYMX'][1])
        if "ASYMY" not in BeamLimitingDeviceType and "ASYMX" in beam:
            top = float(beam['ASYMY'][0])
            bottom = float(beam['ASYMY'][1])

        # Invert y axis to match apperture class -top, -botton that uses Varian standard ESAPI
        return [left, -top, right, -bottom]

    def GetLeafWidths(self, beam_dict: Dict) -> np.ndarray:
        """Get MLCX leaf width from  BeamLimitingDeviceSequence (300a, 00be) Leaf Position Boundaries Tag"""
        bs = beam_dict["BeamLimitingDeviceSequence"]
        # the script only takes MLCX as parameter
        for b in bs:
            if b.RTBeamLimitingDeviceType in ["MLCX", "MLCX1", "MLCX2"]:
                return np.diff(b.LeafPositionBoundaries)

    def GetLeafPositions(self, control_point: Dataset) -> np.ndarray:
        """Leaf positions are given from bottom to top by ESAPI, but the Aperture class expects them
        from top to bottom Leaf Positions are mechanical boundaries projected onto Isocenter plane"""
        if "BeamLimitingDevicePositionSequence" in control_point:
            pos = control_point.BeamLimitingDevicePositionSequence[-1]
            mlc_open = pos.LeafJawPositions
            n_pairs = int(len(mlc_open) / 2)
            bank_a_pos = mlc_open[:n_pairs]
            bank_b_pos = mlc_open[n_pairs:]

            return np.vstack((bank_a_pos, bank_b_pos))
