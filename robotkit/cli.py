import argparse
import sys
import time

from . import __version__
from .config import load_config
from .drive import Pose
from .hardware import PrintDriver, SerialDriver, list_ports
from .logger import CsvLogger
from .route import Route
from .sensors import Obstacle

PERIOD = 0.05


def build_parser():
    parser = argparse.ArgumentParser(
        prog="robotkit",
        description="Toolkit for building and simulating large robots.",
    )
    parser.add_argument("--version", action="version", version=f"robotkit {__version__}")
    commands = parser.add_subparsers(dest="command")

    gui = commands.add_parser("gui", help="open the visual simulator")
    gui.add_argument("--config", help="path to a robot config file")

    sim = commands.add_parser("sim", help="run the simulator without a window")
    sim.add_argument("--config", help="path to a robot config file")
    sim.add_argument("--goal", nargs=2, type=float, default=[45.0, 0.0], metavar=("X", "Y"))
    sim.add_argument(
        "--obstacle",
        nargs=3,
        type=float,
        action="append",
        default=[],
        metavar=("X", "Y", "RADIUS"),
    )
    sim.add_argument(
        "--waypoint",
        nargs=2,
        type=float,
        action="append",
        default=[],
        metavar=("X", "Y"),
        help="drive through these points in order, replaces --goal",
    )
    sim.add_argument("--log", help="write the run to a CSV file")
    sim.add_argument("--max-time", type=float, default=600.0)

    commands.add_parser("ports", help="list serial ports")

    drive = commands.add_parser("drive", help="send wheel speeds to a motor controller")
    drive.add_argument("--config", help="path to a robot config file")
    drive.add_argument("--port", help="serial port, leave out for a dry run")
    drive.add_argument("--baud", type=int, default=115200)
    drive.add_argument("--left", type=float, required=True, help="left wheel speed in m/s")
    drive.add_argument("--right", type=float, required=True, help="right wheel speed in m/s")
    drive.add_argument("--seconds", type=float, default=3.0)
    return parser


def run_gui(args):
    try:
        from .gui import run
    except ImportError:
        print("tkinter is not available in this Python install")
        return 1
    run(args.config)
    return 0


def run_sim(args):
    config = load_config(args.config)
    obstacles = [Obstacle(x, y, radius) for x, y, radius in args.obstacle]
    sim = config.make_simulator(obstacles, Pose())
    route = Route(args.waypoint or [args.goal])
    navigator = config.make_navigator(route.points[0])
    logger = CsvLogger(args.log, ["time", "x", "y", "state"]) if args.log else None
    state = "driving"
    try:
        while sim.time < args.max_time:
            target = route.next_target(sim.pose)
            if target is None:
                state = "arrived"
                break
            if target != navigator.goal.target:
                navigator.set_target(target)
            linear, angular, state = navigator.update(sim.pose, sim.read_sensors(), PERIOD)
            if logger:
                logger.log(time=round(sim.time, 2), x=round(sim.pose.x, 3), y=round(sim.pose.y, 3), state=state)
            if state == "emergency stop":
                break
            sim.step(linear, angular, PERIOD)
    finally:
        if logger:
            logger.close()
    print(f"result: {state}")
    print(f"time: {sim.time:.1f} s")
    print(f"position: ({sim.pose.x:.2f}, {sim.pose.y:.2f})")
    return 0 if state == "arrived" else 1


def run_ports(args):
    ports = list_ports()
    if not ports:
        print("no serial ports found")
        return 1
    for device, description in ports:
        print(f"{device}  {description}")
    return 0


def run_drive(args):
    config = load_config(args.config)
    if max(abs(args.left), abs(args.right)) > config.max_wheel_speed:
        print(f"wheel speeds must be within {config.max_wheel_speed} m/s")
        return 2

    drive = config.make_drive()
    limiter = config.make_limiter()
    if args.port:
        driver = SerialDriver(args.port, args.baud, config.max_wheel_speed)
    else:
        driver = PrintDriver()

    def push(linear, angular):
        linear, angular = limiter.apply(linear, angular, PERIOD)
        driver.send(*drive.wheel_speeds(linear, angular))

    target_linear = (args.left + args.right) / 2
    target_angular = (args.right - args.left) / config.wheel_base
    try:
        end = time.monotonic() + args.seconds
        while time.monotonic() < end:
            push(target_linear, target_angular)
            time.sleep(PERIOD)
        while abs(limiter.linear) > 0.01 or abs(limiter.angular) > 0.01:
            push(0.0, 0.0)
            time.sleep(PERIOD)
    except KeyboardInterrupt:
        pass
    finally:
        driver.close()
    return 0


HANDLERS = {
    "gui": run_gui,
    "sim": run_sim,
    "ports": run_ports,
    "drive": run_drive,
}


def main(argv=None):
    args = build_parser().parse_args(argv)
    command = args.command or "gui"
    if command == "gui" and not hasattr(args, "config"):
        args.config = None
    try:
        code = HANDLERS[command](args)
    except (RuntimeError, ValueError, OSError) as error:
        print(f"error: {error}")
        code = 1
    sys.exit(code)
