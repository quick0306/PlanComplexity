from typing import Dict, List

import numpy as np
from pydicom.dataset import Dataset

from ApertureMetric.aperture_geometry import PyAperture


class AperturesFromBeamCreator:
    """Build per-control-point aperture geometry from a beam definition."""

    def create(self, beam: Dict[str, str]) -> List[PyAperture]:
        cached_apertures = beam.get("_cached_apertures")
        if cached_apertures is not None:
            return cached_apertures

        apertures: List[PyAperture] = []
        machine_name = beam["TreatmentMachineName"].lower()

        if "halcyon" in machine_name or "ethos" in machine_name:
            leaf_widths = self.get_leaf_widths(beam)
            for control_point in beam["ControlPointSequence"]:
                gantry_angle = float(control_point.GantryAngle) if "GantryAngle" in control_point else beam["GantryAngle"]
                leaf_mlcx1_positions = self.get_halcyon_leaf_positions(control_point, "MLCX1")
                leaf_mlcx2_positions = self.get_halcyon_leaf_positions(control_point, "MLCX2")
                jaw = self.get_halcyon_jaw_positions(beam, control_point)
                if leaf_mlcx1_positions is not None and leaf_mlcx2_positions is not None:
                    apertures.append(PyAperture(leaf_mlcx1_positions, leaf_widths, jaw, gantry_angle))
                    apertures.append(PyAperture(leaf_mlcx2_positions, leaf_widths, jaw, gantry_angle))
        else:
            leaf_widths = self.get_leaf_widths(beam)
            for control_point in beam["ControlPointSequence"]:
                gantry_angle = float(control_point.GantryAngle) if "GantryAngle" in control_point else beam["GantryAngle"]
                leaf_positions = self.get_leaf_positions(control_point)
                jaw = self.get_jaw_positions(beam, control_point)
                if leaf_positions is not None:
                    apertures.append(PyAperture(leaf_positions, leaf_widths, jaw, gantry_angle))

        beam["_cached_apertures"] = apertures
        return apertures

    def get_halcyon_jaw_positions(self, beam: dict, control_point: Dataset) -> List[float]:
        """Return Halcyon/Ethos jaw positions for the given control point."""
        left, right, top, bottom = -140.0, 140.0, -140.0, 140.0
        device_types = []
        if "BeamLimitingDevicePositionSequence" in control_point:
            for beam_limit in control_point.BeamLimitingDevicePositionSequence:
                device_types.append(beam_limit.RTBeamLimitingDeviceType)
                if beam_limit.RTBeamLimitingDeviceType == "X":
                    left = float(beam_limit.LeafJawPositions[0])
                    right = float(beam_limit.LeafJawPositions[1])
                if beam_limit.RTBeamLimitingDeviceType == "Y":
                    top = float(beam_limit.LeafJawPositions[0])
                    bottom = float(beam_limit.LeafJawPositions[1])

        if "X" not in device_types and "X" in beam:
            left = float(beam["X"][0])
            right = float(beam["X"][1])
        if "Y" not in device_types and "Y" in beam:
            top = float(beam["Y"][0])
            bottom = float(beam["Y"][1])

        return [left, -top, right, -bottom]

    def get_halcyon_leaf_widths(self, beam_dict: Dict) -> np.ndarray:
        beam_limits = beam_dict["BeamLimitingDeviceSequence"]
        for beam_limit in beam_limits:
            if beam_limit.RTBeamLimitingDeviceType == "MLCX1":
                return np.linspace(5, 5, 2 * beam_limit.NumberOfLeafJawPairs)
        return np.array([])

    def get_halcyon_leaf_positions(self, control_point: Dataset, mlc_type: str) -> np.ndarray | None:
        """Return Halcyon/Ethos leaf positions from the control point sequence."""
        if "BeamLimitingDevicePositionSequence" not in control_point:
            return None

        for position_item in control_point.BeamLimitingDevicePositionSequence:
            if position_item.RTBeamLimitingDeviceType == mlc_type:
                mlc_open = position_item.LeafJawPositions
                number_of_pairs = int(len(mlc_open) / 2)
                bank_a_positions = mlc_open[:number_of_pairs]
                bank_b_positions = mlc_open[number_of_pairs:]
                return np.vstack((bank_a_positions, bank_b_positions))
        return None

    def get_analyze_leaf_position(self, leaf_mlcx1_positions: np.ndarray, leaf_mlcx2_positions: np.ndarray) -> np.ndarray:
        """Combine dual-layer leaves into a synthesized 5 mm-resolution aperture."""
        leaf_mlcx1_positions = leaf_mlcx1_positions.repeat(2, axis=1)
        leaf_mlcx2_positions = leaf_mlcx2_positions.repeat(2, axis=1)
        leaf_mlcx2_positions = leaf_mlcx2_positions[:, 1:-1]
        leaf_positions = np.vstack(
            (
                np.maximum(leaf_mlcx1_positions[0, :], leaf_mlcx2_positions[0, :]),
                np.minimum(leaf_mlcx1_positions[1, :], leaf_mlcx2_positions[1, :]),
            )
        )
        leaf_positions[:, leaf_positions[1, :] - leaf_positions[0, :] < 0] = 0
        return leaf_positions

    def get_jaw_positions(self, beam: dict, control_point: Dataset) -> List[float]:
        """Return standard jaw positions for the given control point."""
        left, right, top, bottom = -200.0, 200.0, -200.0, 200.0
        device_types = []
        if "BeamLimitingDevicePositionSequence" in control_point:
            for beam_limit in control_point.BeamLimitingDevicePositionSequence:
                device_types.append(beam_limit.RTBeamLimitingDeviceType)
                if beam_limit.RTBeamLimitingDeviceType == "ASYMX":
                    left = float(beam_limit.LeafJawPositions[0])
                    right = float(beam_limit.LeafJawPositions[1])
                if beam_limit.RTBeamLimitingDeviceType == "ASYMY":
                    top = float(beam_limit.LeafJawPositions[0])
                    bottom = float(beam_limit.LeafJawPositions[1])

        if "ASYMX" not in device_types and "ASYMX" in beam:
            left = float(beam["ASYMX"][0])
            right = float(beam["ASYMX"][1])
        if "ASYMY" not in device_types and "ASYMY" in beam:
            top = float(beam["ASYMY"][0])
            bottom = float(beam["ASYMY"][1])

        return [left, -top, right, -bottom]

    def get_leaf_widths(self, beam_dict: Dict) -> np.ndarray:
        """Get leaf widths from BeamLimitingDeviceSequence boundaries."""
        beam_limits = beam_dict["BeamLimitingDeviceSequence"]
        for beam_limit in beam_limits:
            if beam_limit.RTBeamLimitingDeviceType in ["MLCX", "MLCX1", "MLCX2"]:
                return np.diff(beam_limit.LeafPositionBoundaries)
        return np.array([])

    def get_leaf_positions(self, control_point: Dataset) -> np.ndarray | None:
        """Return standard leaf positions for a control point."""
        if "BeamLimitingDevicePositionSequence" not in control_point:
            return None

        position_item = control_point.BeamLimitingDevicePositionSequence[-1]
        mlc_open = position_item.LeafJawPositions
        number_of_pairs = int(len(mlc_open) / 2)
        bank_a_positions = mlc_open[:number_of_pairs]
        bank_b_positions = mlc_open[number_of_pairs:]
        return np.vstack((bank_a_positions, bank_b_positions))


