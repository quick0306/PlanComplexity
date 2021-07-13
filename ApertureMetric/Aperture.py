from typing import List
import numpy as np

from ApertureMetric.LeafPair import LeafPair, PyLeafPair
from ApertureMetric.Jaw import Jaw


class Aperture:
    """
        The first dimension of leafPositions corresponds to the bank, and the second dimension
        corresponds to the leaf pair.
        Leaf coordinates follow the IEC 61217 standard:

                          Positive Y         x = isocenter (0, 0)
                              -
                              |
                              |
                              |
        Negative X |----------x----------| Positive X
                              |
                              |
                              |
                              -
                          Negative Y

        leafPositions and leafWidths must not be null, and they must have the same number of leaves

        jaw is the Position of the jaw (cannot be null),given as:
        left, top, right, bottom; for a completely open jaw, use:
        new double[] { double.MinValue, double.MinValue, double.MaxValue, double.MaxValue };
    """

    def __init__(self, leaf_positions, leaf_widths, jaw):
        """
        :param leaf_positions: Numpy 2D array of floats
        :param leaf_widths: Numpy array 1D
        :param jaw: list with jaw positions
        """
        self.jaw = self.CreateJaw(jaw)
        self.leaf_pairs = self.CreateLeafPairs(leaf_positions, leaf_widths, self.jaw)

    def CreateLeafPairs(self, positions, widths, jaw):
        """Aperture Leaf Pairs"""
        leaf_tops = self.GetLeafTops(widths)

        pairs = []
        for i in range(len(widths)):
            lp = LeafPair(positions[0, i], positions[1, i], widths[i], leaf_tops[i], jaw)
            pairs.append(lp)
        return pairs

    @staticmethod
    def GetLeafTops(widths):
        """Using the leaf widths, creates an array of the location of all the leaf tops (relative to the isocenter)"""
        leaf_tops = [0.0] * len(widths)

        # Leaf index right below isocenter
        middle_index = int(len(widths) / 2)

        # Do bottom half
        for i in range(middle_index + 1, len(widths)):
            leaf_tops[i] = leaf_tops[i - 1] - widths[i - 1]

        # Do top half
        i = middle_index - 1
        while i >= 0:
            leaf_tops[i] = leaf_tops[i + 1] + widths[i]
            i -= 1

        return leaf_tops

    @staticmethod
    def CreateJaw(pos):
        """Creates Jaw object using x and y positions"""
        return Jaw(pos[0], pos[1], pos[2], pos[3])

    @property
    def Jaw(self):
        return self.jaw

    @Jaw.setter
    def Jaw(self, value):
        self.jaw = value

    @property
    def LeafPairs(self):
        return self.leaf_pairs

    @LeafPairs.setter
    def LeafPairs(self, value):
        self.leaf_pairs = value

    def HasOpenLeafBehindJaws(self):
        truth = [lp.IsOpenBehindJaw() for lp in self.LeafPairs]
        return any(truth)

    def ApertureSubRegions(self):
        """aperture sud regions，MLC interplay"""
        no_regs = 0
        new_reg = True
        for i, lp in zip(range(len(self.LeafPairs)), self.LeafPairs):
            if lp.FieldSize() > 0.5:
                if new_reg:
                    no_regs += 1
                    new_reg = False
                else:
                    if lp.Left >= self.LeafPairs[i-1].Right or lp.Right <= self.LeafPairs[i - 1].Left:
                        no_regs += 1
            else:
                if not new_reg:
                    new_reg = True

        return no_regs

    def Area(self):
        return sum([lp.FieldArea() for lp in self.LeafPairs])

    def LeafPairsAreOutsideJaw(self, top, bottom):
        return top.IsOutsideJaw() and bottom.IsOutsideJaw()

    def JawTopIsBelowTopLeafPair(self, top):
        return self.Jaw.Top <= top.Bottom

    def JawBottomIsAboveBottomLeafPair(self, bottom):
        return self.Jaw.Bottom >= bottom.Top

    def LeafPairsAreDisjoint(self, top, bottom):
        return (bottom.Left > top.Right) or (bottom.Right < top.Left)

    def SidePerimeter(self, top, bottom):

        if self.LeafPairsAreOutsideJaw(top, bottom):
            return 0.0

        if self.JawTopIsBelowTopLeafPair(top):
            return bottom.FieldSize()

        if self.JawBottomIsAboveBottomLeafPair(bottom):
            return top.FieldSize()

        if self.LeafPairsAreDisjoint(top, bottom):
            return top.FieldSize() + bottom.FieldSize()

        topEdgeLeft = max(self.Jaw.Left, top.Left)
        bottomEdgeLeft = max(self.Jaw.Left, bottom.Left)
        topEdgeRight = min(self.Jaw.Right, top.Right)
        bottomEdgeRight = min(self.Jaw.Right, bottom.Right)

        return abs(topEdgeLeft - bottomEdgeLeft) + abs(topEdgeRight - bottomEdgeRight)

    def SidePerimeterHorizontal(self):
        """Calculate horizontal leaf perimeter"""
        # Top end of first leaf pair
        perimeter = self.LeafPairs[0].FieldSize()

        for i in range(1, len(self.LeafPairs)):
            perimeter += self.SidePerimeter(self.LeafPairs[i - 1], self.LeafPairs[i])

        # Bottom end of last leaf pair
        perimeter += self.LeafPairs[-1].FieldSize()

        return perimeter

    def SidePerimeterVertical(self):
        """Calculate vertical leaf perimeter"""
        perimeter = 0.0
        for lp in self.LeafPairs:
            if not lp.IsOutsideJaw():
                perimeter += lp.OpenLeafWidth()

        return perimeter

    def OpenLeafParisNumber(self):
        number = 0
        for lp in self.LeafPairs:
            if not lp.IsOutsideJaw():
                number += 1

        return number


class PyAperture(Aperture):

    def __init__(self, leaf_positions: np.ndarray, leaf_widths: np.ndarray, jaw: List[float],
                 gantry_angle: float) -> None:
        super().__init__(leaf_positions, leaf_widths, jaw)
        self.gantry_angle = gantry_angle

    def CreateLeafPairs(self, positions: np.ndarray, widths: np.ndarray, jaw: Jaw) -> List[PyLeafPair]:
        leaf_tops = self.GetLeafTops(widths)

        pairs = []
        for i in range(len(widths)):
            lp = PyLeafPair(positions[0, i], positions[1, i], widths[i], leaf_tops[i], jaw)
            pairs.append(lp)
        return pairs

    @property
    def LeafPairArea(self) -> List[float]:
        return [lp.FieldArea() for lp in self.LeafPairs]

    @property
    def GantryAngle(self) -> float:
        return self.gantry_angle

    @GantryAngle.setter
    def GantryAngle(self, value: float):
        self.gantry_angle = value

    def __repr__(self):
        txt = "Aperture - Gantry: %1.1f" % self.GantryAngle
        return txt

