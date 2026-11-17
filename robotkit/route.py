import math


class Route:
    def __init__(self, points, tolerance=0.25):
        self.points = [tuple(point) for point in points]
        self.tolerance = tolerance
        self.index = 0

    @property
    def finished(self):
        return self.index >= len(self.points)

    def next_target(self, pose):
        while not self.finished and self._close_to(pose, self.points[self.index]):
            self.index += 1
        if self.finished:
            return None
        return self.points[self.index]

    def _close_to(self, pose, point):
        return math.hypot(point[0] - pose.x, point[1] - pose.y) < self.tolerance
