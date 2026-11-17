# robotkit

> **Work in progress.** This project used to live on a different website and is being migrated to GitHub. Some docs, issues and features have not made the move yet.

Open source toolkit for building, simulating and driving large, heavy-duty robots. Runs on Windows, macOS and Linux.

## What it does

- **Visual simulator** with a window: click to set a goal, right-click to drop obstacles
- **Navigation** with go-to-point, obstacle avoidance and a latching emergency stop
- **Heavy robot safety** with acceleration limits so a big machine never jerks
- **Real hardware** over a serial port with a reference Arduino sketch and a 500 ms watchdog
- **Config files** so one tool fits any robot size
- **Downloadable apps** for Windows (`.exe`), macOS and Linux

## Download

Grab the latest build for your system from the [Releases](../../releases) page:

| System | Files |
| --- | --- |
| Windows | `robotkit-gui-windows.exe`, `robotkit-windows.exe` |
| macOS | `robotkit-gui-macos`, `robotkit-macos` |
| Linux | `robotkit-gui-linux`, `robotkit-linux` |

Double-click the `gui` file to open the simulator. The other file is the command line tool.

On macOS and Linux you may need to run `chmod +x robotkit-gui-macos` first. On macOS, if Gatekeeper blocks it, right-click the file and choose Open.

## Run from source

You need Python 3.9 or newer.

```bash
git clone https://github.com/OpenSourceRobots/Robot.Open.Source.git
cd Robot.Open.Source
python3 -m pip install -e ".[serial]"
python3 -m robotkit
```

On Windows use `py` in place of `python3`.

## Commands

```bash
robotkit gui
robotkit sim --goal 45 0 --obstacle 15 1 2 --obstacle 28 -2 2
robotkit ports
robotkit drive --port COM3 --left 0.5 --right 0.5 --seconds 3
```

`robotkit drive` without `--port` is a dry run that only prints what it would send.

## Robot settings

Copy `configs/default.json`, change the numbers to match your robot and pass it with `--config`.

| Setting | Meaning |
| --- | --- |
| `wheel_base` | Distance between the left and right wheels in meters |
| `max_wheel_speed` | Fastest wheel speed in m/s |
| `max_acceleration` | Forward speed change allowed per second |
| `max_angular_acceleration` | Turn rate change allowed per second |
| `stop_distance` | Emergency stop triggers when something is this close |
| `safe_distance` | Obstacle avoidance starts at this distance |
| `sensor_range` | How far the range sensors reach |

## Connecting a real robot

1. Flash `firmware/motor_controller/motor_controller.ino` to a board, or write your own using [the protocol](docs/protocol.md).
2. Find the port with `robotkit ports`.
3. Test with the wheels off the ground: `robotkit drive --port <port> --left 0.2 --right 0.2 --seconds 2`.

## Safety

This is early software. A robot big enough to hurt someone needs a **hardware** emergency stop that cuts motor power without any software involved, proper motor controllers and contactors, and a clear area when testing. The Arduino sketch is a reference for the protocol, not something to run heavy motors from directly.

## Build the apps yourself

```bash
python3 -m pip install . pyserial pyinstaller
python3 scripts/build.py
```

PyInstaller only builds for the system it runs on, so the `.exe` has to be built on Windows. The release workflow does all three systems for you: push a tag like `v0.2.0` and GitHub builds and publishes every file.

## Test

```bash
python3 -m pip install pytest
python3 -m pytest
```

## Roadmap

- [x] Core control and safety code
- [x] Simulator with window
- [x] Serial motor driver and firmware
- [x] Windows, macOS and Linux apps
- [ ] CAN bus support
- [ ] Encoder and GPS input
- [ ] Docs migrated from the old site
- [ ] Old issues and discussions migrated

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
