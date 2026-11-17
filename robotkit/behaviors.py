import math

from .drive import wrap_angle
from .pid import PID


class GoToPoint:
    def __init__(self, target, max_speed=1.5, tolerance=0.25):
        self.target = target
        self.max_speed = max_speed
        self.tolerance = tolerance
        self.turn_pid = PID(kp=1.0, ki=0.0, kd=0.2, limit=0.5)

    def arrived(self, pose):
        return self._distance(pose) < self.tolerance

    def command(self, pose, dt):
        if self.arrived(pose):
            return 0.0, 0.0
        tx, ty = self.target
        wanted = math.atan2(ty - pose.y, tx - pose.x)
        error = wrap_angle(wanted - pose.heading)
        angular = self.turn_pid.update(error, dt)
        speed = min(self.max_speed, self._distance(pose) * 0.5)
        linear = speed * max(0.0, math.cos(error))
        return linear, angular

    def _distance(self, pose):
        tx, ty = self.target
        return math.hypot(tx - pose.x, ty - pose.y)


class AvoidObstacles:
    def __init__(self, safe_distance=5.0, turn_speed=0.4, crawl_speed=0.3):
        self.safe_distance = safe_distance
        self.turn_speed = turn_speed
        self.crawl_speed = crawl_speed

    def command(self, left_range, front_range, right_range):
        side_limit = self.safe_distance * 0.6
        if front_range > self.safe_distance and min(left_range, right_range) > side_limit:
            return None
        if left_range > right_range:
            return self.crawl_speed, self.turn_speed
        return self.crawl_speed, -self.turn_speed
