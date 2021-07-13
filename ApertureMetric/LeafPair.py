from ApertureMetric.Rect import Rect
from ApertureMetric.Jaw import Jaw


class LeafPair:
    def __init__(self, left, right, width, top, jaw):
        """Left and right represent the bank A and B, respectively"""
        self.position = Rect(left, top, right, top - width)
        self.width = width
        self.jaw = jaw

    @property
    def Position(self):
        return self.position

    @Position.setter
    def Position(self, value):
        self.position = value

    @property
    def Left(self):
        return self.position.Left

    @property
    def Top(self):
        return self.position.Top

    @property
    def Right(self):
        return self.position.Right

    @property
    def Bottom(self):
        return self.position.Bottom

    @property
    def Width(self):
        return self.width

    @Width.setter
    def Width(self, value):
        self.width = value

    @property
    def Jaw(self):
        """Each leaf pair contains a reference to the jaw"""
        return self.jaw

    @Jaw.setter
    def Jaw(self, value):
        self.jaw = value

    def IsOutsideJaw(self):
        """The reason for <= or >= instead of just < or > is that if the jaw edge is equal to the leaf edge,
        it's as if the jaw edge was the leaf edge, so it's safer to count the leaf as outside, so that the edges
        are not counted twice (leaf and jaw edge)"""
        return (
                (self.Jaw.Top <= self.Bottom)
                or (self.Jaw.Bottom >= self.Top)
                or (self.Jaw.Left >= self.Right)
                or (self.Jaw.Right <= self.Left)
        )

    def FieldSize(self):
        if self.IsOutsideJaw():
            return 0.0

        left = max(self.Jaw.Left, self.Left)
        right = min(self.Jaw.Right, self.Right)
        return right - left

    def OpenLeafWidth(self):
        """Returns the amount of leaf width that is open, considering the Position of the jaw"""
        if self.IsOutsideJaw():
            return 0.0

        top = min(self.Jaw.Top, self.Top)
        bottom = max(self.Jaw.Bottom, self.Bottom)

        return top - bottom

    def FieldArea(self):
        return self.FieldSize() * self.OpenLeafWidth()

    def IsOpen(self):
        return self.FieldSize() > 0.0

    def IsOpenBehindJaw(self):
        """Used to warn the user that there is a leaf behind the jaws, even though it is open and within
         the top and bottom jaw edges"""
        return (self.IsOutsideJaw()) and (self.Jaw.Left > self.Left or self.Jaw.Right < self.Right)


class PyLeafPair(LeafPair):

    def __init__(self, left: float, right: float, width: float, top: float, jaw: Jaw) -> None:
        super().__init__(left, right, width, top, jaw)

    def __repr__(self):
        txt = "Leaf Pair: left: %1.1f top: %1.1f right: %1.1f botton: %1.1f" \
              % (self.Left, self.Top, self.Right, self.Bottom)

        return txt
