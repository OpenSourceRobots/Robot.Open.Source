class AccelerationLimiter:
    def __init__(self, max_linear=0.5, max_angular=0.3):
        self.max_linear = max_linear
        self.max_angular = max_angular
        self.linear = 0.0
        self.angular = 0.0

    def apply(self, linear, angular, dt):
        self.linear = self._approach(self.linear, linear, self.max_linear * dt)
        self.angular = self._approach(self.angular, angular, self.max_angular * dt)
        return self.linear, self.angular

    def halt(self):
        self.linear = 0.0
        self.angular = 0.0

    @staticmethod
    def _approach(current, target, step):
        if target > current:
            return min(target, current + step)
        return max(target, current - step)


class EmergencyStop:
    def __init__(self, stop_distance=1.5):
        self.stop_distance = stop_distance
        self.engaged = False

    def check(self, readings):
        if min(readings.values()) < self.stop_distance:
            self.engaged = True
        return self.engaged

    def release(self):
        self.engaged = False
