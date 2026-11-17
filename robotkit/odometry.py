import math

from .drive import Pose, wrap_angle


class Odometry:
    def __init__(self, wheel_base, pose=None):
        self.wheel_base = wheel_base
        self.pose = pose or Pose()

    def update(self, left_distance, right_distance):
        distance = (left_distance + right_distance) / 2
        turn = (right_distance - left_distance) / self.wheel_base
        middle = self.pose.heading + turn / 2
        self.pose = Pose(
            self.pose.x + distance * math.cos(middle),
            self.pose.y + distance * math.sin(middle),
            wrap_angle(self.pose.heading + turn),
        )
        return self.pose
