from typing import List

import numpy as np

from ApertureMetric.jaw_geometry import Jaw
from ApertureMetric.leaf_pair import LeafPair, PyLeafPair


class Aperture:
    """Geometric aperture model built from paired MLC leaf positions."""

    def __init__(self, leaf_positions, leaf_widths, jaw, *, leaf_position_boundaries=None):
        leaf_positions = np.asarray(leaf_positions, dtype=float)
        leaf_widths = np.asarray(leaf_widths, dtype=float)
        if leaf_widths.ndim != 1 or leaf_positions.shape != (2, len(leaf_widths)):
            raise ValueError("MLC position shape must be (2, number of leaf widths).")
        if not np.all(np.isfinite(leaf_positions)) or not np.all(np.isfinite(leaf_widths)) or np.any(leaf_widths <= 0):
            raise ValueError("MLC positions and positive leaf widths must be finite.")
        self.leaf_position_boundaries = None
        if leaf_position_boundaries is not None:
            boundaries = np.asarray(leaf_position_boundaries, dtype=float)
            if (boundaries.shape != (len(leaf_widths) + 1,)
                    or not np.all(np.isfinite(boundaries))
                    or np.any(np.diff(boundaries) <= 0)
                    or not np.allclose(np.diff(boundaries), leaf_widths, rtol=0., atol=1e-8)):
                raise ValueError("MLC boundaries must be finite, increasing, and match each leaf width.")
            self.leaf_position_boundaries = boundaries.copy()
        self.jaw = self.create_jaw(jaw)
        self.leaf_pairs = self.create_leaf_pairs(leaf_positions, leaf_widths, self.jaw)

    def create_leaf_pairs(self, positions, widths, jaw):
        leaf_tops = self._positioned_leaf_tops(widths)

        pairs = []
        for index in range(len(widths)):
            leaf_pair = LeafPair(positions[0, index], positions[1, index], widths[index], leaf_tops[index], jaw)
            pairs.append(leaf_pair)
        return pairs

    def _positioned_leaf_tops(self, widths):
        if self.leaf_position_boundaries is not None:
            # Internal Y is reflected from IEC Y, without changing the DICOM slot order.
            return -self.leaf_position_boundaries[:-1]
        # Keep widths-only synthetic and legacy callers compatible. DICOM callers
        # must supply absolute boundaries, especially for odd or offset leaf arrays.
        return self.get_leaf_tops(widths)

    @staticmethod
    def get_leaf_tops(widths):
        leaf_tops = [0.0] * len(widths)
        middle_index = int(len(widths) / 2)

        for index in range(middle_index + 1, len(widths)):
            leaf_tops[index] = leaf_tops[index - 1] - widths[index - 1]

        index = middle_index - 1
        while index >= 0:
            leaf_tops[index] = leaf_tops[index + 1] + widths[index]
            index -= 1

        return leaf_tops

    @staticmethod
    def create_jaw(pos):
        return Jaw(pos[0], pos[1], pos[2], pos[3])

    def has_open_leaf_behind_jaws(self):
        return any(leaf_pair.is_open_behind_jaw() for leaf_pair in self.leaf_pairs)

    def aperture_sub_regions(self):
        number_of_regions = 0
        new_region = True
        for index, leaf_pair in zip(range(len(self.leaf_pairs)), self.leaf_pairs):
            if leaf_pair.field_size() > 0.5:
                if new_region:
                    number_of_regions += 1
                    new_region = False
                elif leaf_pair.left >= self.leaf_pairs[index - 1].right or leaf_pair.right <= self.leaf_pairs[index - 1].left:
                    number_of_regions += 1
            elif not new_region:
                new_region = True

        return number_of_regions

    def area(self):
        return sum(leaf_pair.field_area() for leaf_pair in self.leaf_pairs)

    def leaf_pairs_are_outside_jaw(self, top, bottom):
        return top.is_outside_jaw() and bottom.is_outside_jaw()

    def jaw_top_is_below_top_leaf_pair(self, top):
        return self.jaw.top <= top.bottom

    def jaw_bottom_is_above_bottom_leaf_pair(self, bottom):
        return self.jaw.bottom >= bottom.top

    def leaf_pairs_are_disjoint(self, top, bottom):
        return (bottom.left > top.right) or (bottom.right < top.left)

    def side_perimeter(self, top, bottom):
        top_size, bottom_size = top.field_size(), bottom.field_size()
        if top_size <= 0.0 or bottom_size <= 0.0:
            return top_size + bottom_size
        overlap = max(0.0, min(self.jaw.right, top.right, bottom.right)
                      - max(self.jaw.left, top.left, bottom.left))
        return top_size + bottom_size - 2.0 * overlap

    def side_perimeter_horizontal(self):
        if not self.leaf_pairs:
            return 0.0
        perimeter = self.leaf_pairs[0].field_size()
        for index in range(1, len(self.leaf_pairs)):
            perimeter += self.side_perimeter(self.leaf_pairs[index - 1], self.leaf_pairs[index])
        perimeter += self.leaf_pairs[-1].field_size()
        return perimeter

    def side_perimeter_vertical(self):
        """One bank's exposed length, retained for the existing edge-area formula."""
        perimeter = 0.0
        for leaf_pair in self.leaf_pairs:
            if not leaf_pair.is_outside_jaw():
                perimeter += leaf_pair.open_leaf_width()
        return perimeter

    def perimeter(self):
        """Full boundary length of the transmitted aperture, in millimetres."""
        if self.jaw.top <= self.jaw.bottom or self.jaw.right <= self.jaw.left:
            return 0.0
        vertical = 2.0 * sum(pair.open_leaf_width() for pair in self.leaf_pairs if pair.is_open())
        return self.side_perimeter_horizontal() + vertical

    def open_leaf_pairs_number(self):
        number = 0
        for leaf_pair in self.leaf_pairs:
            if not leaf_pair.is_outside_jaw():
                number += 1
        return number


class PyAperture(Aperture):
    def __init__(self, leaf_positions: np.ndarray, leaf_widths: np.ndarray, jaw: List[float], gantry_angle: float, *, leaf_position_boundaries=None) -> None:
        super().__init__(leaf_positions, leaf_widths, jaw, leaf_position_boundaries=leaf_position_boundaries)
        self.gantry_angle = gantry_angle

    def create_leaf_pairs(self, positions: np.ndarray, widths: np.ndarray, jaw: Jaw) -> List[PyLeafPair]:
        leaf_tops = self._positioned_leaf_tops(widths)

        pairs = []
        for index in range(len(widths)):
            leaf_pair = PyLeafPair(positions[0, index], positions[1, index], widths[index], leaf_tops[index], jaw)
            pairs.append(leaf_pair)
        return pairs

    @property
    def leaf_pair_areas(self) -> List[float]:
        return [leaf_pair.field_area() for leaf_pair in self.leaf_pairs]

    def __repr__(self):
        return "Aperture - Gantry: %1.1f" % self.gantry_angle

