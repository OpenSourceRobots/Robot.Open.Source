import json
import math

import pytest

from robotkit import (
    AccelerationLimiter,
    DifferentialDrive,
    EmergencyStop,
    GoToPoint,
    Navigator,
    Obstacle,
    PID,
    Pose,
    RangeSensor,
    RobotConfig,
    SerialDriver,
)
from robotkit.cli import build_parser


class FakeLink:
    def __init__(self):
        self.sent = []
        self.closed = False

    def write(self, data):
        self.sent.append(data)

    def close(self):
        self.closed = True


def test_pid_proportional_only():
    pid = PID(kp=2.0)
    assert pid.update(1.5, 0.1) == 3.0


def test_pid_respects_limit():
    pid = PID(kp=10.0, limit=1.0)
    assert pid.update(5.0, 0.1) == 1.0


def test_drive_goes_straight():
    drive = DifferentialDrive()
    pose = drive.move(Pose(), 1.0, 1.0, 1.0)
    assert math.isclose(pose.x, 1.0)
    assert math.isclose(pose.y, 0.0, abs_tol=1e-9)


def test_wheel_speeds_are_capped():
    drive = DifferentialDrive(max_wheel_speed=2.0)
    left, right = drive.wheel_speeds(10.0, 0.0)
    assert max(left, right) <= 2.0


def test_sensor_sees_obstacle():
    sensor = RangeSensor(max_range=20.0)
    reading = sensor.read(Pose(), [Obstacle(10.0, 0.0, 2.0)])
    assert math.isclose(reading, 8.0)


def test_sensor_misses_obstacle_behind():
    sensor = RangeSensor(max_range=20.0)
    reading = sensor.read(Pose(), [Obstacle(-10.0, 0.0, 2.0)])
    assert reading == 20.0


def test_go_to_point_stops_at_target():
    goal = GoToPoint(target=(5.0, 5.0))
    assert goal.command(Pose(5.0, 5.0, 0.0), 0.05) == (0.0, 0.0)


def test_limiter_ramps_up_slowly():
    limiter = AccelerationLimiter(max_linear=0.5)
    linear, _ = limiter.apply(2.0, 0.0, 1.0)
    assert linear == 0.5


def test_emergency_stop_latches():
    estop = EmergencyStop(stop_distance=1.5)
    assert estop.check({"front": 1.0, "left": 9.0, "right": 9.0})
    assert estop.check({"front": 9.0, "left": 9.0, "right": 9.0})
    estop.release()
    assert not estop.check({"front": 9.0, "left": 9.0, "right": 9.0})


def test_navigator_reaches_goal_around_obstacles():
    config = RobotConfig()
    sim = config.make_simulator([Obstacle(15.0, 1.0, 2.0), Obstacle(28.0, -2.0, 2.0)])
    navigator = config.make_navigator((45.0, 0.0))
    state = "driving"
    while sim.time < 300:
        linear, angular, state = navigator.update(sim.pose, sim.read_sensors(), 0.05)
        if state in ("arrived", "emergency stop"):
            break
        sim.step(linear, angular, 0.05)
    assert state == "arrived"


def test_navigator_stops_when_blocked_up_close():
    navigator = Navigator((10.0, 0.0))
    ranges = {"left": 9.0, "front": 0.5, "right": 9.0}
    assert navigator.update(Pose(), ranges, 0.05) == (0.0, 0.0, "emergency stop")


def test_config_loads_from_file(tmp_path):
    path = tmp_path / "robot.json"
    path.write_text(json.dumps({"wheel_base": 3.5}))
    assert RobotConfig.load(path).wheel_base == 3.5


def test_config_rejects_unknown_setting(tmp_path):
    path = tmp_path / "robot.json"
    path.write_text(json.dumps({"wheelbase": 3.5}))
    with pytest.raises(ValueError):
        RobotConfig.load(path)


def test_serial_driver_scales_and_formats():
    link = FakeLink()
    driver = SerialDriver("fake", max_speed=2.0, link=link)
    driver.send(1.0, -2.0)
    driver.close()
    assert link.sent == [b"M 0.500 -1.000\n", b"S\n"]
    assert link.closed


def test_serial_driver_clamps_speed():
    link = FakeLink()
    driver = SerialDriver("fake", max_speed=2.0, link=link)
    driver.send(9.0, -9.0)
    assert link.sent == [b"M 1.000 -1.000\n"]


def test_cli_parses_drive_command():
    args = build_parser().parse_args(["drive", "--left", "0.5", "--right", "0.5"])
    assert args.command == "drive"
    assert args.seconds == 3.0
