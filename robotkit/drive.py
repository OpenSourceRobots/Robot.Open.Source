import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Pose:
    x: float = 0.0
    y: float = 0.0
    heading: float = 0.0


def wrap_angle(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


class DifferentialDrive:
    def __init__(self, wheel_base=2.0, max_wheel_speed=2.0):
        self.wheel_base = wheel_base
        self.max_wheel_speed = max_wheel_speed

    def wheel_speeds(self, linear, angular):
        half = self.wheel_base / 2
        left = linear - angular * half
        right = linear + angular * half
        fastest = max(abs(left), abs(right))
        if fastest > self.max_wheel_speed:
            scale = self.max_wheel_speed / fastest
            left *= scale
            right *= scale
        return left, right

    def move(self, pose, left, right, dt):
        linear = (left + right) / 2
        angular = (right - left) / self.wheel_base
        heading = wrap_angle(pose.heading + angular * dt)
        x = pose.x + linear * math.cos(heading) * dt
        y = pose.y + linear * math.sin(heading) * dt
        return Pose(x, y, heading)
