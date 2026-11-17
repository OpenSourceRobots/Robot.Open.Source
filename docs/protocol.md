# Serial protocol

robotkit talks to a motor controller over a serial port at 115200 baud. Every message is one line of ASCII ending in a newline.

| Message | Meaning |
| --- | --- |
| `M <left> <right>` | Set wheel speeds. Each value is from -1.0 (full reverse) to 1.0 (full forward). |
| `S` | Stop both motors right away. |

Example: `M 0.250 0.250` drives straight at a quarter of full speed.

## Watchdog

The controller must stop the motors if it does not hear a valid message for 500 ms. robotkit sends a command every 50 ms while driving, so a crashed program, a pulled cable or a frozen laptop always ends with the robot stopped.

## Speed scaling

The Python side converts wheel speeds from m/s to the -1.0 to 1.0 range using `max_wheel_speed` from the robot config. The controller only has to map -1.0 to 1.0 onto its motor output.

## Writing your own controller

Any board that can read lines from a serial port and follows the watchdog rule will work. A reference Arduino sketch is in `firmware/motor_controller/motor_controller.ino`.
