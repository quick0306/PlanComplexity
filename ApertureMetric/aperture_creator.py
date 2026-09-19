from typing import Dict, List

import numpy as np
from pydicom.dataset import Dataset

from ApertureMetric.aperture_geometry import PyAperture


STANDARD_MLC_DEVICE_TYPES = {"MLCX", "MLCY"}


def _stack_leaf_banks(leaf_jaw_positions) -> np.ndarray:
    number_of_pairs = int(len(leaf_jaw_positions) / 2)
    bank_a_positions = leaf_jaw_positions[:number_of_pairs]
    bank_b_positions = leaf_jaw_positions[number_of_pairs:]
    return np.vstack((bank_a_positions, bank_b_positions))


class AperturesFromBeamCreator:
    """Build per-control-point aperture geometry from a beam definition."""

    def create(self, beam: Dict[str, str]) -> List[PyAperture]:
        cached_apertures = beam.get("_cached_apertures")
        if cached_apertures is not None:
            return cached_apertures

        apertures: List[PyAperture] = []
        machine_name = beam["TreatmentMachineName"].lower()
        jaw = None

        if "halcyon" in machine_name or "ethos" in machine_name:
            distal_boundaries = self.get_leaf_boundaries(beam, "MLCX1")
            proximal_boundaries = self.get_leaf_boundaries(beam, "MLCX2")
            last_mlcx1_positions = None
            last_mlcx2_positions = None
            for control_point in beam["ControlPointSequence"]:
                gantry_angle = float(control_point.GantryAngle) if "GantryAngle" in control_point else beam["GantryAngle"]
                leaf_mlcx1_positions = self.get_halcyon_leaf_positions(control_point, "MLCX1")
                leaf_mlcx2_positions = self.get_halcyon_leaf_positions(control_point, "MLCX2")
                if leaf_mlcx1_positions is None and last_mlcx1_positions is not None:
                    leaf_mlcx1_positions = last_mlcx1_positions.copy()
                if leaf_mlcx2_positions is None and last_mlcx2_positions is not None:
                    leaf_mlcx2_positions = last_mlcx2_positions.copy()
                jaw = self.get_halcyon_jaw_positions(beam, control_point, previous_jaw=jaw)
                if leaf_mlcx1_positions is not None and leaf_mlcx2_positions is not None:
                    # DICOM control points inherit unchanged machine parameters; some
                    # TPS exports write final meterset control points without repeating
                    # the unchanged MLC positions.
                    last_mlcx1_positions = leaf_mlcx1_positions.copy()
                    last_mlcx2_positions = leaf_mlcx2_positions.copy()
                    apertures.append(PyAperture(leaf_mlcx1_positions, np.diff(distal_boundaries), jaw, gantry_angle,
                                                leaf_position_boundaries=distal_boundaries))
                    apertures.append(PyAperture(leaf_mlcx2_positions, np.diff(proximal_boundaries), jaw, gantry_angle,
                                                leaf_position_boundaries=proximal_boundaries))
        else:
            boundaries = self.get_leaf_boundaries(beam, "MLCX")
            leaf_widths = np.diff(boundaries)
            last_leaf_positions = None
            for control_point in beam["ControlPointSequence"]:
                gantry_angle = float(control_point.GantryAngle) if "GantryAngle" in control_point else beam["GantryAngle"]
                leaf_positions = self.get_leaf_positions(control_point)
                if leaf_positions is None and last_leaf_positions is not None:
                    # DICOM omits unchanged values after the first control point; keep
                    # aperture count aligned with cumulative meterset weights.
                    leaf_positions = last_leaf_positions.copy()
                jaw = self.get_jaw_positions(beam, control_point, previous_jaw=jaw)
                if leaf_positions is not None:
                    last_leaf_positions = leaf_positions.copy()
                    apertures.append(PyAperture(leaf_positions, leaf_widths, jaw, gantry_angle,
                                                leaf_position_boundaries=boundaries))

        beam["_cached_apertures"] = apertures
        return apertures

    def get_halcyon_jaw_positions(self, beam: dict, control_point: Dataset, *, previous_jaw=None) -> List[float]:
        """Return Halcyon/Ethos jaw positions for the given control point."""
        return self._jaw_positions(beam, control_point, half_field=140.0, previous_jaw=previous_jaw)

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
                return _stack_leaf_banks(position_item.LeafJawPositions)
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

    def get_jaw_positions(self, beam: dict, control_point: Dataset, *, previous_jaw=None) -> List[float]:
        """Return standard jaw positions for the given control point."""
        return self._jaw_positions(beam, control_point, half_field=200.0, previous_jaw=previous_jaw)

    @staticmethod
    def _jaw_positions(beam, control_point, *, half_field, previous_jaw=None):
        positions = {str(item.RTBeamLimitingDeviceType).upper(): item.LeafJawPositions
                     for item in getattr(control_point, "BeamLimitingDevicePositionSequence", [])}
        result = []
        for axis, aliases in enumerate((("X", "ASYMX"), ("Y", "ASYMY"))):
            values = next((positions[key] for key in aliases if key in positions), None)
            if values is None and previous_jaw is not None:
                # Tolerate exports that omit repeated axes after later control
                # points too. Convert the cached internal Y back to IEC.
                values = ([previous_jaw[0], previous_jaw[2]] if axis == 0
                          else [-previous_jaw[1], -previous_jaw[3]])
            if values is None:
                values = next((beam[key] for key in aliases if key in beam), [-half_field, half_field])
            values = np.asarray(values, dtype=float)
            if values.shape != (2,) or not np.all(np.isfinite(values)) or values[0] > values[1]:
                raise ValueError("Jaw positions must be a finite ordered pair.")
            result.append(values)
        (left, right), (y1, y2) = result
        return [left, -y1, right, -y2]

    @staticmethod
    def get_leaf_boundaries(beam_dict, device_type):
        for device in beam_dict.get("BeamLimitingDeviceSequence", []):
            if str(device.RTBeamLimitingDeviceType).upper() == device_type:
                boundaries = np.asarray(getattr(device, "LeafPositionBoundaries", []), dtype=float)
                count = int(getattr(device, "NumberOfLeafJawPairs", len(boundaries) - 1))
                if (count <= 0 or boundaries.shape != (count + 1,)
                        or not np.all(np.isfinite(boundaries)) or np.any(np.diff(boundaries) <= 0)):
                    raise ValueError(f"Invalid {device_type} leaf boundaries or leaf count.")
                return boundaries
        raise ValueError(f"Missing {device_type} leaf boundaries.")

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

        # DICOM item order is not semantic; select the MLC positions by device type.
        for position_item in control_point.BeamLimitingDevicePositionSequence:
            if str(position_item.RTBeamLimitingDeviceType).upper() not in STANDARD_MLC_DEVICE_TYPES:
                continue
            return _stack_leaf_banks(position_item.LeafJawPositions)
        return None


