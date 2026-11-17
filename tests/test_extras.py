import csv
import math

from robotkit import CsvLogger, Odometry, Pose, Route
from robotkit.cli import main


def test_odometry_straight_line():
    odometry = Odometry(wheel_base=2.0)
    pose = odometry.update(3.0, 3.0)
    assert math.isclose(pose.x, 3.0)
    assert math.isclose(pose.y, 0.0, abs_tol=1e-9)


def test_odometry_turns_in_place():
    odometry = Odometry(wheel_base=2.0)
    pose = odometry.update(-1.0, 1.0)
    assert math.isclose(pose.heading, 1.0)
    assert math.isclose(pose.x, 0.0, abs_tol=1e-9)


def test_route_moves_to_next_point():
    route = Route([(0.0, 0.0), (10.0, 0.0)])
    assert route.next_target(Pose(0.0, 0.0, 0.0)) == (10.0, 0.0)


def test_route_finishes():
    route = Route([(1.0, 1.0)])
    assert route.next_target(Pose(1.0, 1.0, 0.0)) is None
    assert route.finished


def test_logger_writes_rows(tmp_path):
    path = tmp_path / "run.csv"
    with CsvLogger(path, ["time", "x"]) as logger:
        logger.log(time=0.1, x=2.5)
    with open(path) as file:
        rows = list(csv.reader(file))
    assert rows == [["time", "x"], ["0.1", "2.5"]]


def test_sim_command_follows_waypoints(tmp_path, capsys):
    log = tmp_path / "run.csv"
    try:
        main(["sim", "--waypoint", "10", "0", "--waypoint", "10", "10", "--log", str(log)])
    except SystemExit as stop:
        assert stop.code == 0
    assert "result: arrived" in capsys.readouterr().out
    assert log.exists()
