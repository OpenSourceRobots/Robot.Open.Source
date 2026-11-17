from .behaviors import AvoidObstacles, GoToPoint
from .safety import EmergencyStop


class Navigator:
    def __init__(self, target, avoid=None, estop=None):
        self.goal = GoToPoint(target)
        self.avoid = avoid or AvoidObstacles()
        self.estop = estop or EmergencyStop()

    def set_target(self, target):
        self.goal = GoToPoint(target, self.goal.max_speed, self.goal.tolerance)

    def update(self, pose, ranges, dt):
        if self.estop.check(ranges):
            return 0.0, 0.0, "emergency stop"
        if self.goal.arrived(pose):
            return 0.0, 0.0, "arrived"
        avoidance = self.avoid.command(ranges["left"], ranges["front"], ranges["right"])
        if avoidance is not None:
            return avoidance[0], avoidance[1], "avoiding"
        linear, angular = self.goal.command(pose, dt)
        return linear, angular, "driving"
