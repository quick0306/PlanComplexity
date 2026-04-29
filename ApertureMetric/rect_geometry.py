class Rect:
    """Axis-aligned rectangle helper used by jaw and leaf geometry."""

    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom
