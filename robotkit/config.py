import json
from dataclasses import dataclass, fields

from .behaviors import AvoidObstacles
from .drive import DifferentialDrive
from .navigator import Navigator
from .safety import AccelerationLimiter, EmergencyStop
from .simulator import Simulator


@dataclass
class RobotConfig:
    wheel_base: float = 2.0
    max_wheel_speed: float = 2.0
    max_acceleration: float = 0.5
    max_angular_acceleration: float = 0.3
    stop_distance: float = 1.5
    safe_distance: float = 5.0
    sensor_range: float = 15.0

    @classmethod
    def load(cls, path):
        with open(path) as file:
            data = json.load(file)
        known = {field.name for field in fields(cls)}
        unknown = set(data) - known
        if unknown:
            raise ValueError("unknown settings: " + ", ".join(sorted(unknown)))
        return cls(**data)

    def make_drive(self):
        return DifferentialDrive(self.wheel_base, self.max_wheel_speed)

    def make_limiter(self):
        return AccelerationLimiter(self.max_acceleration, self.max_angular_acceleration)

    def make_simulator(self, obstacles=None, start=None):
        return Simulator(
            obstacles=obstacles,
            start=start,
            drive=self.make_drive(),
            limiter=self.make_limiter(),
            sensor_range=self.sensor_range,
        )

    def make_navigator(self, target):
        return Navigator(
            target,
            avoid=AvoidObstacles(self.safe_distance),
            estop=EmergencyStop(self.stop_distance),
        )


def load_config(path=None):
    if path:
        return RobotConfig.load(path)
    return RobotConfig()
