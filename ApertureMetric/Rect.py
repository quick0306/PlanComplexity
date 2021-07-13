class Rect:
    def __init__(self, left: float, top: float, right: float, bottom: float) -> None:
        """Rectangular dimension (used for leaf and jaw positions) it is relative to the top of the first
        leaf and the iso-center"""
        self.Left = left
        self.Top = top
        self.Right = right
        self.Bottom = bottom

    def __repr__(self):
        return "Position: left: %1.1f top: %1.1f right: %1.1f bottom: %1.1f" \
               % (self.Left, self.Top, self.Right, self.Bottom)
