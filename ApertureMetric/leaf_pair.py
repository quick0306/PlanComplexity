from ApertureMetric.rect_geometry import Rect
from ApertureMetric.jaw_geometry import Jaw


class LeafPair:
    def __init__(self, left, right, width, top, jaw):
        """Left and right represent the bank A and B, respectively"""
        self.position = Rect(left, top, right, top - width)
        self.width = width
        self.jaw = jaw

    @property
    def left(self):
        return self.position.left

    @property
    def top(self):
        return self.position.top

    @property
    def right(self):
        return self.position.right

    @property
    def bottom(self):
        return self.position.bottom

    def is_outside_jaw(self):
        """The reason for <= or >= instead of just < or > is that if the jaw edge is equal to the leaf edge,
        it's as if the jaw edge was the leaf edge, so it's safer to count the leaf as outside, so that the edges
        are not counted twice (leaf and jaw edge)"""
        return (
                (self.jaw.top <= self.bottom)
                or (self.jaw.bottom >= self.top)
                or (self.jaw.left >= self.right)
                or (self.jaw.right <= self.left)
        )

    def field_size(self):
        if self.is_outside_jaw():
            return 0.0

        left = max(self.jaw.left, self.left)
        right = min(self.jaw.right, self.right)
        return max(right - left, 0.0)

    def open_leaf_width(self):
        """Returns the amount of leaf width that is open, considering the Position of the jaw"""
        if self.is_outside_jaw():
            return 0.0

        top = min(self.jaw.top, self.top)
        bottom = max(self.jaw.bottom, self.bottom)

        return top - bottom

    def field_area(self):
        return self.field_size() * self.open_leaf_width()

    def is_open(self):
        return self.field_size() > 0.0

    def is_open_behind_jaw(self):
        """Used to warn the user that there is a leaf behind the jaws, even though it is open and within
         the top and bottom jaw edges"""
        return self.is_outside_jaw() and (self.jaw.left > self.left or self.jaw.right < self.right)


class PyLeafPair(LeafPair):

    def __init__(self, left: float, right: float, width: float, top: float, jaw: Jaw) -> None:
        super().__init__(left, right, width, top, jaw)

    def __repr__(self):
        txt = "Leaf Pair: left: %1.1f top: %1.1f right: %1.1f botton: %1.1f" \
              % (self.left, self.top, self.right, self.bottom)

        return txt




