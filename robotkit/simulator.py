import math

from .drive import DifferentialDrive, Pose
from .safety import AccelerationLimiter
from .sensors import RangeSensor


class Simulator:
    def __init__(self, obstacles=None, start=None, drive=None, limiter=None, sensor_range=15.0):
        self.obstacles = list(obstacles or [])
        self.pose = start or Pose()
        self.drive = drive or DifferentialDrive()
        self.limiter = limiter or AccelerationLimiter()
        self.sensors = {
            "left": RangeSensor(math.radians(40), sensor_range),
            "front": RangeSensor(0.0, sensor_range),
            "right": RangeSensor(math.radians(-40), sensor_range),
        }
        self.time = 0.0

    def read_sensors(self):
        return {
            name: sensor.read(self.pose, self.obstacles)
            for name, sensor in self.sensors.items()
        }

    def step(self, linear, angular, dt=0.05):
        linear, angular = self.limiter.apply(linear, angular, dt)
        left, right = self.drive.wheel_speeds(linear, angular)
        self.pose = self.drive.move(self.pose, left, right, dt)
        self.time += dt
        return self.pose

    def halt(self):
        self.limiter.halt()
