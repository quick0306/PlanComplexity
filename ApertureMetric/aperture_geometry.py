from typing import List

import numpy as np

from ApertureMetric.jaw_geometry import Jaw
from ApertureMetric.leaf_pair import LeafPair, PyLeafPair


class Aperture:
    """Geometric aperture model built from paired MLC leaf positions."""

    def __init__(self, leaf_positions, leaf_widths, jaw):
        self.jaw = self.create_jaw(jaw)
        self.leaf_pairs = self.create_leaf_pairs(leaf_positions, leaf_widths, self.jaw)

    def create_leaf_pairs(self, positions, widths, jaw):
        leaf_tops = self.get_leaf_tops(widths)

        pairs = []
        for index in range(len(widths)):
            leaf_pair = LeafPair(positions[0, index], positions[1, index], widths[index], leaf_tops[index], jaw)
            pairs.append(leaf_pair)
        return pairs

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
        if self.leaf_pairs_are_outside_jaw(top, bottom):
            return 0.0

        if self.jaw_top_is_below_top_leaf_pair(top):
            return bottom.field_size()

        if self.jaw_bottom_is_above_bottom_leaf_pair(bottom):
            return top.field_size()

        if self.leaf_pairs_are_disjoint(top, bottom):
            return top.field_size() + bottom.field_size()

        top_edge_left = max(self.jaw.left, top.left)
        bottom_edge_left = max(self.jaw.left, bottom.left)
        top_edge_right = min(self.jaw.right, top.right)
        bottom_edge_right = min(self.jaw.right, bottom.right)

        return abs(top_edge_left - bottom_edge_left) + abs(top_edge_right - bottom_edge_right)

    def side_perimeter_horizontal(self):
        perimeter = self.leaf_pairs[0].field_size()
        for index in range(1, len(self.leaf_pairs)):
            perimeter += self.side_perimeter(self.leaf_pairs[index - 1], self.leaf_pairs[index])
        perimeter += self.leaf_pairs[-1].field_size()
        return perimeter

    def side_perimeter_vertical(self):
        perimeter = 0.0
        for leaf_pair in self.leaf_pairs:
            if not leaf_pair.is_outside_jaw():
                perimeter += leaf_pair.open_leaf_width()
        return perimeter

    def open_leaf_pairs_number(self):
        number = 0
        for leaf_pair in self.leaf_pairs:
            if not leaf_pair.is_outside_jaw():
                number += 1
        return number


class PyAperture(Aperture):
    def __init__(self, leaf_positions: np.ndarray, leaf_widths: np.ndarray, jaw: List[float], gantry_angle: float) -> None:
        super().__init__(leaf_positions, leaf_widths, jaw)
        self.gantry_angle = gantry_angle

    def create_leaf_pairs(self, positions: np.ndarray, widths: np.ndarray, jaw: Jaw) -> List[PyLeafPair]:
        leaf_tops = self.get_leaf_tops(widths)

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

