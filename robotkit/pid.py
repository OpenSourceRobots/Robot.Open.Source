class PID:
    def __init__(self, kp, ki=0.0, kd=0.0, limit=None):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.limit = limit
        self.total = 0.0
        self.last_error = None

    def reset(self):
        self.total = 0.0
        self.last_error = None

    def update(self, error, dt):
        self.total += error * dt
        if self.last_error is None or dt <= 0:
            slope = 0.0
        else:
            slope = (error - self.last_error) / dt
        self.last_error = error
        output = self.kp * error + self.ki * self.total + self.kd * slope
        if self.limit is not None:
            output = max(-self.limit, min(self.limit, output))
        return output
