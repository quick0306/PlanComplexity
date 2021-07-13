from ApertureMetric.Rect import Rect


class Jaw:
    def __init__(self, left: float, top: float, right: float, bottom: float) -> None:
        self.jaw_position = Rect(left, top, right, bottom)

    @property
    def Position(self):
        return self.jaw_position

    @Position.setter
    def Position(self, value):
        self.jaw_position = value

    @property
    def Left(self):
        return self.jaw_position.Left

    @property
    def Top(self):
        return self.jaw_position.Top

    @property
    def Right(self):
        return self.jaw_position.Right

    @property
    def Bottom(self):
        return self.jaw_position.Bottom