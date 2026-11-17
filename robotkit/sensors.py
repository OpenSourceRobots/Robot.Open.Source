import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Obstacle:
    x: float
    y: float
    radius: float


class RangeSensor:
    def __init__(self, angle=0.0, max_range=15.0):
        self.angle = angle
        self.max_range = max_range

    def read(self, pose, obstacles):
        direction = pose.heading + self.angle
        dx = math.cos(direction)
        dy = math.sin(direction)
        closest = self.max_range
        for obstacle in obstacles:
            hit = self._ray_hit(pose, dx, dy, obstacle)
            if hit is not None and hit < closest:
                closest = hit
        return closest

    def _ray_hit(self, pose, dx, dy, obstacle):
        ox = obstacle.x - pose.x
        oy = obstacle.y - pose.y
        along = ox * dx + oy * dy
        if along < 0:
            return None
        off_squared = ox * ox + oy * oy - along * along
        radius_squared = obstacle.radius ** 2
        if off_squared > radius_squared:
            return None
        distance = along - math.sqrt(radius_squared - off_squared)
        if distance < 0:
            return None
        return distance
